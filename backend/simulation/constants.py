# Road and frame dimensions
W, H = 1440, 800

# Speed-trap line positions (fraction of frame height)
START_LINE_Y = int(H * 0.75)
END_LINE_Y   = int(H * 0.25)

# Lane centre X positions
LANES_X = [int(W * 0.3), int(W * 0.5), int(W * 0.7)]

# Road left/right boundary
ROAD_LEFT  = LANES_X[0]  - 70
ROAD_RIGHT = LANES_X[-1] + 70

# Simulation FPS
SIM_FPS = 30.0

# Vehicle body colours  (BGR)
VEHICLE_COLORS = {
    "car": [
        (30,  30,  190),   # deep red
        (190, 30,  30),    # deep blue
        (25,  25,  25),    # near-black
        (200, 200, 200),   # silver
        (240, 240, 240),   # white
        (20,  110, 20),    # dark green
        (20,  80,  160),   # mid blue
        (180, 120, 30),    # bronze
    ],
    "truck": [
        (80,  70,  170),
        (35,  110, 35),
        (160, 110, 35),
        (120, 120, 120),
    ],
    "bus": [
        (0,   160, 240),
        (0,   90,  190),
        (25,  175, 25),
    ],
}
