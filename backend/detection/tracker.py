import os
import cv2
from ultralytics import YOLO


def load_yolo_model():
    """Load YOLO model with a weights_only fallback patch for older torch versions."""
    try:
        import torch
        model = YOLO("yolov8n.pt")
        return model
    except Exception as e:
        print(f"Standard YOLO load failed, applying patch: {e}")
        import torch
        original_load = torch.load

        def patched_load(*args, **kwargs):
            kwargs["weights_only"] = False
            return original_load(*args, **kwargs)

        torch.load = patched_load
        model = YOLO("yolov8n.pt")
        torch.load = original_load
        return model


# Module-level singleton — loaded once when detection package is imported
model = load_yolo_model()


def generate_frames(video_path, overspeed_limit_kmh=60, distance_meters=20.0, record_config=None):
    """Stream annotated frames from a real video file with speed detection."""
    if not video_path or not os.path.isfile(video_path):
        print(f"Error: Video file not found at {video_path}")
        return

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    W, H = 1280, 720

    out = None
    all_logs = []
    overspeed_summary = []

    if record_config and record_config.get("output_path"):
        os.makedirs(os.path.dirname(record_config["output_path"]), exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(record_config["output_path"], fourcc, fps, (W, H))

    START_LINE_Y = int(H * 0.75)
    END_LINE_Y   = int(H * 0.25)

    cross = {}
    target_classes = [2, 3, 5, 7]   # car, motorcycle, bus, truck
    frame_idx = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_idx += 1
            frame = cv2.resize(frame, (W, H))
            annotated = frame.copy()

            cv2.line(annotated, (0, START_LINE_Y), (W, START_LINE_Y), (0, 0, 255), 2)
            cv2.putText(annotated, "START", (10, START_LINE_Y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.line(annotated, (0, END_LINE_Y), (W, END_LINE_Y), (255, 0, 0), 2)
            cv2.putText(annotated, "END", (10, END_LINE_Y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            results = model.track(
                frame, persist=True, verbose=False,
                tracker="bytetrack.yaml", conf=0.3, iou=0.5, classes=target_classes,
            )

            if results and len(results) > 0 and results[0].boxes.id is not None:
                ids     = results[0].boxes.id.int().cpu().tolist()
                boxes   = results[0].boxes.xyxy.cpu().tolist()
                cls_ids = results[0].boxes.cls.int().cpu().tolist()

                for box, cls_id, obj_id in zip(boxes, cls_ids, ids):
                    label = results[0].names[int(cls_id)]
                    x1, y1, x2, y2 = map(int, box)
                    bx, by = (x1 + x2) // 2, y2

                    if by >= START_LINE_Y and obj_id not in cross:
                        cross[obj_id] = {"start_frame": frame_idx, "end_frame": None, "speed": 0}

                    if obj_id in cross and cross[obj_id]["end_frame"] is None:
                        if by <= END_LINE_Y:
                            cross[obj_id]["end_frame"] = frame_idx
                            frames_taken = abs(frame_idx - cross[obj_id]["start_frame"])
                            if frames_taken > 2:
                                time_sec = frames_taken / fps
                                speed_kmh = (distance_meters / time_sec) * 3.6
                                cross[obj_id]["speed"] = speed_kmh
                                log_entry = {
                                    "id": obj_id, "label": label,
                                    "speed": round(speed_kmh, 1), "frame": frame_idx,
                                    "overspeed": speed_kmh > overspeed_limit_kmh,
                                }
                                if not any(l["id"] == obj_id for l in all_logs):
                                    all_logs.append(log_entry)
                                    if log_entry["overspeed"]:
                                        overspeed_summary.append(log_entry)

                    current_speed = cross.get(obj_id, {}).get("speed", 0)
                    color = (0, 0, 255) if current_speed > overspeed_limit_kmh else (0, 255, 0)
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                    info = (f"{int(current_speed)} km/h" if current_speed > 0
                            else f"{label} {obj_id}")
                    cv2.putText(annotated, info, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if out:
                out.write(annotated)

            if record_config and record_config.get("live_callback"):
                count = len(all_logs)
                avg = sum(l["speed"] for l in all_logs) / count if count else 0
                mx  = max((l["speed"] for l in all_logs), default=0)
                record_config["live_callback"]({
                    "total_vehicles":   count,
                    "total_violations": len(overspeed_summary),
                    "avg_speed":        round(avg, 1),
                    "max_speed":        round(mx, 1),
                    "all_logs":         all_logs,
                    "overspeed_summary": overspeed_summary,
                })

            flag, enc = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not flag:
                continue
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + bytearray(enc) + b"\r\n"

    except Exception as e:
        print(f"generate_frames error: {e}")
    finally:
        cap.release()
        if out:
            out.release()
        if record_config and record_config.get("data_callback"):
            record_config["data_callback"]({
                "all_logs": all_logs,
                "overspeed_summary": overspeed_summary,
            })
