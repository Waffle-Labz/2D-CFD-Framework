from pathlib import Path
import re

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Configuration
# snapshot_dir = Path("data/airfoils_200/NACA2412_20/snapshots/")
snapshot_dir = Path("snapshots/")

gamma = 1.4
dt = 0.001  # Replace with your actual timestep in seconds

# Sort snapshots by their numerical frame number
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
        energy = data["energy"].copy()
        solid = data["solid"].copy()

        frame = get_frame_number(file)
        timestamp = frame * dt

        # Calculate pressure
        with np.errstate(divide="ignore", invalid="ignore"):
            pressure = (gamma - 1) * (
                energy - 0.5 * (mx**2 + my**2) / rho
            )

        pressure = np.ma.masked_where(
            solid | ~np.isfinite(pressure),
            pressure,
        )

        snapshots.append((frame, timestamp, pressure))

# Consistent colour scale across every frame
valid_pressures = [
    pressure.compressed()
    for _, _, pressure in snapshots
    if pressure.count() > 0
]

if not valid_pressures:
    raise ValueError("No valid fluid pressure values found.")

vmin = min(float(p.min()) for p in valid_pressures)
vmax = max(float(p.max()) for p in valid_pressures)

# Create figure
fig, ax = plt.subplots(figsize=(12, 6), dpi=100)

frame, timestamp, pressure = snapshots[0]

image = ax.imshow(
    pressure,
    origin="upper",
    cmap="coolwarm",
    aspect="equal",
    vmin=vmin,
    vmax=vmax,
    interpolation="nearest",
)

fig.colorbar(image, ax=ax, label="Pressure")
ax.set_xlabel("x (grid cells)")
ax.set_ylabel("y (grid cells)")

title = ax.set_title("")


def update(index):
    frame, timestamp, pressure = snapshots[index]

    image.set_data(pressure)
    title.set_text(
        f"Pressure | Frame {frame}"
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
plt.show()
