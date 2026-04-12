import os
import sys
import time
import random
import cv2
import numpy as np

from .vehicle import VirtualVehicle
from .road import draw_road
from .constants import (
    W, H, LANES_X, ROAD_LEFT, ROAD_RIGHT,
    START_LINE_Y, END_LINE_Y, SIM_FPS,
)

# Resolve the backend root so database.py is importable regardless of cwd
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

try:
    from database import get_all_car_numbers, get_vehicle_details as _db_get_details
    _DB_AVAILABLE = True
except Exception as _db_import_err:
    print(f"[DB] Could not import database module: {_db_import_err}")
    _DB_AVAILABLE = False

# Optional: update helper to change driver contact when violation occurs
try:
    from db_utils import update_driver_contact_by_plate as _update_contact
except Exception:
    _update_contact = None
# Notifier helpers (Twilio SMS only)
try:
    from notify import send_sms as _send_sms, send_twilio_sms as _send_twilio
except Exception:
    _send_sms = None
    _send_twilio = None


def _safe_get_vehicle_details(plate):
    """Fetch vehicle/owner/driver details; returns empty dict on any error."""
    if not _DB_AVAILABLE:
        return {}
    try:
        result = _db_get_details(plate)
        return result if result else {}
    except Exception as e:
        print(f"[DB] detail fetch failed for {plate}: {e}")
        return {}


