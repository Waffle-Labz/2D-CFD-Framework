import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from math import sin, pi

# Configuration
# snapshot_path = Path("snapshots/snapshot_1000.npz")
snapshot_path = Path("data/airfoils_200/NACA2412_20/snapshots/snapshot_2000.npz")
gamma = 1.4

# Freestream conditions — change if the simulation uses different values
# rho_inf = 1.0
rho_inf = 131700 / (287.05 * 300)
u_inf = 200
v_inf = 0.0
# p_inf = rho_inf * 287.05 * 300
p_inf = 131700

V_inf = np.sqrt(u_inf**2 + v_inf**2)
q_inf = 0.5 * rho_inf * V_inf**2  # Freestream dynamic pressure

# Load snapshot
with np.load(snapshot_path) as data:
    rho = data["density"].astype(float)
    mx = data["momentum_x"].astype(float)
    my = data["momentum_y"].astype(float)
    energy = data["energy"].astype(float)
    solid = data["solid"].astype(bool)

# Calculate local pressure
with np.errstate(divide="ignore", invalid="ignore"):
    kinetic_energy = np.divide(
        mx**2 + my**2,
        2 * rho,
        out=np.full_like(rho, np.nan),
        where=rho > 0,
    )
    pressure = (gamma - 1) * (energy - kinetic_energy)

# Calculate pressure coefficient
cp = (pressure - p_inf) * sin(20 * pi / 180) / q_inf

# Mask solid cells and invalid values
invalid = (
    solid
    | (rho <= 0)
    | (pressure <= 0)
    | ~np.isfinite(cp)
)
cp = np.ma.masked_where(invalid, cp)

# Plot
fig, ax = plt.subplots(figsize=(12, 6))

image = ax.imshow(
    cp,
    origin="upper",
    cmap="coolwarm",
    aspect="equal",
    interpolation="nearest",
)

ax.set_title(
    f"Pressure Coefficient"
)
ax.set_xlabel("X cell")
ax.set_ylabel("Y cell")

# Symmetric colour scale makes positive and negative Cp easier to compare
limit = max(
    abs(float(cp.min())),
    abs(float(cp.max())),
)
if limit > 0:
    image.set_clim(-limit, limit)

image.set_clim(-0.3, 0.3)

cbar = fig.colorbar(image, ax=ax)
cbar.set_label(r"Pressure coefficient, $C_p$")

plt.tight_layout()
plt.show()

# fluid = ~solid

# print("Freestream pressure:", p_inf)
# print("Fluid pressure min:", np.min(pressure[fluid]))
# print("Fluid pressure max:", np.max(pressure[fluid]))
# print("Cp min:", np.min(cp[fluid]))
# print("Cp max:", np.max(cp[fluid]))