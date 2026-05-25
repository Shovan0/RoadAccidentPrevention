import os
import cv2
import math
from collections import defaultdict
from ultralytics import YOLO


# ================= YOLO MODEL =================
def load_yolo_model():
    try:
        import torch
        return YOLO("yolov8n.pt")
    except Exception as e:
        print(f"YOLO load fallback: {e}")
        import torch
        original_load = torch.load

        def patched_load(*args, **kwargs):
            kwargs["weights_only"] = False
            return original_load(*args, **kwargs)

        torch.load = patched_load
        model = YOLO("yolov8n.pt")
        torch.load = original_load
        return model


model = load_yolo_model()


# ================= SPEED TRACKER =================
class SpeedTracker:
    def __init__(self, fps, scale_factor=0.05):
        self.fps = fps
        self.scale_factor = scale_factor

        self.prev_pos = {}
        self.prev_time = {}
        self.speed_history = defaultdict(list)

    def update(self, obj_id, x, y, frame_idx):
        current_time = frame_idx / self.fps
        speed_kmh = 0

        if obj_id in self.prev_pos:
            prev_x, prev_y = self.prev_pos[obj_id]

            dx = x - prev_x
            dy = y - prev_y

            pixel_dist = math.sqrt(dx * dx + dy * dy)
            time_diff = current_time - self.prev_time[obj_id]

            if time_diff > 0:
                speed_mps = (pixel_dist * self.scale_factor) / time_diff
                speed_kmh = speed_mps * 3.6

        # Save state
        self.prev_pos[obj_id] = (x, y)
        self.prev_time[obj_id] = current_time

        # Smooth speed
        self.speed_history[obj_id].append(speed_kmh)
        if len(self.speed_history[obj_id]) > 5:
            self.speed_history[obj_id].pop(0)

        avg_speed = sum(self.speed_history[obj_id]) / len(self.speed_history[obj_id])

        return avg_speed


