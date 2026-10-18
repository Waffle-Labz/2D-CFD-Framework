import numpy as np

from ..custom_shapes import SHAPES
from ..constants import *

class State:
    def __init__(self, width, height, config, dx, dy, solid=None, init_shape="NONE"):
        self.width = width
        self.height = height
        self.config = config
        self.dx = dx
        self.dy = dy

        density = config.rho_inf # DEFAULT_DENSITY
        velocity_x = DEFAULT_VELOCITY_X
        velocity_y = DEFAULT_VELOCITY_Y
        temperature = config.temperature_inf # DEFAULT_TEMPERATURE
        pressure = density * config.gas_constant * temperature
        kinetic_energy = 0.5 * density * (velocity_x**2 + velocity_y**2)
        energy = (
            pressure / (config.gamma - 1.0)
            + kinetic_energy
        )

        self.density = np.full((height, width), density, dtype=np.float64)
        self.momentum_x = np.full((height, width), density * velocity_x, dtype=np.float64)
        self.momentum_y = np.full((height, width), density * velocity_y, dtype=np.float64)
        self.energy = np.full(
            (height, width),
            energy,
            dtype=np.float64
        )
        self.solid = np.zeros((height, width), dtype=bool)

        if solid is not None:
            if solid.shape != (height, width):
                raise ValueError("Solid array must match the dimensions of the state")
            self.solid = np.array(solid, dtype=bool)

        if init_shape != "NONE":
            self.add_shape(init_shape)

    def add_shape(self, code, offset=None):

        # Check if code is a code or a custom shape (list of strings)
        if isinstance(code, list): shape = code
        else: shape = SHAPES[code]

        # Handle empty shape
        if len(shape) == 0 or len(shape[0]) == 0:
            return

        shape_height = len(shape)
        shape_width = len(shape[0])

        if any(len(row) != shape_width for row in shape):
            raise ValueError("Shape rows must all have the same length")

        start_x = self.width // 2 - shape_width // 2
        start_y = self.height // 2 - shape_height // 2

        if offset is not None:
            start_x += offset[0]
            start_y += offset[1]
        else:
            start_x += self.config.x_offset
            start_y += self.config.y_offset

        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell == "1":
                    try:
                        if 0 <= start_y + y < self.height and 0 <= start_x + x < self.width:
                            self.solid[start_y + y, start_x + x] = True
                    except (IndexError, TypeError):
                        pass

    def reset_solid(self):
        self.solid.fill(False)

    @property
    def velocity_x(self):
        return self.momentum_x / self.density

    @property
    def velocity_y(self):
        return self.momentum_y / self.density

    @property
    def velocity(self):
        return np.stack([self.velocity_x, self.velocity_y], axis=0)

    @property
    def speed(self):
        # Use np.hypot for better numerical stability and performance
        return np.hypot(self.velocity_x, self.velocity_y)

    @property
    def pressure(self):
        gamma = self.config.gamma
        # Cache velocity calculations to avoid redundant division
        inv_rho = 1.0 / self.density
        kinetic_energy = 0.5 * (self.momentum_x ** 2 + self.momentum_y ** 2) * inv_rho
        return (gamma - 1) * (self.energy - kinetic_energy)

    @property
    def mach(self):
        gamma = self.config.gamma

        # Cache velocity and pressure calculations to avoid redundant division
        inv_rho = 1.0 / self.density
        kinetic_energy = 0.5 * (self.momentum_x ** 2 + self.momentum_y ** 2) * inv_rho
        pressure = (gamma - 1) * (self.energy - kinetic_energy)
        speed_of_sound = np.sqrt(gamma * pressure * inv_rho)
        return np.sqrt(self.velocity_x ** 2 + self.velocity_y ** 2) / speed_of_sound

    @property
    def temperature(self):
        gamma = self.config.gamma
        R = self.config.gas_constant # Specific gas constant for air in J/(kg·K)

        # Cache velocity and pressure calculations to avoid redundant division
        inv_rho = 1.0 / self.density
        kinetic_energy = 0.5 * (self.momentum_x ** 2 + self.momentum_y ** 2) * inv_rho
        pressure = (gamma - 1) * (self.energy - kinetic_energy)
        return pressure * inv_rho / R

    @property
    def acceleration(self):
        # Convective acceleration
        # a = (u · ∇)u

        velocity_x = self.velocity_x
        velocity_y = self.velocity_y

        # Extend x direction
        vx_x_extended = np.concatenate(
            [velocity_x[:, :1], velocity_x, velocity_x[:, -1:]],
            axis=1
        )

        vy_x_extended = np.concatenate(
            [velocity_y[:, :1], velocity_y, velocity_y[:, -1:]],
            axis=1
        )

        # Extend y direction
        vx_y_extended = np.concatenate(
            [velocity_x[:1], velocity_x, velocity_x[-1:]],
            axis=0
        )

        vy_y_extended = np.concatenate(
            [velocity_y[:1], velocity_y, velocity_y[-1:]],
            axis=0
        )

        # Velocity derivatives
        du_dx = (
            vx_x_extended[:, 2:] - vx_x_extended[:, :-2]
        ) / (2 * self.dx)

        dv_dx = (
            vy_x_extended[:, 2:] - vy_x_extended[:, :-2]
        ) / (2 * self.dx)

        du_dy = (
            vx_y_extended[2:] - vx_y_extended[:-2]
        ) / (2 * self.dy)

        dv_dy = (
            vy_y_extended[2:] - vy_y_extended[:-2]
        ) / (2 * self.dy)

        # Convective acceleration
        acceleration_x = (
            velocity_x * du_dx
            + velocity_y * du_dy
        )

        acceleration_y = (
            velocity_x * dv_dx
            + velocity_y * dv_dy
        )

        return np.stack(
            [acceleration_x, acceleration_y],
            axis=0
        )

    @property
    def vorticity(self):
        velocity_x = self.velocity_x
        velocity_y = self.velocity_y

        # x derivatives
        vx_extended = np.concatenate(
            [velocity_x[:, :1], velocity_x, velocity_x[:, -1:]],
            axis=1
        )

        vy_extended = np.concatenate(
            [velocity_y[:, :1], velocity_y, velocity_y[:, -1:]],
            axis=1
        )

        dv_dx = (
            vy_extended[:, 2:] - vy_extended[:, :-2]
        ) / (2 * self.dx)

        # y derivatives
        vx_extended = np.concatenate(
            [velocity_x[:1], velocity_x, velocity_x[-1:]],
            axis=0
        )

        vy_extended = np.concatenate(
            [velocity_y[:1], velocity_y, velocity_y[-1:]],
            axis=0
        )

        du_dy = (
            vx_extended[2:] - vx_extended[:-2]
        ) / (2 * self.dy)

        return dv_dx - du_dy

    @property
    def density_gradient(self):
        density = self.density

        rho_x_extended = np.concatenate(
            [density[:, :1], density, density[:, -1:]],
            axis=1
        )

        rho_y_extended = np.concatenate(
            [density[:1], density, density[-1:]],
            axis=0
        )

        drho_dx = (
            rho_x_extended[:, 2:] - rho_x_extended[:, :-2]
        ) / (2 * self.dx)

        drho_dy = (
            rho_y_extended[2:] - rho_y_extended[:-2]
        ) / (2 * self.dy)

        return np.stack(
            [drho_dx, drho_dy],
            axis=0
        )

    @property
    def pressure_gradient(self):
        pressure = self.pressure

        p_x_extended = np.concatenate(
            [pressure[:, :1], pressure, pressure[:, -1:]],
            axis=1
        )

        p_y_extended = np.concatenate(
            [pressure[:1], pressure, pressure[-1:]],
            axis=0
        )

        dp_dx = (
            p_x_extended[:, 2:] - p_x_extended[:, :-2]
        ) / (2 * self.dx)

        dp_dy = (
            p_y_extended[2:] - p_y_extended[:-2]
        ) / (2 * self.dy)

        return np.stack(
            [dp_dx, dp_dy],
            axis=0
        )

    @property
    def temperature_gradient(self):
        temperature = self.temperature

        T_x_extended = np.concatenate(
            [temperature[:, :1], temperature, temperature[:, -1:]],
            axis=1
        )

        T_y_extended = np.concatenate(
            [temperature[:1], temperature, temperature[-1:]],
            axis=0
        )

        dT_dx = (
            T_x_extended[:, 2:] - T_x_extended[:, :-2]
        ) / (2 * self.dx)

        dT_dy = (
            T_y_extended[2:] - T_y_extended[:-2]
        ) / (2 * self.dy)

        return np.stack(
            [dT_dx, dT_dy],
            axis=0
        )
    
    @property
    def strain_rate(self):
        """
        Strain-rate tensor components.

        Returns:
            np.ndarray with shape (3, height, width):
            [S_xx, S_yy, S_xy]
        """
        velocity_x = self.velocity_x
        velocity_y = self.velocity_y

        # Extend x direction
        vx_x_extended = np.concatenate(
            [velocity_x[:, :1], velocity_x, velocity_x[:, -1:]],
            axis=1
        )

        vy_x_extended = np.concatenate(
            [velocity_y[:, :1], velocity_y, velocity_y[:, -1:]],
            axis=1
        )

        # Extend y direction
        vx_y_extended = np.concatenate(
            [velocity_x[:1], velocity_x, velocity_x[-1:]],
            axis=0
        )

        vy_y_extended = np.concatenate(
            [velocity_y[:1], velocity_y, velocity_y[-1:]],
            axis=0
        )

        # Velocity derivatives
        du_dx = (
            vx_x_extended[:, 2:] - vx_x_extended[:, :-2]
        ) / (2 * self.dx)

        dv_dx = (
            vy_x_extended[:, 2:] - vy_x_extended[:, :-2]
        ) / (2 * self.dx)

        du_dy = (
            vx_y_extended[2:] - vx_y_extended[:-2]
        ) / (2 * self.dy)

        dv_dy = (
            vy_y_extended[2:] - vy_y_extended[:-2]
        ) / (2 * self.dy)

        S_xx = du_dx
        S_yy = dv_dy
        S_xy = 0.5 * (du_dy + dv_dx)

        return np.stack([
            S_xx,
            S_yy,
            S_xy
        ], axis=0)

    @property
    def strain_rate_magnitude(self):
        """
        Magnitude of the strain-rate tensor.

        ||S|| = sqrt(S_xx^2 + S_yy^2 + 2*S_xy^2)

        Units: s^-1
        """

        S_xx = self.strain_rate[0]
        S_yy = self.strain_rate[1]
        S_xy = self.strain_rate[2]

        return np.sqrt(
            S_xx**2 +
            S_yy**2 +
            2 * S_xy**2
        )

    @property
    def shear_rate(self):
        """
        Magnitude of the shear rate.

        gamma_dot = 2|S_xy|
                = |du/dy + dv/dx|

        Units: s^-1
        """

        velocity_x = self.velocity_x
        velocity_y = self.velocity_y

        # Extend x direction
        vy_x_extended = np.concatenate(
            [velocity_y[:, :1], velocity_y, velocity_y[:, -1:]],
            axis=1
        )

        # Extend y direction
        vx_y_extended = np.concatenate(
            [velocity_x[:1], velocity_x, velocity_x[-1:]],
            axis=0
        )

        # Velocity derivatives
        dv_dx = (
            vy_x_extended[:, 2:] - vy_x_extended[:, :-2]
        ) / (2 * self.dx)

        du_dy = (
            vx_y_extended[2:] - vx_y_extended[:-2]
        ) / (2 * self.dy)

        return np.abs(du_dy + dv_dx)
    