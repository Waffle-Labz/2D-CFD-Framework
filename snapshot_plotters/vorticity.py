import numpy as np
import matplotlib.pyplot as plt

# Load snapshot
# data = np.load("data/airfoils_200/NACA2412_20/snapshots/snapshot_2000.npz")
data = np.load("data/geometry/diamond/snapshots/snapshot_1000.npz")

rho = data["density"]
mx = data["momentum_x"]
my = data["momentum_y"]
solid = data["solid"]

# Grid spacing (metres)
dx = 1.0  # Replace with your actual grid spacing
dy = 1.0  # Replace with your actual grid spacing

# Calculate velocity components
u = mx / rho
v = my / rho

# Calculate vorticity: dv/dx - du/dy
dv_dy, dv_dx = np.gradient(v, dy, dx)
du_dy, du_dx = np.gradient(u, dy, dx)

vorticity = dv_dx - du_dy

# Mask solid cells
vorticity = np.ma.masked_where(solid, vorticity)

# Plot
limit = np.max(np.abs(vorticity.compressed()))

fig, ax = plt.subplots(figsize=(12, 5))

im = ax.imshow(
    vorticity,
    origin="upper",
    cmap="RdBu_r",
    aspect="equal",
    vmin=-limit,
    vmax=limit,
)

fig.colorbar(im, ax=ax, label="Vorticity (s⁻¹)")
ax.set_title("Vorticity Field")
ax.set_xlabel("x (grid cells)")
ax.set_ylabel("y (grid cells)")

plt.tight_layout()
plt.show()