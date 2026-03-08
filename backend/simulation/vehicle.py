import random
import string
import cv2
import numpy as np

from .constants import VEHICLE_COLORS, H


class VirtualVehicle:
    """Top-down 3-D style vehicle sprite for the virtual simulation."""

    def __init__(self, vid, lane_idx, lane_x, overspeed_limit):
        self.id        = vid
        self.lane      = lane_idx
        self.x         = float(lane_x)
        self.target_x  = float(lane_x)
        self.y         = float(H + random.randint(0, 100))
        self.plate     = self._generate_plate()

        r = random.random()
        if r < 0.6:
            self.type       = "car"
            self.w, self.h  = 66, 122
            self.base_color = random.choice(VEHICLE_COLORS["car"])
            self.base_speed = random.uniform(5, 8)
        elif r < 0.8:
            self.type       = "truck"
            self.w, self.h  = 90, 190
            self.base_color = random.choice(VEHICLE_COLORS["truck"])
            self.base_speed = random.uniform(3, 5)
        else:
            self.type       = "bus"
            self.w, self.h  = 84, 174
            self.base_color = random.choice(VEHICLE_COLORS["bus"])
            self.base_speed = random.uniform(4, 6)

        if random.random() < 0.3:          # ~30 % chance to overspeed
            self.base_speed *= 1.8

        self.current_speed  = self.base_speed
        self.start_frame    = None
        self.end_frame      = None
        self.detected_speed = 0.0
        self.is_overspeed   = False
        self.active         = True
        self.plate_captured  = False
        self.scan_start_frame = None

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _generate_plate():
        states   = ["MH", "DL", "KA", "TN", "WB", "GJ", "UP", "HR", "RJ", "MP"]
        state    = random.choice(states)
        district = f"{random.randint(1, 99):02d}"
        series   = "".join(random.choices(string.ascii_uppercase, k=2))
        number   = f"{random.randint(1, 9999):04d}"
        return f"{state} {district} {series} {number}"

    def change_lane(self, new_lane_idx, new_lane_x):
        self.lane     = new_lane_idx
        self.target_x = float(new_lane_x)

    def update(self):
        self.y -= self.current_speed
        if abs(self.x - self.target_x) > 1:
            self.x += 3 if self.target_x > self.x else -3
        if self.y < -200:
            self.active = False

    # ------------------------------------------------------------------ drawing
    def draw(self, frame, current_frame):
        cx = int(self.x)
        ty = int(self.y)
        hw = self.w // 2
        h  = self.h
        bc    = self.base_color
        dark  = tuple(max(0, c - 65) for c in bc)
        light = tuple(min(255, c + 80) for c in bc)
        mid   = tuple(max(0, c - 28) for c in bc)

        if self.type == "car":
            self._draw_car(frame, cx, ty, hw, h, bc, dark, light, mid)
        elif self.type == "truck":
            self._draw_truck(frame, cx, ty, hw, h, bc, dark, light, mid)
        else:
            self._draw_bus(frame, cx, ty, hw, h, bc, dark, light, mid)

        # Bounding box while vehicle is being tracked between the two trap lines
        if self.start_frame is not None and self.end_frame is None:
            track_col = (0, 255, 180)   # teal – actively tracked
            cv2.rectangle(frame, (cx - hw - 5, ty - 5), (cx + hw + 5, ty + h + 5), track_col, 2)
            cv2.putText(frame, "TRACKING",
                        (cx - hw, ty - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.40, track_col, 1)

        # Flashing red border when overspeeding
        if self.is_overspeed:
            flash = (current_frame // 8) % 2 == 0
            bdr = (0, 0, 255) if flash else (60, 60, 255)
            cv2.rectangle(frame, (cx - hw - 3, ty - 3), (cx + hw + 3, ty + h + 3), bdr, 3)

        # Number plate at rear (bottom)
        self._draw_plate(frame, cx, ty + h - 46)

        # Bounding box around the number plate
        pw = 130
        plate_y = ty + h - 46
        cv2.rectangle(frame,
                      (cx - pw // 2 - 4, plate_y - 4),
                      (cx + pw // 2 + 4, plate_y + 42),
                      (0, 220, 255), 2)
        cv2.putText(frame, "PLATE",
                    (cx - pw // 2, plate_y - 7),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 220, 255), 1)

        # Scan animation after violation capture
        if self.scan_start_frame is not None:
            progress = (current_frame - self.scan_start_frame) / 28.0
            if progress <= 1.3:
                self._draw_scan(frame, cx, ty + h - 46, hw, progress)

        # Speed / ID label above vehicle
        lc = (0, 0, 255) if self.is_overspeed else (0, 230, 0)
        if self.detected_speed > 0:
            lbl = (f"{self.detected_speed} km/h"
                   f"{'  !VIOLATION' if self.is_overspeed else ''}")
            cv2.putText(frame, lbl, (cx - hw, ty - 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, lc, 2)
        else:
            cv2.putText(frame, f"ID:{self.id}", (cx - hw, ty - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (210, 210, 210), 1)

    # ── CAR ──────────────────────────────────────────────────────────────────
    def _draw_car(self, frame, cx, ty, hw, h, bc, dark, light, mid):
        rm = max(hw // 3, 8)
        rt = ty + h // 5
        rb = ty + 4 * h // 5

        # Drop shadow
        cv2.fillPoly(frame, [np.array([
            [cx-hw+6, ty+6], [cx+hw+6, ty+6],
            [cx+hw+6, ty+h+6], [cx-hw+6, ty+h+6]], np.int32)], (18, 18, 18))

        # Body
        cv2.rectangle(frame, (cx-hw, ty), (cx+hw, ty+h), bc, -1)

        # Hood (front = top)
        cv2.fillPoly(frame, [np.array([
            [cx-hw+5, ty], [cx+hw-5, ty],
            [cx+hw, ty+9], [cx-hw, ty+9]], np.int32)], light)

        # Trunk (rear = bottom)
        cv2.fillPoly(frame, [np.array([
            [cx-hw, ty+h-9], [cx+hw, ty+h-9],
            [cx+hw-5, ty+h], [cx-hw+5, ty+h]], np.int32)], dark)

        # Roof
        cv2.rectangle(frame, (cx-hw+rm, rt), (cx+hw-rm, rb), dark, -1)
        cv2.rectangle(frame, (cx-hw+rm, rt), (cx+hw-rm, rb), mid, 1)

        # Front windshield (semi-transparent)
        ws = np.array([[cx-hw+5,ty+9],[cx+hw-5,ty+9],
                       [cx+hw-rm,rt],[cx-hw+rm,rt]], np.int32)
        ov = frame.copy(); cv2.fillPoly(ov, [ws], (165, 215, 255))
        cv2.addWeighted(ov, 0.65, frame, 0.35, 0, frame)
        cv2.line(frame, (cx-hw+8, ty+11), (cx+hw-rm+2, rt+2), (225, 245, 255), 1)

        # Rear window
        rw = np.array([[cx-hw+rm,rb],[cx+hw-rm,rb],
                       [cx+hw-5, ty+h-9],[cx-hw+5,ty+h-9]], np.int32)
        ov2 = frame.copy(); cv2.fillPoly(ov2, [rw], (105, 148, 215))
        cv2.addWeighted(ov2, 0.55, frame, 0.45, 0, frame)

        # Side windows
        for x1, x2 in [(cx-hw, cx-hw+rm-1), (cx+hw-rm+1, cx+hw)]:
            ov3 = frame.copy()
            cv2.fillPoly(ov3, [np.array(
                [[x1,rt+3],[x2,rt+3],[x2,rb-3],[x1,rb-3]], np.int32)],
                (130, 188, 238))
            cv2.addWeighted(ov3, 0.55, frame, 0.45, 0, frame)

        # Door line + handles
        door_mid = (rt + rb) // 2
        cv2.line(frame, (cx-hw, door_mid), (cx+hw, door_mid), dark, 1)
        for hx in [cx-hw+rm//2, cx+hw-rm//2]:
            cv2.rectangle(frame, (hx-4, door_mid-8), (hx+4, door_mid-5), light, -1)

        # Outline
        cv2.rectangle(frame, (cx-hw, ty), (cx+hw, ty+h), dark, 1)

        # Wheels
        wr = max(8, hw // 5)
        for wx, wy in [(cx-hw-2, ty+16), (cx+hw+2, ty+16),
                       (cx-hw-2, ty+h-16), (cx+hw+2, ty+h-16)]:
            self._draw_wheel(frame, wx, wy, wr)

        # Headlights (front)
        cv2.ellipse(frame, (cx-hw//2, ty+4), (hw//3+1, 3), 0,0,360, (255,255,185), -1)
        cv2.ellipse(frame, (cx+hw//2, ty+4), (hw//3+1, 3), 0,0,360, (255,255,185), -1)

        # Taillights (rear)
        cv2.rectangle(frame, (cx-hw+4, ty+h-6), (cx-hw+16, ty+h-2), (0,30,255), -1)
        cv2.rectangle(frame, (cx+hw-16, ty+h-6), (cx+hw-4, ty+h-2), (0,30,255), -1)

    # ── TRUCK ─────────────────────────────────────────────────────────────────
    def _draw_truck(self, frame, cx, ty, hw, h, bc, dark, light, mid):
        cabin_h   = h // 3
        cargo_end = ty + h - cabin_h

        cv2.fillPoly(frame, [np.array([
            [cx-hw+6,ty+6],[cx+hw+6,ty+6],
            [cx+hw+6,ty+h+6],[cx-hw+6,ty+h+6]], np.int32)], (18, 18, 18))

        # Cargo box
        cv2.rectangle(frame, (cx-hw+5, ty), (cx+hw-5, cargo_end), mid, -1)
        for ly in range(ty+14, cargo_end-4, 18):
            cv2.line(frame, (cx-hw+5, ly), (cx+hw-5, ly), dark, 1)
        cv2.rectangle(frame, (cx-hw+5, ty), (cx-hw+11, cargo_end), dark, -1)
        cv2.rectangle(frame, (cx+hw-11, ty), (cx+hw-5, cargo_end), dark, -1)
        cv2.rectangle(frame, (cx-hw+5, ty), (cx+hw-5, cargo_end), dark, 1)

        # Cabin
        cv2.rectangle(frame, (cx-hw, cargo_end), (cx+hw, ty+h), bc, -1)
        ov = frame.copy()
        cv2.rectangle(ov, (cx-hw+8, cargo_end+6), (cx+hw-8, ty+h-5), (155,210,255), -1)
        cv2.addWeighted(ov, 0.65, frame, 0.35, 0, frame)
        cv2.rectangle(frame, (cx-hw, ty+h-9), (cx+hw, ty+h), light, -1)
        cv2.rectangle(frame, (cx-hw, cargo_end), (cx+hw, ty+h), dark, 1)

        # Taillights (cargo top = rear)
        cv2.rectangle(frame, (cx-hw+8, ty+2), (cx-hw+20, ty+6), (0,30,255), -1)
        cv2.rectangle(frame, (cx+hw-20, ty+2), (cx+hw-8, ty+6), (0,30,255), -1)

        # Headlights (cabin bottom = front)
        cv2.rectangle(frame, (cx-hw+5, ty+h-7), (cx-hw+18, ty+h-3), (255,255,200), -1)
        cv2.rectangle(frame, (cx+hw-18, ty+h-7), (cx+hw-5, ty+h-3), (255,255,200), -1)

        # Wheels
        for wx, wy in [(cx-hw-2, ty+16), (cx+hw+2, ty+16),
                       (cx-hw-2, cargo_end+cabin_h//2), (cx+hw+2, cargo_end+cabin_h//2)]:
            self._draw_wheel(frame, wx, wy, 10)

    # ── BUS ───────────────────────────────────────────────────────────────────
    def _draw_bus(self, frame, cx, ty, hw, h, bc, dark, light, mid):
        cv2.fillPoly(frame, [np.array([
            [cx-hw+6,ty+6],[cx+hw+6,ty+6],
            [cx+hw+6,ty+h+6],[cx-hw+6,ty+h+6]], np.int32)], (18, 18, 18))

        body = np.array([
            [cx-hw+5,ty],[cx+hw-5,ty],
            [cx+hw,ty+6],[cx+hw,ty+h-6],
            [cx+hw-5,ty+h],[cx-hw+5,ty+h],
            [cx-hw,ty+h-6],[cx-hw,ty+6]], np.int32)
        cv2.fillPoly(frame, [body], bc)
        cv2.rectangle(frame, (cx-hw+5, ty), (cx+hw-5, ty+6), light, -1)
        cv2.rectangle(frame, (cx+hw-8, ty+6), (cx+hw, ty+h-6), dark, -1)

        # Windows
        for i in range(4):
            wy = ty + 14 + i * ((h-44)//4)
            if wy + 17 > ty + h - 22:
                break
            for x1, x2 in [(cx-hw+4, cx-3), (cx+3, cx+hw-4)]:
                cv2.rectangle(frame, (x1, wy), (x2, wy+17), (155,210,255), -1)
                cv2.rectangle(frame, (x1, wy), (x2, wy+17), dark, 1)
                cv2.line(frame, (x1+2, wy+2), (x1+2, wy+15), (210,235,255), 1)

        # Centre door
        door_top = ty + h//2 - 18
        cv2.rectangle(frame, (cx-12, door_top), (cx+12, ty+h-5), dark, 1)
        cv2.line(frame, (cx, door_top), (cx, ty+h-5), dark, 1)
        cv2.polylines(frame, [body], True, dark, 1)

        # Headlights (top = front)
        cv2.rectangle(frame, (cx-hw+4, ty+2), (cx-hw+20, ty+7), (255,255,200), -1)
        cv2.rectangle(frame, (cx+hw-20, ty+2), (cx+hw-4, ty+7), (255,255,200), -1)

        # Taillights (bottom = rear)
        cv2.rectangle(frame, (cx-hw+4, ty+h-7), (cx-hw+22, ty+h-2), (0,30,255), -1)
        cv2.rectangle(frame, (cx+hw-22, ty+h-7), (cx+hw-4, ty+h-2), (0,30,255), -1)

        # Wheels
        for wx, wy in [(cx-hw-2, ty+18), (cx+hw+2, ty+18),
                       (cx-hw-2, ty+h-18), (cx+hw+2, ty+h-18)]:
            self._draw_wheel(frame, wx, wy, 10)

    # ── SHARED ────────────────────────────────────────────────────────────────
    @staticmethod
    def _draw_wheel(frame, wx, wy, wr):
        cv2.circle(frame, (wx, wy), wr, (14, 14, 14), -1)
        cv2.circle(frame, (wx, wy), wr-2, (44, 44, 44), -1)
        cv2.line(frame, (wx-wr+3, wy), (wx+wr-3, wy), (164, 164, 164), 1)
        cv2.line(frame, (wx, wy-wr+3), (wx, wy+wr-3), (164, 164, 164), 1)
        cv2.circle(frame, (wx, wy), 3, (210, 210, 210), -1)

    def _draw_plate(self, frame, cx, py):
        """Indian-style plate: white background, dark-red header strip, black text."""
        pw, ph = 130, 38
        cv2.rectangle(frame, (cx-pw//2, py), (cx+pw//2, py+ph), (255,255,255), -1)
        cv2.rectangle(frame, (cx-pw//2, py), (cx+pw//2, py+10), (170, 0, 0),   -1)
        cv2.rectangle(frame, (cx-pw//2, py), (cx+pw//2, py+ph), (0, 0, 0),      1)
        parts = self.plate.split()
        if len(parts) == 4:
            cv2.putText(frame, f"{parts[0]} {parts[1]}",
                        (cx-pw//2+5, py+24), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0,0,0), 1)
            cv2.putText(frame, f"{parts[2]} {parts[3]}",
                        (cx-pw//2+5, py+35), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0,0,0), 1)
        else:
            cv2.putText(frame, self.plate,
                        (cx-pw//2+4, py+28), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0,0,0), 1)

    def _draw_scan(self, frame, cx, py, hw, progress):
        """Green scan line animates over the plate when a violation is locked."""
        pw, ph = 130, 38
        if progress <= 1.0:
            scan_y = int(py + progress * ph)
            ov = frame.copy()
            cv2.rectangle(ov, (cx-pw//2, py), (cx+pw//2, scan_y), (0, 255, 80), -1)
            cv2.addWeighted(ov, 0.2, frame, 0.8, 0, frame)
            cv2.line(frame, (cx-pw//2, scan_y), (cx+pw//2, scan_y), (0, 255, 100), 2)
        else:
            cv2.putText(frame, "CAPTURED", (cx-hw, py-4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 100), 1)