def generate_virtual_simulation(
    overspeed_limit_kmh: float = 60,
    distance_meters: float = 20.0,
    record_config=None,
):
    """
    Generator — yields MJPEG boundary frames for a synthetic top-down simulation.

    The road scene is fully STATIC (like a real fixed CCTV camera); only
    vehicles move through the frame.
    """
    vehicles: list[VirtualVehicle] = []
    vehicle_counter = 0
    all_logs: list[dict] = []
    overspeed_logs: list[dict] = []
    frame_idx = 0

    # ── Load registered car plates from DB ───────────────────────────
    db_plates: list[str] = []
    if _DB_AVAILABLE:
        try:
            db_plates = get_all_car_numbers()
            print(f"[DB] Loaded {len(db_plates)} registered plates from database.")
        except Exception as _e:
            print(f"[DB] Could not load plates: {_e}")
    if not db_plates:
        print("[DB] No plates in DB — vehicles will use randomly generated plates.")

    # If you updated a driver's contact in the DB to your phone number,
    # place that car so it will be assigned to the 5th spawned vehicle.
    TARGET_PHONE = os.getenv('TARGET_PHONE', '9007074039')
    _plate_pool = list(db_plates)  # mutable copy for cycling
    user_plate = None
    try:
        # find plates matching the target phone
        matching = [p for p in _plate_pool if _safe_get_vehicle_details(p).get('driver_contact') == TARGET_PHONE]
        if matching:
            user_plate = matching[0]
            # ensure pool length >= 5 by repeating entries if needed
            while len(_plate_pool) < 5:
                _plate_pool.extend(list(db_plates))
            # move user_plate to index 4 (so vehicle_counter==5 uses it)
            if user_plate in _plate_pool:
                _plate_pool.remove(user_plate)
                _plate_pool.insert(4, user_plate)
                print(f"[DB] Placed user plate {user_plate} at position for 5th vehicle")
    except Exception as _e:
        print(f"[DB] Could not arrange plate pool for target phone: {_e}")

    # Optional: pre-draw the static road into a template so we can copy it
    # each frame instead of re-drawing from scratch (minor optimisation).
    _road_template = np.zeros((H, W, 3), dtype=np.uint8)
    draw_road(_road_template, distance_meters)

    try:
        while True:
            frame_idx += 1

            # ── 1. STATIC ROAD ────────────────────────────────────────────────
            frame = _road_template.copy()

            # ── 2. SPAWN VEHICLES  (max 1 per lane, slow rate) ───────────────
            if random.random() < 0.025:
                lane_choice = random.randint(0, len(LANES_X) - 1)
                # Strict: lane must be completely empty
                is_clear = all(v.lane != lane_choice for v in vehicles)
                if is_clear:
                    vehicle_counter += 1
                    # Make every 5th vehicle overspeed
                    should_overspeed = (vehicle_counter % 5 == 0)
                    # Pick next plate from the DB pool; fall back to random
                    if _plate_pool:
                        assigned_plate = _plate_pool[(vehicle_counter - 1) % len(_plate_pool)]
                    else:
                        assigned_plate = None
                    vehicles.append(
                        VirtualVehicle(
                            vehicle_counter, lane_choice,
                            LANES_X[lane_choice], overspeed_limit_kmh,
                            plate=assigned_plate,
                            force_overspeed=should_overspeed,
                        )
                    )

            # ── 3. UPDATE VEHICLES (no overtaking — slow down behind car ahead)
            for v in vehicles:
                # Find the closest vehicle ahead in the same lane
                ahead, min_dist = None, 1000
                for other in vehicles:
                    if other.id != v.id and other.lane == v.lane and other.y < v.y:
                        d = v.y - (other.y + other.h)
                        if d < min_dist:
                            min_dist, ahead = d, other

                if ahead and min_dist < 80:
                    # No overtaking — just slow down to match car ahead
                    v.current_speed = max(ahead.current_speed - 0.5, 0)
                else:
                    if v.current_speed < v.base_speed:
                        v.current_speed += 0.2

                v.update()

                # ── SPEED DETECTION BETWEEN TRAP LINES ──
                v_bottom = v.y + v.h
                if v.start_frame is None and v_bottom <= START_LINE_Y:
                    v.start_frame = frame_idx

                if v.start_frame is not None and v.end_frame is None and v_bottom <= END_LINE_Y:
                    v.end_frame = frame_idx
                    frames_taken = abs(v.end_frame - v.start_frame)
                    if frames_taken > 0:
                        time_sec = frames_taken / SIM_FPS
                        v.detected_speed = round((distance_meters / time_sec) * 3.6, 1)
                        v.is_overspeed = v.detected_speed > overspeed_limit_kmh

                        # Enforce: if this vehicle is the user's plate (placed as 5th),
                        # set its detected speed to exactly 50 km/h. Ensure all other
                        # vehicles remain under 50 km/h.
                        try:
                            if user_plate and v.plate == user_plate:
                                v.detected_speed = 50.0
                                v.is_overspeed = v.detected_speed > overspeed_limit_kmh
                            else:
                                # clamp others to below 50 km/h
                                if v.detected_speed >= 50.0:
                                    v.detected_speed = 49.9
                                    v.is_overspeed = v.detected_speed > overspeed_limit_kmh
                        except Exception:
                            pass

                        # Plate is already known — no OCR needed
                        if v.is_overspeed and not v.plate_captured:
                            v.scan_start_frame = frame_idx
                            v.plate_captured = True
                            print(
                                f"[VIOLATION] ID:{v.id} | {v.type} | {v.plate} | "
                                f"{v.detected_speed} km/h (limit {overspeed_limit_kmh})"
                            )

                        log_entry = {
                            "id":        v.id,
                            "plate":     v.plate,
                            "label":     v.type,
                            "speed":     v.detected_speed,
                            "frame":     frame_idx,
                            "overspeed": v.is_overspeed,
                        }

                        # Enrich violation entry with DB owner/driver details
                        if v.is_overspeed:
                            details = _safe_get_vehicle_details(v.plate)
                            log_entry["driver_name"]    = details.get("driver_name")    or "N/A"
                            log_entry["driver_contact"] = details.get("driver_contact") or "N/A"
                            log_entry["driver_license"] = details.get("license_number") or "N/A"
                            log_entry["owner_name"]     = details.get("owner_name")     or "N/A"
                            log_entry["owner_contact"]  = details.get("owner_contact")  or "N/A"
                            log_entry["vehicle_make"]   = details.get("make")           or "N/A"
                            log_entry["vehicle_model"]  = details.get("model")          or "N/A"
                            log_entry["vehicle_color"]  = details.get("color")          or "N/A"
                            # Send a real-time notification via Twilio to the driver's phone
                            try:
                                body = (
                                    f"ALERT: Vehicle {v.plate} detected at {v.detected_speed} km/h "
                                    f"(limit {overspeed_limit_kmh} km/h)."
                                )
                                driver_phone = details.get('driver_contact')
                                if driver_phone and _send_twilio:
                                    try:
                                        sent = _send_twilio(driver_phone, body)
                                        log_entry['twilio_sms_sent'] = bool(sent)
                                        if sent:
                                            print(f"[NOTIFY] Twilio SMS sent to driver {driver_phone} for plate={v.plate}")
                                    except Exception as _fberr:
                                        print(f"[NOTIFY] Twilio SMS failed: {_fberr}")

                                # Additionally, attempt a voice call to the driver phone stored in DB (if configured)
                                # Voice call support removed — only SMS is sent
                            except Exception as _nerr:
                                print(f"[NOTIFY] notification send failed: {_nerr}")

                        all_logs.append(log_entry)
                        if v.is_overspeed:
                            overspeed_logs.append(log_entry)

                # Draw vehicle on top of static road
                v.draw(frame, frame_idx)

            vehicles = [v for v in vehicles if v.active]

            # ── 4. VIOLATION PANEL (right-side overlay) ───────────────────────
            recent = overspeed_logs[-5:] if overspeed_logs else []
            if recent:
                panel_x = W - 280
                panel_h = 24 + 52 * len(recent)
                cv2.rectangle(frame, (panel_x - 6, 44), (W - 4, 44 + panel_h), (0, 0, 0), -1)
                cv2.rectangle(frame, (panel_x - 6, 44), (W - 4, 44 + panel_h), (0, 30, 200), 2)
                cv2.putText(frame, "VIOLATIONS", (panel_x, 63),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (80, 80, 255), 2)
                for i, viol in enumerate(reversed(recent)):
                    by = 72 + i * 50
                    cv2.rectangle(frame, (panel_x - 2, by), (W - 8, by + 46), (22, 0, 0), -1)
                    cv2.putText(frame, f"Plate: {viol['plate']}",
                                (panel_x, by + 14),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.46, (255, 120, 120), 1)
                    cv2.putText(
                        frame, f"{viol['label'].upper()}  {viol['speed']} km/h",
                        (panel_x, by + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (230, 230, 0), 1,
                    )
                    over_by = round(viol["speed"] - overspeed_limit_kmh, 1)
                    cv2.putText(frame, f"+{over_by} km/h over limit",
                                (panel_x, by + 42),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (100, 255, 100), 1)

            # ── 5. TOP INFO BAR ───────────────────────────────────────────────
            cv2.rectangle(frame, (0, 0), (W, 40), (0, 0, 0), -1)
            cv2.putText(
                frame,
                (f"LIVE SIMULATION  |  Detected: {len(all_logs)}"
                 f"  |  Violations: {len(overspeed_logs)}"
                 f"  |  Limit: {overspeed_limit_kmh} km/h"),
                (12, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2,
            )

            # ── 6. STATS CALLBACK ─────────────────────────────────────────────
            if record_config and record_config.get("live_callback"):
                count = len(all_logs)
                avg = sum(lg["speed"] for lg in all_logs) / count if count else 0
                mx  = max((lg["speed"] for lg in all_logs), default=0)
                record_config["live_callback"]({
                    "total_vehicles":    count,
                    "total_violations":  len(overspeed_logs),
                    "avg_speed":         round(avg, 1),
                    "max_speed":         round(mx, 1),
                    "all_logs":          all_logs,
                    "overspeed_summary": overspeed_logs,
                })

            # ── 7. ENCODE + YIELD FRAME ───────────────────────────────────────
            ok, enc = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 82])
            if not ok:
                continue
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + bytearray(enc)
                + b"\r\n"
            )
            time.sleep(1.0 / SIM_FPS)

    except Exception as exc:
        print(f"[Simulation Error] {exc}")
