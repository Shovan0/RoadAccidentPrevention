import cv2
import numpy as np

from .constants import W, H, LANES_X, ROAD_LEFT, ROAD_RIGHT, START_LINE_Y, END_LINE_Y


def draw_road(frame, distance_meters: float) -> None:
    """
    Draw a completely STATIC road scene — like a real fixed-position speed camera.
    Nothing moves here; only vehicles drawn on top will animate.
    """
    # ── Background (grass) ──────────────────────────────────────────────────
    frame[:, :ROAD_LEFT]  = (34, 100, 34)   # green grass left
    frame[:, ROAD_RIGHT:]  = (34, 100, 34)   # green grass right

    # Subtle grass texture strips (fixed)
    for gx in range(0, ROAD_LEFT - 8, 18):
        cv2.line(frame, (gx, 0), (gx, H), (28, 88, 28), 1)
    for gx in range(ROAD_RIGHT + 8, W, 18):
        cv2.line(frame, (gx, 0), (gx, H), (28, 88, 28), 1)

    # ── Asphalt ─────────────────────────────────────────────────────────────
    frame[:, ROAD_LEFT:ROAD_RIGHT] = (52, 52, 52)

    # ── Curb stripes (alternating red / white, fixed positions) ─────────────
    stripe_h = 20
    for i in range(H // stripe_h + 1):
        y0 = i * stripe_h
        y1 = y0 + stripe_h
        color = (0, 0, 200) if i % 2 == 0 else (240, 240, 240)
        cv2.rectangle(frame, (ROAD_LEFT - 10, y0), (ROAD_LEFT,      y1), color, -1)
        cv2.rectangle(frame, (ROAD_RIGHT,     y0), (ROAD_RIGHT + 10, y1), color, -1)

    # ── Lane dividers (dashed white centre lines, fixed) ────────────────────
    num_lanes = len(LANES_X)
    for i in range(1, num_lanes):
        div_x = (LANES_X[i-1] + LANES_X[i]) // 2
        dash_len, gap_len = 28, 20
        step = dash_len + gap_len
        for y in range(0, H, step):
            cv2.rectangle(frame,
                          (div_x - 2, y),
                          (div_x + 2, y + dash_len),
                          (255, 255, 255), -1)

    # ── Solid edge lines ────────────────────────────────────────────────────
    cv2.line(frame, (ROAD_LEFT,  0), (ROAD_LEFT,  H), (255, 255, 255), 2)
    cv2.line(frame, (ROAD_RIGHT, 0), (ROAD_RIGHT, H), (255, 255, 255), 2)

    # ── Distance-marker posts (fixed positions) ──────────────────────────────
    pole_xs = [ROAD_LEFT - 22, ROAD_RIGHT + 22]
    marker_interval = H // 4
    for py in range(marker_interval // 2, H, marker_interval):
        for px in pole_xs:
            cv2.rectangle(frame, (px-4, py-30), (px+4, py+30), (130, 110, 80), -1)
            cv2.rectangle(frame, (px-12, py-5),  (px+12, py+5), (230, 200, 150), -1)

    # ── Speed-trap detection lines ───────────────────────────────────────────
    # (Removed) Trap lines and labels — detection now uses frame-to-frame pixel distance
    # Speed is calculated internally without visual trap lines on screen
