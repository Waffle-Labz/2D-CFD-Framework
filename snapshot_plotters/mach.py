import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configuration
# snapshot_path = Path("data/airfoils_200/NACA2412_20/snapshots/snapshot_2000.npz")
snapshot_path = Path("snapshots/snapshot_1000.npz")
gamma = 1.4

# Load snapshot
with np.load(snapshot_path) as data:
    density = data["density"].astype(float)
    momentum_x = data["momentum_x"].astype(float)
    momentum_y = data["momentum_y"].astype(float)
    energy = data["energy"].astype(float)
    solid = data["solid"].astype(bool)

# Calculate velocity
with np.errstate(divide="ignore", invalid="ignore"):
    u = momentum_x / density
    v = momentum_y / density

# Calculate pressure
pressure = (gamma - 1) * (
    energy - 0.5 * (momentum_x**2 + momentum_y**2) / density
)

# Calculate speed of sound and Mach number
with np.errstate(divide="ignore", invalid="ignore"):
    speed = np.sqrt(u**2 + v**2)
    sound_speed = np.sqrt(gamma * pressure / density)
    mach = speed / sound_speed

# Mask solid cells and invalid values
invalid = (
    solid
    | ~np.isfinite(mach)
    | (density <= 0)
    | (pressure <= 0)
)
mach = np.ma.masked_where(invalid, mach)

# Plot
fig, ax = plt.subplots(figsize=(12, 6))

image = ax.imshow(
    mach,
    origin="upper",
    cmap="viridis",
    aspect="equal",
    interpolation="nearest",
    vmin=0,
)

ax.set_title(f"Mach Number")
ax.set_xlabel("X cell")
ax.set_ylabel("Y cell")

cbar = fig.colorbar(image, ax=ax)
cbar.set_label("Mach number")

plt.tight_layout()
plt.show()