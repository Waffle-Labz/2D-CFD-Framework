from dataclasses import dataclass

from ..constants import *

@dataclass
class Config:
    # Simulation
    paused: bool = False
    reset: bool = False
    step: bool = False
    dt: float = DEFAULT_DT
    sim_speed: int = DEFAULT_SIM_SPEED

    # Visualisation
    field: str = DEFAULT_FIELD
    vector_field: str = DEFAULT_VECTOR_FIELD
    vector_spacing: int = DEFAULT_VECTOR_SPACING
    vector_scale: float = DEFAULT_VECTOR_SCALE

    # Physics
    equation_set: str = DEFAULT_EQUATION_SET
    flux_set: str = DEFAULT_FLUX_METHOD
    gamma: float = DEFAULT_GAMMA
    dynamic_viscosity: float = DEFAULT_DYNAMIC_VISCOSITY
    thermal_conductivity: float = DEFAULT_THERMAL_CONDUCTIVITY
    gas_constant: float = DEFAULT_GAS_CONSTANT
    cfl_number: float = 0.5

    # Inflow
    rho_inf: float = DEFAULT_DENSITY_INF
    velocity_x_inf: float = DEFAULT_VELOCITY_X_INF
    velocity_y_inf: float = DEFAULT_VELOCITY_Y_INF
    energy_inf: float = 15.0
    pressure_inf: float = 1.0
    temperature_inf: float = DEFAULT_TEMPERATURE_INF

    # Colour selection
    colour_min: str = DEFAULT_COLOUR_MIN
    colour_max: str = DEFAULT_COLOUR_MAX
    colour_min_value: float = DEFAULT_MIN_COLOUR_VALUE
    colour_max_value: float = DEFAULT_MAX_COLOUR_VALUE
    auto_colour_scale: bool = DEFAULT_AUTO_COLOUR_SCALE
    auto_value_scale: bool = DEFAULT_AUTO_VALUE_SCALE

    # Shape
    shape_has_changed: bool = False
    shape: str = DEFAULT_SHAPE
    x_offset: int = DEFAULT_X_OFFSET
    y_offset: int = DEFAULT_Y_OFFSET

    # Current cell
    current_cell: tuple[int, int] = (0, 0)
    current_density: float = 0.0
    current_pressure: float = 0.0
    current_velocity: tuple[float, float] = (0.0, 0.0)
    current_energy: float = 0.0
    current_mach: float = 0.0
    current_temperature: float = 0.0
    