# ================= FRAME GENERATOR =================
def generate_frames(video_path, overspeed_limit_kmh=60, distance_meters=20, record_config=None):
    if not video_path or not os.path.isfile(video_path):
        print(f"Video not found: {video_path}")
        return

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    W, H = 1280, 720

    tracker = SpeedTracker(fps)
    # Trap line positions (match simulation ratios)
    START_LINE_Y = int(H * 0.74)
    END_LINE_Y = int(H * 0.26)

    # Per-object crossing state
    obj_state = {}

    out = None
    all_logs = []
    overspeed_summary = []

    if record_config and record_config.get("output_path"):
        os.makedirs(os.path.dirname(record_config["output_path"]), exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(record_config["output_path"], fourcc, fps, (W, H))

    target_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
    frame_idx = 0
    # If requested, first preprocess entire video to output_path, then stream it.
    preprocess_first = bool(record_config and record_config.get("preprocess_first"))

    def process_loop(do_write=True):
        nonlocal all_logs, overspeed_summary
        local_frame_idx = 0
        cap_local = cv2.VideoCapture(video_path)
        while True:
            ret, frame = cap_local.read()
            if not ret:
                break

            local_frame_idx += 1
            frame = cv2.resize(frame, (W, H))
            annotated = frame.copy()

            results = model.track(
                frame,
                persist=True,
                verbose=False,
                tracker="bytetrack.yaml",
                conf=0.3,
                iou=0.5,
                classes=target_classes,
            )

            if results and results[0].boxes.id is not None:
                ids = results[0].boxes.id.int().cpu().tolist()
                boxes = results[0].boxes.xyxy.cpu().tolist()
                cls_ids = results[0].boxes.cls.int().cpu().tolist()

                for box, cls_id, obj_id in zip(boxes, cls_ids, ids):
                    label = results[0].names[int(cls_id)]
                    x1, y1, x2, y2 = map(int, box)

                    # Bottom-center point
                    bx, by = (x1 + x2) // 2, y2

                    # Initialize object state
                    st = obj_state.setdefault(obj_id, {
                        "start_frame": None,
                        "start_y": None,
                        "end_frame": None,
                        "end_y": None,
                        "plate_captured": False,
                    })

                    # Check for crossing start/stop trap lines (moving upward)
                    if st["start_frame"] is None and by <= START_LINE_Y:
                        st["start_frame"] = local_frame_idx
                        st["start_y"] = by

                    if st["start_frame"] is not None and st["end_frame"] is None and by <= END_LINE_Y:
                        st["end_frame"] = local_frame_idx
                        st["end_y"] = by

                        # Compute speed using pixel distance between trap lines + known meters
                        frames_taken = st["end_frame"] - st["start_frame"]
                        if frames_taken > 0:
                            pixel_distance = abs((st.get("start_y") or 0) - (st.get("end_y") or 0))
                            pixel_span = abs(START_LINE_Y - END_LINE_Y) or 1
                            meters_per_pixel = distance_meters / pixel_span
                            measured_meters = pixel_distance * meters_per_pixel
                            time_seconds = frames_taken / fps if fps else frames_taken / 30.0
                            speed_kmh = (measured_meters / time_seconds) * 3.6 if time_seconds > 0 else 0
                        else:
                            speed_kmh = 0

                        log_entry = {
                            "id": obj_id,
                            "label": label,
                            "speed": round(speed_kmh, 1),
                            "frame": local_frame_idx,
                            "overspeed": speed_kmh > overspeed_limit_kmh,
                        }

                        if not any(l["id"] == obj_id for l in all_logs):
                            all_logs.append(log_entry)
                            if log_entry["overspeed"]:
                                overspeed_summary.append(log_entry)

                    # Draw bounding box and speed if available
                    # Attempt to show smoothed speed if previously computed
                    display_speed = None
                    # find any existing log speed for this id
                    for l in reversed(all_logs):
                        if l["id"] == obj_id:
                            display_speed = l.get("speed")
                            break

                    color = (0, 0, 255) if (display_speed or 0) > overspeed_limit_kmh else (0, 255, 0)
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                    if display_speed is not None:
                        cv2.putText(
                            annotated,
                            f"{int(display_speed)} km/h",
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            color,
                            2,
                        )

            if do_write and out:
                out.write(annotated)

            # Live stats callback
            if record_config and record_config.get("live_callback"):
                count = len(all_logs)
                avg = sum(l["speed"] for l in all_logs) / count if count else 0
                mx = max((l["speed"] for l in all_logs), default=0)

                record_config["live_callback"]({
                    "total_vehicles": count,
                    "total_violations": len(overspeed_summary),
                    "avg_speed": round(avg, 1),
                    "max_speed": round(mx, 1),
                    "all_logs": all_logs,
                    "overspeed_summary": overspeed_summary,
                })

            # If streaming while processing, yield encoded frame
            flag, enc = cv2.imencode(".jpg", annotated)
            if not flag:
                continue

            yield_frame = b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + bytearray(enc) + b"\r\n"
            yield yield_frame

        cap_local.release()

    if preprocess_first and out:
        # 1) Process and write all frames to output_path without yielding
        print("[PROCESS] Preprocessing entire video before streaming...")
        for _ in process_loop(do_write=True):
            # process_loop yields frames; discard them during preprocessing
            pass

        # Call data callback after preprocessing
        if record_config and record_config.get("data_callback"):
            record_config["data_callback"]({
                "all_logs": all_logs,
                "overspeed_summary": overspeed_summary,
            })

        # 2) Stream the written output file
        stream_cap = cv2.VideoCapture(record_config["output_path"])
        while True:
            ret2, f2 = stream_cap.read()
            if not ret2:
                break
            f2 = cv2.resize(f2, (W, H))
            ok2, enc2 = cv2.imencode('.jpg', f2)
            if not ok2:
                continue
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + bytearray(enc2) + b"\r\n"
        stream_cap.release()
        return

    # Default: process and stream frames live
    try:
        for frame_bytes in process_loop(do_write=bool(out)):
            yield frame_bytes
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap.release()
        if out:
            out.release()

        if record_config and record_config.get("data_callback"):
            record_config["data_callback"]({
                "all_logs": all_logs,
                "overspeed_summary": overspeed_summary,
            })