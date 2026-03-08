# process_video.py — re-export shim for backward compatibility with main.py
# The actual implementations live in the detection/ and simulation/ packages.
from detection.tracker import generate_frames           # noqa: F401
from simulation.engine import generate_virtual_simulation  # noqa: F401
