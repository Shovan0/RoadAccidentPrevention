# process_video.py
import os
import cv2
from ultralytics import YOLO
import numpy as np
from datetime import datetime
import random
import string
import time

# -------------------------------
# Helper: Load Model Safely
# -------------------------------
def load_yolo_model():
    try:
        import torch
        model = YOLO("yolov8n.pt")
        return model
    except Exception as e:
        print(f"Standard load failed, applying patch: {e}")
        import torch
        original_load = torch.load
        def patched_load(*args, **kwargs):
            kwargs['weights_only'] = False
            return original_load(*args, **kwargs)
        torch.load = patched_load
        model = YOLO("yolov8n.pt")
        torch.load = original_load
        return model

model = load_yolo_model()

# -------------------------------
# 1. REAL VIDEO PROCESSING (Unchanged)
# -------------------------------
def generate_frames(video_path, overspeed_limit_kmh=60, distance_meters=20.0, record_config=None):
    if not video_path or not os.path.isfile(video_path):
        print(f"Error: Video file not found at {video_path}")
        return

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    PROCESS_W, PROCESS_H = 1280, 720
    
    out = None
    all_logs = []
    overspeed_summary = []
    
    if record_config and record_config.get("output_path"):
        os.makedirs(os.path.dirname(record_config["output_path"]), exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(record_config["output_path"], fourcc, fps, (PROCESS_W, PROCESS_H))

    # --- ADJUSTED LINE SPACING (Wider Gap) ---
    # Moved Start line lower (75%) and End line higher (25%)
    START_LINE_Y = int(PROCESS_H * 0.75)
    END_LINE_Y = int(PROCESS_H * 0.25)
    
    cross = {}
    target_classes = [2, 3, 5, 7]
    frame_idx = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret: break
            frame_idx += 1
            frame = cv2.resize(frame, (PROCESS_W, PROCESS_H))
            annotated = frame.copy()

            cv2.line(annotated, (0, START_LINE_Y), (PROCESS_W, START_LINE_Y), (0, 0, 255), 2)
            cv2.putText(annotated, "START", (10, START_LINE_Y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
            cv2.line(annotated, (0, END_LINE_Y), (PROCESS_W, END_LINE_Y), (255, 0, 0), 2)
            cv2.putText(annotated, "END", (10, END_LINE_Y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

            results = model.track(frame, persist=True, verbose=False, tracker="bytetrack.yaml", 
                                  conf=0.3, iou=0.5, classes=target_classes)

            if results and len(results) > 0 and results[0].boxes.id is not None:
                ids = results[0].boxes.id.int().cpu().tolist()
                boxes = results[0].boxes.xyxy.cpu().tolist()
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
                                log_entry = {"id": obj_id, "label": label, "speed": round(speed_kmh, 1), "frame": frame_idx, "overspeed": speed_kmh > overspeed_limit_kmh}
                                if not any(l["id"] == obj_id for l in all_logs):
                                    all_logs.append(log_entry)
                                    if log_entry["overspeed"]: overspeed_summary.append(log_entry)

                    current_speed = cross.get(obj_id, {}).get("speed", 0)
                    color = (0, 0, 255) if current_speed > overspeed_limit_kmh else (0, 255, 0)
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                    info = f"{int(current_speed)} km/h" if current_speed > 0 else f"{label} {obj_id}"
                    cv2.putText(annotated, info, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if out: out.write(annotated)
            if record_config and record_config.get("live_callback"):
                count = len(all_logs)
                avg = sum(l["speed"] for l in all_logs)/count if count else 0
                mx = max([l["speed"] for l in all_logs]) if count else 0
                record_config["live_callback"]({"total_vehicles": count, "total_violations": len(overspeed_summary), "avg_speed": round(avg, 1), "max_speed": round(mx, 1), "all_logs": all_logs, "overspeed_summary": overspeed_summary})

            (flag, encodedImage) = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not flag: continue
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

    except Exception as e: print(f"Error: {e}")
    finally:
        cap.release()
        if out: out.release()
        if record_config and record_config.get("data_callback"):
            record_config["data_callback"]({"all_logs": all_logs, "overspeed_summary": overspeed_summary})

def process_video_for_speed(video_path, overspeed_limit_kmh=60, distance_meters=20.0):
    return {"error": "Use streaming mode"}

# -------------------------------
# 2. VIRTUAL TRAFFIC SIMULATION (Smart Overtaking)
# -------------------------------
class VirtualVehicle:
    def __init__(self, id, lane_idx, lane_x, overspeed_limit):
        self.id = id
        self.lane = lane_idx
        self.x = lane_x
        self.target_x = lane_x
        # Spawn at bottom
        self.y = 720 + random.randint(0, 100) 
        self.plate = self.generate_plate()
        
        # Vehicle Type & Base Speed
        r = random.random()
        if r < 0.6: 
            self.type = "car"
            self.w, self.h = 50, 90
            self.color = (0, 255, 255) # Yellow
            self.base_speed_px = random.uniform(5, 8) 
        elif r < 0.8:
            self.type = "truck"
            self.w, self.h = 70, 140
            self.color = (255, 100, 0) # Blue
            self.base_speed_px = random.uniform(3, 5) 
        else:
            self.type = "bus"
            self.w, self.h = 65, 130
            self.color = (0, 165, 255) # Orange
            self.base_speed_px = random.uniform(4, 6)

        # Chance to Overspeed
        if random.random() < 0.3:
            self.base_speed_px *= 1.8 
            self.color = (0, 0, 255) 

        self.current_speed_px = self.base_speed_px
        
        # Speed Detection State
        self.start_frame = None
        self.end_frame = None
        self.detected_speed = 0.0
        self.is_overspeed = False
        self.active = True

    def generate_plate(self):
        # Indian Style Plate: MH 12 AB 1234
        states = ["MH", "DL", "KA", "TN", "WB", "GJ", "UP", "HR", "RJ", "MP"]
        state = random.choice(states)
        district = f"{random.randint(1, 99):02d}"
        series = "".join(random.choices(string.ascii_uppercase, k=2))
        number = f"{random.randint(1, 9999):04d}"
        return f"{state} {district} {series} {number}"

    def change_lane(self, new_lane_idx, new_lane_x):
        self.lane = new_lane_idx
        self.target_x = new_lane_x

    def update(self):
        # Move forward
        self.y -= self.current_speed_px
        
        # Smooth sideways movement (Lane Change)
        if abs(self.x - self.target_x) > 1:
            move_dir = 1 if self.target_x > self.x else -1
            self.x += move_dir * 3 # Lateral speed
            
        if self.y < -200: self.active = False

def generate_virtual_simulation(overspeed_limit_kmh=60, distance_meters=20.0, record_config=None):
    W, H = 1280, 720
    fps = 30.0
    
    # 3 Lanes
    lanes_x = [int(W*0.3), int(W*0.5), int(W*0.7)]
    vehicles = []
    vehicle_counter = 0
    
    # --- ADJUSTED LINE SPACING (Wider Gap) ---
    # Moved Start line lower (75%) and End line higher (25%)
    START_LINE_Y = int(H * 0.75)
    END_LINE_Y = int(H * 0.25)
    
    all_logs = []
    overspeed_logs = []
    frame_idx = 0

    try:
        while True:
            frame_idx += 1
            # 1. Background
            frame = np.zeros((H, W, 3), dtype=np.uint8)
            frame[:] = (60, 60, 60) 
            
            # Draw Lanes
            for lx in lanes_x:
                for i in range(0, H, 40):
                    cv2.line(frame, (lx - 70, i), (lx - 70, i+20), (255, 255, 255), 2)
            cv2.line(frame, (lanes_x[-1] + 70, 0), (lanes_x[-1] + 70, H), (255, 255, 255), 2) 
            cv2.rectangle(frame, (0, 0), (lanes_x[0]-70, H), (34, 139, 34), -1) 
            cv2.rectangle(frame, (lanes_x[-1]+70, 0), (W, H), (34, 139, 34), -1) 

            # Draw Detection Lines
            cv2.line(frame, (0, START_LINE_Y), (W, START_LINE_Y), (0, 0, 255), 3) 
            cv2.putText(frame, f"START ({distance_meters}m to End)", (10, START_LINE_Y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
            
            cv2.line(frame, (0, END_LINE_Y), (W, END_LINE_Y), (255, 0, 0), 3) 
            cv2.putText(frame, "END DETECTION", (10, END_LINE_Y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2)

            # 2. Spawn Vehicles
            if random.random() < 0.08:
                lane_choice = random.randint(0, 2)
                lane_x_pos = lanes_x[lane_choice]
                
                # Check clearance at spawn point
                is_clear = True
                for v in vehicles:
                    if v.lane == lane_choice and v.y > H - 150:
                        is_clear = False
                        break
                
                if is_clear:
                    vehicle_counter += 1
                    vehicles.append(VirtualVehicle(vehicle_counter, lane_choice, lane_x_pos, overspeed_limit_kmh))

            # 3. Update & Overtake Logic
            for v in vehicles:
                # Check for vehicle ahead
                ahead = None
                min_d = 1000
                for other in vehicles:
                    if v.id != other.id and v.lane == other.lane and other.y < v.y:
                        d = v.y - (other.y + other.h)
                        if d < min_d:
                            min_d = d
                            ahead = other
                
                # Lane Change / Slow Down logic
                if ahead and min_d < 80: # Too close
                    changed = False
                    # Try Left
                    if v.lane > 0:
                        # Check if left lane is empty in that zone
                        safe = True
                        for other in vehicles:
                            if other.lane == v.lane - 1 and abs(other.y - v.y) < 180:
                                safe = False; break
                        if safe:
                            v.change_lane(v.lane - 1, lanes_x[v.lane - 1])
                            changed = True
                    
                    # Try Right
                    if not changed and v.lane < 2:
                        safe = True
                        for other in vehicles:
                            if other.lane == v.lane + 1 and abs(other.y - v.y) < 180:
                                safe = False; break
                        if safe:
                            v.change_lane(v.lane + 1, lanes_x[v.lane + 1])
                            changed = True
                    
                    if not changed:
                        # Stuck: Match speed
                        v.current_speed_px = max(ahead.current_speed_px - 0.5, 0)
                else:
                    # Clear road: Accelerate to base speed
                    if v.current_speed_px < v.base_speed_px:
                        v.current_speed_px += 0.2

                v.update()
                
                # --- DETECTION LOGIC ---
                v_bottom = v.y + v.h
                if v.start_frame is None and v_bottom <= START_LINE_Y:
                    v.start_frame = frame_idx
                
                if v.start_frame is not None and v.end_frame is None and v_bottom <= END_LINE_Y:
                    v.end_frame = frame_idx
                    frames_taken = abs(v.end_frame - v.start_frame)
                    if frames_taken > 0:
                        time_sec = frames_taken / fps
                        calculated_speed = (distance_meters / time_sec) * 3.6
                        v.detected_speed = round(calculated_speed, 1)
                        v.is_overspeed = v.detected_speed > overspeed_limit_kmh
                        
                        log_entry = {
                            "id": v.id, 
                            "plate": v.plate, # Added Plate to Log
                            "label": v.type, 
                            "speed": v.detected_speed, 
                            "frame": frame_idx, 
                            "overspeed": v.is_overspeed
                        }
                        all_logs.append(log_entry)
                        if v.is_overspeed: overspeed_logs.append(log_entry)

                # Draw
                cv2.rectangle(frame, (int(v.x-v.w/2), int(v.y)), (int(v.x+v.w/2), int(v.y+v.h)), v.color, -1)
                
                # Draw Plate (Larger box for Indian Plate)
                cv2.rectangle(frame, (int(v.x-35), int(v.y+10)), (int(v.x+35), int(v.y+28)), (255,255,255), -1)
                cv2.putText(frame, v.plate, (int(v.x-33), int(v.y+23)), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0,0,0), 1)

                box_c = (0, 0, 255) if v.is_overspeed else (0, 255, 0)
                cv2.rectangle(frame, (int(v.x-v.w/2), int(v.y)), (int(v.x+v.w/2), int(v.y+v.h)), box_c, 2)
                
                if v.detected_speed > 0:
                    cv2.putText(frame, f"{v.detected_speed} km/h", (int(v.x-v.w/2), int(v.y)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_c, 2)
                else:
                    cv2.putText(frame, f"ID:{v.id}", (int(v.x-v.w/2), int(v.y)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

            vehicles = [v for v in vehicles if v.active]

            # Overlay
            cv2.rectangle(frame, (0, 0), (W, 40), (0, 0, 0), -1)
            cv2.putText(frame, f"LIVE SIMULATION | Vehicles: {len(all_logs)} | Violations: {len(overspeed_logs)}", (20, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Send Stats
            if record_config and record_config.get("live_callback"):
                count = len(all_logs)
                avg = sum(l["speed"] for l in all_logs)/count if count else 0
                mx = max([l["speed"] for l in all_logs]) if count else 0
                record_config["live_callback"]({
                    "total_vehicles": count, 
                    "total_violations": len(overspeed_logs),
                    "avg_speed": round(avg, 1),
                    "max_speed": round(mx, 1),
                    "all_logs": all_logs,
                    "overspeed_summary": overspeed_logs
                })

            (flag, encodedImage) = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not flag: continue
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
            time.sleep(0.03)

    except Exception as e: print(f"Sim Error: {e}")