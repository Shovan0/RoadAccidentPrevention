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

    vehicles = []
    vehicle_counter = 0
    all_logs = []
    overspeed_logs = []
    frame_idx = 0

    # ─────────────────────────────────────────────
    # LOAD DB PLATES
    # ─────────────────────────────────────────────
    db_plates = []

    if _DB_AVAILABLE:
        try:
            db_plates = get_all_car_numbers()
            print(f"[DB] Loaded {len(db_plates)} plates")
        except Exception as e:
            print(f"[DB ERROR] {e}")

    _plate_pool = list(db_plates)

    # ─────────────────────────────────────────────
    # STATIC ROAD
    # ─────────────────────────────────────────────
    _road_template = np.zeros((H, W, 3), dtype=np.uint8)
    draw_road(_road_template, distance_meters)

    try:

        while True:

            frame_idx += 1

            frame = _road_template.copy()

            # ─────────────────────────────────────────────
            # SPAWN VEHICLES
            # ─────────────────────────────────────────────
            if random.random() < 0.04:

                lane_choice = random.randint(0, len(LANES_X) - 1)

                lane_vehicles = [
                    v for v in vehicles
                    if v.lane == lane_choice
                ]

                # allow spawn only if enough gap exists
                can_spawn = True

                for lv in lane_vehicles:
                    if lv.y > H - 250:
                        can_spawn = False
                        break

                if can_spawn:

                    vehicle_counter += 1

                    assigned_plate = None

                    if _plate_pool:
                        assigned_plate = _plate_pool[
                            (vehicle_counter - 1) % len(_plate_pool)
                        ]

                    vehicle = VirtualVehicle(
                        vehicle_counter,
                        lane_choice,
                        LANES_X[lane_choice],
                        overspeed_limit_kmh,
                        plate=assigned_plate,
                    )

                    # SPAWN BELOW FRAME
                    vehicle.y = H + random.randint(40, 180)

                    # RANDOM REALISTIC SPEED
                    speed_kmh = random.randint(25, 90)

                    # convert km/h → pixels/frame
                    vehicle.current_speed = speed_kmh / 12

                    # store actual speed
                    vehicle.real_speed_kmh = speed_kmh

                    vehicles.append(vehicle)

            # ─────────────────────────────────────────────
            # UPDATE VEHICLES
            # ─────────────────────────────────────────────
            for v in vehicles:

                # MOVE VEHICLE
                v.update()

                v_bottom = v.y + v.h

                # START LINE
                if (
                    v.start_frame is None
                    and v_bottom <= START_LINE_Y
                ):
                    v.start_frame = frame_idx
                    v.start_y = v_bottom

                # END LINE
                if (
                    v.start_frame is not None
                    and v.end_frame is None
                    and v_bottom <= END_LINE_Y
                ):

                    v.end_frame = frame_idx
                    v.end_y = v_bottom

                    frames_taken = (
                        v.end_frame - v.start_frame
                    )

                    if frames_taken > 0:
                        # Calculate speed from pixel distance traveled
                        pixel_distance = abs((v.start_y or 0) - (v.end_y or 0))
                        pixel_span = abs(START_LINE_Y - END_LINE_Y) or 1
                        meters_per_pixel = distance_meters / pixel_span
                        measured_meters = pixel_distance * meters_per_pixel
                        time_seconds = frames_taken / SIM_FPS
                        
                        v.detected_speed = round(
                            (measured_meters / time_seconds) * 3.6,
                            1
                        )

                        v.is_overspeed = (
                            v.detected_speed > overspeed_limit_kmh
                        )

                        if (
                            v.is_overspeed
                            and not v.plate_captured
                        ):

                            v.scan_start_frame = frame_idx
                            v.plate_captured = True

                            print(
                                f"[VIOLATION] "
                                f"{v.plate} "
                                f"{v.detected_speed} km/h"
                            )

                        log_entry = {
                            "id": v.id,
                            "plate": v.plate,
                            "label": v.type,
                            "speed": v.detected_speed,
                            "frame": frame_idx,
                            "overspeed": v.is_overspeed,
                        }

                        if v.is_overspeed:

                            details = _safe_get_vehicle_details(v.plate)

                            log_entry["driver_name"] = (
                                details.get("driver_name") or "N/A"
                            )

                            log_entry["driver_contact"] = (
                                details.get("driver_contact") or "N/A"
                            )

                            try:

                                body = (
                                    f"ALERT: Vehicle {v.plate} "
                                    f"detected at "
                                    f"{v.detected_speed} km/h"
                                )

                                phone = details.get(
                                    "driver_contact"
                                )

                                if phone and _send_twilio:

                                    _send_twilio(phone, body)

                            except Exception as e:
                                print(e)

                            overspeed_logs.append(log_entry)

                        all_logs.append(log_entry)

                # DRAW VEHICLE
                v.draw(frame, frame_idx)

            # ─────────────────────────────────────────────
            # REMOVE OFFSCREEN VEHICLES
            # ─────────────────────────────────────────────
            vehicles = [
                v for v in vehicles
                if v.y > -300
            ]

            # ─────────────────────────────────────────────
            # VIOLATION PANEL
            # ─────────────────────────────────────────────
            recent = overspeed_logs[-5:]

            if recent:

                panel_x = W - 280

                panel_h = 24 + 52 * len(recent)

                cv2.rectangle(
                    frame,
                    (panel_x - 6, 44),
                    (W - 4, 44 + panel_h),
                    (0, 0, 0),
                    -1,
                )

                cv2.rectangle(
                    frame,
                    (panel_x - 6, 44),
                    (W - 4, 44 + panel_h),
                    (0, 30, 200),
                    2,
                )

                cv2.putText(
                    frame,
                    "VIOLATIONS",
                    (panel_x, 63),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (80, 80, 255),
                    2,
                )

                for i, viol in enumerate(reversed(recent)):

                    by = 72 + i * 50

                    cv2.rectangle(
                        frame,
                        (panel_x - 2, by),
                        (W - 8, by + 46),
                        (22, 0, 0),
                        -1,
                    )

                    cv2.putText(
                        frame,
                        f"{viol['plate']}",
                        (panel_x, by + 16),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.45,
                        (255, 255, 255),
                        1,
                    )

                    cv2.putText(
                        frame,
                        f"{viol['speed']} km/h",
                        (panel_x, by + 36),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.45,
                        (0, 255, 255),
                        1,
                    )

            # ─────────────────────────────────────────────
            # TOP BAR
            # ─────────────────────────────────────────────
            cv2.rectangle(
                frame,
                (0, 0),
                (W, 40),
                (0, 0, 0),
                -1,
            )

            cv2.putText(
                frame,
                (
                    f"LIVE SIMULATION | "
                    f"Detected: {len(all_logs)} | "
                    f"Violations: {len(overspeed_logs)} | "
                    f"Limit: {overspeed_limit_kmh} km/h"
                ),
                (12, 27),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

            # ─────────────────────────────────────────────
            # CALLBACK
            # ─────────────────────────────────────────────
            if (
                record_config
                and record_config.get("live_callback")
            ):

                count = len(all_logs)

                avg = (
                    sum(lg["speed"] for lg in all_logs) / count
                    if count else 0
                )

                mx = max(
                    (lg["speed"] for lg in all_logs),
                    default=0
                )

                record_config["live_callback"]({
                    "total_vehicles": count,
                    "total_violations": len(overspeed_logs),
                    "avg_speed": round(avg, 1),
                    "max_speed": round(mx, 1),
                    "all_logs": all_logs,
                    "overspeed_summary": overspeed_logs,
                })

            # ─────────────────────────────────────────────
            # ENCODE FRAME
            # ─────────────────────────────────────────────
            ok, enc = cv2.imencode(
                ".jpg",
                frame,
                [cv2.IMWRITE_JPEG_QUALITY, 82]
            )

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

    TARGET_PHONE = os.getenv('TARGET_PHONE', '9007074039')
    _plate_pool = list(db_plates)
    user_plate = None
    try:
        matching = [p for p in _plate_pool if _safe_get_vehicle_details(p).get('driver_contact') == TARGET_PHONE]
        if matching:
            user_plate = matching[0]
            while len(_plate_pool) < 5:
                _plate_pool.extend(list(db_plates))
            if user_plate in _plate_pool:
                _plate_pool.remove(user_plate)
                _plate_pool.insert(4, user_plate)
                print(f"[DB] Placed user plate {user_plate} at position for 5th vehicle")
    except Exception as _e:
        print(f"[DB] Could not arrange plate pool for target phone: {_e}")

    # Pre-draw the static road template once
    _road_template = np.zeros((H, W, 3), dtype=np.uint8)
    draw_road(_road_template, distance_meters)

    # Ensure at least one vehicle is present at simulation start so it's visible
    if not vehicles:
        vehicle_counter += 1
        if _plate_pool:
            assigned_plate = _plate_pool[(vehicle_counter - 1) % len(_plate_pool)]
        else:
            assigned_plate = None
        # spawn one vehicle in the middle lane to be visible immediately
        mid_lane = min(len(LANES_X) - 1, max(0, len(LANES_X) // 2))
        vehicles.append(
            VirtualVehicle(
                vehicle_counter, mid_lane,
                LANES_X[mid_lane], overspeed_limit_kmh,
                plate=assigned_plate,
            )
        )
        # place this initial vehicle just inside the frame so it's visible immediately
        try:
            vehicles[-1].y = float(H - 60)
        except Exception:
            pass

    # ── Speed pattern defined ONCE, outside all loops ────────────────
    speed_pattern = [30, 40, 20]  # km/h

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
                    should_overspeed = (vehicle_counter % 5 == 0)
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

            # ── 3. UPDATE & DRAW ALL VEHICLES ─────────────────────────────────
            for v in vehicles:

                # ── Controlled speed (cycles every 1 second) ──────────────────
                pattern_index = (frame_idx // SIM_FPS) % len(speed_pattern)
                controlled_speed = speed_pattern[pattern_index]

                # Convert km/h → pixels/frame  (tune the 0.6 scalar if needed)
                pixel_speed = controlled_speed / 3.6 * 0.6
                v.current_speed = pixel_speed

                # Move vehicle
                v.update()

                # ── SPEED DETECTION BETWEEN TRAP LINES ───────────────────────
                v_bottom = v.y + v.h

                if v.start_frame is None and v_bottom <= START_LINE_Y:
                    v.start_frame = frame_idx
                    v.start_bottom = v_bottom

                if v.start_frame is not None and v.end_frame is None and v_bottom <= END_LINE_Y:
                    v.end_frame = frame_idx
                    v.end_bottom = v_bottom
                    frames_taken = abs(v.end_frame - v.start_frame)
                    if frames_taken > 0:
                        time_sec = frames_taken / SIM_FPS

                        # Compute distance travelled in pixels between the two trap lines
                        pixel_distance = abs((v.start_bottom or 0) - (v.end_bottom or 0))
                        # Convert pixels -> meters using the known distance between trap lines
                        pixel_span = abs(START_LINE_Y - END_LINE_Y) or 1
                        meters_per_pixel = distance_meters / pixel_span
                        measured_m = pixel_distance * meters_per_pixel

                        v.detected_speed = round((measured_m / time_sec) * 3.6, 1)
                        v.is_overspeed = v.detected_speed > overspeed_limit_kmh

                        # Force user plate to exactly 50 km/h; clamp others below 50
                        try:
                            if user_plate and v.plate == user_plate:
                                v.detected_speed = 50.0
                                v.is_overspeed = v.detected_speed > overspeed_limit_kmh
                            else:
                                if v.detected_speed >= 50.0:
                                    v.detected_speed = 49.9
                                    v.is_overspeed = v.detected_speed > overspeed_limit_kmh
                        except Exception:
                            pass

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

                            # Send real-time Twilio SMS to the driver
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
                            except Exception as _nerr:
                                print(f"[NOTIFY] notification send failed: {_nerr}")

                        all_logs.append(log_entry)
                        if v.is_overspeed:
                            overspeed_logs.append(log_entry)

                # ── Draw this vehicle onto the frame ──────────────────────────
                v.draw(frame, frame_idx)

            # Remove vehicles that have left the frame
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