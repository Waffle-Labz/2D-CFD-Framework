from pathlib import Path
import re

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Configuration
snapshot_dir = Path("data/airfoils_200/NACA2412_20/snapshots/")

dt = 0.001  # Replace with your actual timestep in seconds

# Sort snapshots numerically by frame number
def get_frame_number(path):
    match = re.fullmatch(r"snapshot_(\d+)\.npz", path.name)
    if match is None:
        raise ValueError(f"Unexpected snapshot filename: {path.name}")
    return int(match.group(1))

files = sorted(
    snapshot_dir.glob("snapshot_*.npz"),
    key=get_frame_number,
)

if not files:
    raise FileNotFoundError("No snapshots found.")

snapshots = []

for file in files:
    with np.load(file) as data:
        rho = data["density"].copy()
        mx = data["momentum_x"].copy()
        my = data["momentum_y"].copy()
        solid = data["solid"].copy()

        frame = get_frame_number(file)
        timestamp = frame * dt

        # Speed magnitude
        with np.errstate(divide="ignore", invalid="ignore"):
            speed = np.sqrt(mx**2 + my**2) / rho

        speed = np.ma.masked_where(
            solid | ~np.isfinite(speed),
            speed,
        )

        snapshots.append((frame, timestamp, speed))

# Consistent colour scale across all frames
vmax = max(
    float(speed.max())
    for _, _, speed in snapshots
    if speed.count() > 0
)

fig, ax = plt.subplots(figsize=(12, 6))

image = ax.imshow(
    snapshots[0][2],
    origin="upper",
    cmap="viridis",
    aspect="equal",
    vmin=0,
    vmax=vmax,
    interpolation="nearest",
)

fig.colorbar(image, ax=ax, label="Speed (m/s)")
ax.set_xlabel("x (grid cells)")
ax.set_ylabel("y (grid cells)")

title = ax.set_title("")


def update(index):
    frame, timestamp, speed = snapshots[index]

    image.set_data(speed)
    title.set_text(
        f"Speed | Frame {frame}"
    )

    return image, title


animation = FuncAnimation(
    fig,
    update,
    frames=len(snapshots),
    interval=100,
    blit=False,
    repeat=True,
)

plt.tight_layout()

# animation.save(
#     "images/airfoils/20_speed_animation.gif",
#     writer="pillow",
#     fps=10,
#     dpi=100,
# )

# print("GIF saved to circle_speed_animation.gif")

plt.show()
