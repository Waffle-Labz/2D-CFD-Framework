from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, to_rgb

# Configuration
snapshot_path = Path("data/airfoils_200/NACA2412_20/snapshots/snapshot_2000.npz")  # Set your snapshot path
spacing = 6
background_colour = "#f0f0f0"
solid_colour = "#404040"

if not snapshot_path.is_file():
    raise FileNotFoundError(f"Snapshot not found: {snapshot_path}")

with np.load(snapshot_path) as data:
    rho = data["density"].copy()
    mx = data["momentum_x"].copy()
    my = data["momentum_y"].copy()
    solid = data["solid"].copy()

# Extract frame number from filename
frame = int(snapshot_path.stem.removeprefix("snapshot_"))

# Calculate velocity and speed
with np.errstate(divide="ignore", invalid="ignore"):
    u = mx / rho
    v = my / rho
    speed = np.sqrt(u**2 + v**2)

valid = (
    (~solid)
    & np.isfinite(speed)
    & np.isfinite(u)
    & np.isfinite(v)
)

if not np.any(valid):
    raise ValueError("No valid fluid cells to plot.")

vmax = float(np.max(speed[valid]))
if vmax == 0:
    vmax = 1.0

norm = Normalize(vmin=0, vmax=vmax)
cmap = plt.get_cmap("viridis")

# Solid regions and fluid background
background = np.empty((*rho.shape, 3))
background[:] = to_rgb(background_colour)
background[solid] = to_rgb(solid_colour)

fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
ax.imshow(background, origin="upper", interpolation="nearest")

# Sample velocity vectors
y, x = np.mgrid[
    0:rho.shape[0]:spacing,
    0:rho.shape[1]:spacing,
]

sample_u = u[::spacing, ::spacing]
sample_v = v[::spacing, ::spacing]
sample_speed = speed[::spacing, ::spacing]
sample_valid = valid[::spacing, ::spacing]

x = x[sample_valid]
y = y[sample_valid]
sample_u = sample_u[sample_valid]
sample_v = -sample_v[sample_valid]
sample_speed = sample_speed[sample_valid]

# Limit the longest arrow to 80% of the spacing between vectors
max_length = spacing * 0.8

max_speed = np.max(sample_speed)
if max_speed > 0:
    vector_u = sample_u * (max_length / max_speed)
    vector_v = sample_v * (max_length / max_speed)
else:
    vector_u = sample_u
    vector_v = sample_v

vectors = ax.quiver(
    x, y,
    vector_u, vector_v,
    sample_speed,
    cmap=cmap,
    norm=norm,
    angles="xy",
    scale_units="xy",
    scale=1,
    pivot="mid",
    width=0.003,
    headwidth=2.5,
    headlength=3,
    headaxislength=2.5,
)

fig.colorbar(vectors, ax=ax, label="Speed (m/s)")
ax.set_title(f"Velocity Vector Field — Frame {frame}")
ax.set_xlabel("x (grid cells)")
ax.set_ylabel("y (grid cells)")
ax.set_xlim(-0.5, rho.shape[1] - 0.5)
ax.set_ylim(rho.shape[0] - 0.5, -0.5)
ax.set_aspect("equal")

plt.tight_layout()
plt.show()