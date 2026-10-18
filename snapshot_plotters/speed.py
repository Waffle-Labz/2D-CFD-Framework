import numpy as np
import matplotlib.pyplot as plt

data = np.load("data/airfoils_200/NACA2412_15/snapshots/snapshot_2000.npz")

rho = data["density"]
mx = data["momentum_x"]
my = data["momentum_y"]
solid = data["solid"]

MINIMUM, MAXIMUM = 0, 200
# MINIMUM, MAXIMUM = None, None

# Calculate speed magnitude
u = mx / rho
v = my / rho
speed = np.sqrt(u**2 + v**2)

# Hide solid cells
speed = np.ma.masked_where(solid, speed)

# Plot
plt.figure(figsize=(12, 5))
if MAXIMUM != None and MINIMUM != None:
    plt.imshow(
        speed,
        origin="upper",
        cmap="viridis",
        aspect="equal",
        vmin=MINIMUM,
        vmax=MAXIMUM
    )
else:
    plt.imshow(
        speed,
        origin="upper",
        cmap="viridis",
        aspect="equal",
    )

plt.colorbar(label="Speed (m/s)")
plt.title("Speed Magnitude")
plt.xlabel("x (grid cells)")
plt.ylabel("y (grid cells)")
plt.tight_layout()
plt.show()