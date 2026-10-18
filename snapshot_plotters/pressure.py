import numpy as np
import matplotlib.pyplot as plt

data = np.load("data/airfoils_200/NACA2412_15/snapshots/snapshot_2000.npz")

rho = data["density"]
mx = data["momentum_x"]
my = data["momentum_y"]
energy = data["energy"]
solid = data["solid"]


MINIMUM, MAXIMUM = 100_000, 140_000
# MINIMUM, MAXIMUM = None, None

gamma = 1.4

pressure = (gamma - 1) * (
    energy - 0.5 * (mx**2 + my**2) / rho
)

# Hide the solid cells
pressure = np.ma.masked_where(solid, pressure)

plt.figure(figsize=(12, 5))

plt.imshow(
    pressure,
    origin="upper",
    cmap="coolwarm",
    aspect="equal",
    vmin=MINIMUM,
    vmax=MAXIMUM
)

plt.colorbar(label="Pressure")
plt.title("Pressure field")
plt.xlabel("x (grid cells)")
plt.ylabel("y (grid cells)")
plt.tight_layout()
plt.show()