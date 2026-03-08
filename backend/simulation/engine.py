import os
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

    # Optional: pre-draw the static road into a template so we can copy it
    # each frame instead of re-drawing from scratch (minor optimisation).
    _road_template = np.zeros((H, W, 3), dtype=np.uint8)
    draw_road(_road_template, distance_meters)

    try:
        while True:
            frame_idx += 1

            # ── 1. STATIC ROAD ────────────────────────────────────────────────
            frame = _road_template.copy()

            # ── 2. SPAWN VEHICLES ─────────────────────────────────────────────
            if random.random() < 0.08:
                lane_choice = random.randint(0, len(LANES_X) - 1)
                is_clear = all(
                    not (v.lane == lane_choice and v.y > H - 150)
                    for v in vehicles
                )
                if is_clear:
                    vehicle_counter += 1
                    vehicles.append(
                        VirtualVehicle(
                            vehicle_counter, lane_choice,
                            LANES_X[lane_choice], overspeed_limit_kmh,
                        )
                    )

            # ── 3. UPDATE VEHICLES + OVERTAKE LOGIC ──────────────────────────
            for v in vehicles:
                # Find the closest vehicle ahead in the same lane
                ahead, min_dist = None, 1000
                for other in vehicles:
                    if other.id != v.id and other.lane == v.lane and other.y < v.y:
                        d = v.y - (other.y + other.h)
                        if d < min_dist:
                            min_dist, ahead = d, other

                if ahead and min_dist < 80:
                    # Try to overtake into an adjacent lane
                    changed = False
                    for delta in [-1, 1]:
                        nl = v.lane + delta
                        if 0 <= nl < len(LANES_X):
                            safe = all(
                                abs(o.y - v.y) >= 180
                                for o in vehicles
                                if o.lane == nl and o.id != v.id
                            )
                            if safe:
                                v.change_lane(nl, LANES_X[nl])
                                changed = True
                                break
                    if not changed:
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
