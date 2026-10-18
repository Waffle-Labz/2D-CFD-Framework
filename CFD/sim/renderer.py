import pygame
import numpy as np
from math import atan2, pi, sin, cos

from .state import State
from .solver import Solver
from ..constants import *


class SimRenderer:
    def __init__(self, width, height, config, 
                 solver: Solver, state: State, 
                 current_cell_update_method, cfl_update_method,
                 data_collection_dict: dict
                 ):
        self.width = width
        self.height = height
        self.config = config
        self.solver = solver
        self.state = state
        self.current_cell_update_method = current_cell_update_method
        self.update_cfl_number = cfl_update_method
        self.cfl_num = -1
        self.data_collection_dict = data_collection_dict

        self.data_metric_functions = {
            DataMetric.MIN_SPEED:
                lambda: np.min(self.state.speed),

            DataMetric.MAX_SPEED:
                lambda: np.max(self.state.speed),

            DataMetric.AVERAGE_SPEED:
                lambda: np.mean(self.state.speed),

            DataMetric.MIN_PRESSURE:
                lambda: np.min(self.state.pressure),

            DataMetric.MAX_PRESSURE:
                lambda: np.max(self.state.pressure),

            DataMetric.AVERAGE_PRESSURE:
                lambda: np.mean(self.state.pressure),

            DataMetric.MIN_DENSITY:
                lambda: np.min(self.state.density),

            DataMetric.MAX_DENSITY:
                lambda: np.max(self.state.density),

            DataMetric.AVERAGE_DENSITY:
                lambda: np.mean(self.state.density),

            DataMetric.MIN_TEMPERATURE:
                lambda: np.min(self.state.temperature),

            DataMetric.MAX_TEMPERATURE:
                lambda: np.max(self.state.temperature),

            DataMetric.AVERAGE_TEMPERATURE:
                lambda: np.mean(self.state.temperature),

            DataMetric.MIN_MACH:
                lambda: np.min(self.state.mach),

            DataMetric.MAX_MACH:
                lambda: np.max(self.state.mach),

            DataMetric.AVERAGE_MACH:
                lambda: np.mean(self.state.mach)
        }
        
        pygame.init()

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("2D CFD Framework")

        self.time_passed = 0.0
        self.frame = 0
        self.clock = pygame.time.Clock()
        self.running = True

    def world_to_screen(self, x, y):
        screen_x = int(x / self.state.width * self.width)
        screen_y = int((1 - y / self.state.height) * self.height)

        return screen_x, screen_y

    def value_to_colour(self, value, minimum, maximum, auto_colour_scale, colour_min, colour_max):
        if maximum == minimum:
            normalised = np.zeros_like(value, dtype=np.float32)
        else:
            normalised = np.clip(
                (value - minimum) / (maximum - minimum),
                0,
                1
            )

        if auto_colour_scale:
            # N-point automatic colour scale
            colour_stops = [
                (0.00, (0, 0, 255)),
                (0.25, (0, 255, 255)),
                (0.50, (0, 255, 0)),
                (0.75, (255, 255, 0)),
                (1.00, (255, 0, 0))
            ]

            positions = np.array(
                [position for position, colour in colour_stops]
            )

            colours = np.array(
                [colour for position, colour in colour_stops],
                dtype=np.float32
            )

            indices = np.searchsorted(
                positions,
                normalised,
                side="right"
            )

            indices = np.clip(
                indices,
                1,
                len(positions) - 1
            )

            lower = indices - 1
            upper = indices

            t = (
                normalised - positions[lower]
            ) / (
                positions[upper] - positions[lower]
            )

            rgb = (
                colours[lower]
                + (colours[upper] - colours[lower]) * t[..., None]
            )

        else:
            # User-defined two-point colour scale
            min_rgb = np.array(
                pygame.Color(colour_min)[:3],
                dtype=np.float32
            )

            max_rgb = np.array(
                pygame.Color(colour_max)[:3],
                dtype=np.float32
            )

            rgb = (
                min_rgb
                + (max_rgb - min_rgb) * normalised[..., None]
            )

        return np.clip(rgb, 0, 255).astype(np.uint8)

    def draw_field(self, field, auto_colour_scale, auto_value_scale, colour_min, colour_max, colour_min_value, colour_max_value):

        # Sets the min and max values
        if auto_value_scale:
            minimum = np.min(field)
            maximum = np.max(field)
        else:
            minimum = colour_min_value
            maximum = colour_max_value

        rgb = self.value_to_colour(
            field,
            minimum,
            maximum,
            auto_colour_scale,
            colour_min,
            colour_max
        )

        # Create texture
        texture = pygame.surfarray.make_surface(
            np.transpose(rgb, (1, 0, 2))
        )

        # Scale texture to renderer dimensions
        texture = pygame.transform.scale(
            texture,
            (self.width, self.height)
        )

        # Draw entire field in one operation
        self.screen.blit(texture, (0, 0))

    def draw_vectors(self, vector_field, vector_spacing: int, vector_scale: float):
        dx = self.solver.dx
        dy = self.solver.dy

        component_x = vector_field[0]
        component_y = vector_field[1]

        solid = self.state.solid

        arrow_size = 4
        arrow_angle = pi / 6  # 30 degrees

        max_dx = vector_spacing * dx * 0.45 # Lower number = more space, 0.5 maximum
        max_dy = vector_spacing * dy * 0.45

        for y in range(0, self.state.height, vector_spacing):
            for x in range(0, self.state.width, vector_spacing):

                if solid[y, x]:
                    continue

                u = component_x[y, x]
                v = component_y[y, x]

                # Scale vector
                vector_x = u * vector_scale
                vector_y = v * vector_scale

                # Limit each component independently
                vector_x = np.clip(vector_x, -max_dx, max_dx)
                vector_y = np.clip(vector_y, -max_dy, max_dy)

                # Centre of cell
                start_x = x * dx + dx // 2
                start_y = y * dy + dy // 2

                end_x = start_x + vector_x
                end_y = start_y - vector_y

                # Draw vector
                pygame.draw.line(
                    self.screen,
                    VECTOR_ARROW_COLOUR,
                    (start_x, start_y),
                    (end_x, end_y),
                    1
                )

                # Direction of vector
                angle = atan2(
                    end_y - start_y,
                    end_x - start_x
                )

                # Arrowhead
                left_x = end_x - arrow_size * cos(angle - arrow_angle)
                left_y = end_y - arrow_size * sin(angle - arrow_angle)

                right_x = end_x - arrow_size * cos(angle + arrow_angle)
                right_y = end_y - arrow_size * sin(angle + arrow_angle)

                pygame.draw.line(
                    self.screen,
                    VECTOR_ARROW_COLOUR,
                    (end_x, end_y),
                    (left_x, left_y),
                    1
                )

                pygame.draw.line(
                    self.screen,
                    VECTOR_ARROW_COLOUR,
                    (end_x, end_y),
                    (right_x, right_y),
                    1
                )

    def draw_solids(self):
        dx = self.solver.dx
        dy = self.solver.dy

        state = self.state

        for y in range(state.height):
            for x in range(state.width):
                if state.solid[y, x]:
                    pygame.draw.rect(
                        self.screen,
                        (255, 255, 255),
                        (
                            x * dx,
                            y * dy,
                            dx,
                            dy
                        )
                    )

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # elif event.type == pygame.MOUSEMOTION:
            #     mouse_x, mouse_y = event.pos

        # Update current cell every frame
        mouse_x, mouse_y = pygame.mouse.get_pos()

        x = int(mouse_x // self.solver.dx)
        y = int(mouse_y // self.solver.dy)

        if 0 <= x < self.state.width and 0 <= y < self.state.height:

            # Update current cell info in config
            self.config.current_cell = (x, y)
            self.config.current_density = self.state.density[y, x]
            self.config.current_pressure = self.state.pressure[y, x]
            self.config.current_velocity = (
                self.state.velocity_x[y, x],
                self.state.velocity_y[y, x]
            )
            self.config.current_energy = self.state.energy[y, x]
            self.config.current_mach = self.state.mach[y, x]
            self.config.current_temperature = self.state.temperature[y, x]

            self.current_cell_update_method()

    def calculate_cfl(self):
        rho = self.state.density
        u = self.state.velocity_x
        v = self.state.velocity_y
        p = self.state.pressure

        c = np.sqrt(self.config.gamma * p / rho)

        cfl = self.config.dt * (
            (np.abs(u) + c) / self.state.dx
            + (np.abs(v) + c) / self.state.dy
        )

        # Ignore solid cells
        cfl = np.where(self.state.solid, 0.0, cfl)

        return np.max(cfl)

    def render(self, config):
        self.screen.fill((0, 0, 0))
        config.field = config.field.lower()
        config.vector_field = config.vector_field.lower()


        if config.field == "speed":
            self.draw_field(
                self.state.speed,
                auto_colour_scale=config.auto_colour_scale,
                auto_value_scale=config.auto_value_scale,
                colour_min=config.colour_min,
                colour_max=config.colour_max,
                colour_min_value=config.colour_min_value,
                colour_max_value=config.colour_max_value
            )

        if config.field == "density":
            self.draw_field(
                self.state.density, 
                auto_colour_scale=config.auto_colour_scale,
                auto_value_scale=config.auto_value_scale,
                colour_min=config.colour_min,
                colour_max=config.colour_max,
                colour_min_value=config.colour_min_value,
                colour_max_value=config.colour_max_value
            )

        if config.field == "pressure":
            self.draw_field(
                self.state.pressure, 
                auto_colour_scale=config.auto_colour_scale,
                auto_value_scale=config.auto_value_scale,
                colour_min=config.colour_min,
                colour_max=config.colour_max,
                colour_min_value=config.colour_min_value,
                colour_max_value=config.colour_max_value
            )

        if config.field == "velocity x":
            self.draw_field(
                self.state.velocity_x,
                auto_colour_scale=config.auto_colour_scale,
                auto_value_scale=config.auto_value_scale,
                colour_min=config.colour_min,
                colour_max=config.colour_max,
                colour_min_value=config.colour_min_value,
                colour_max_value=config.colour_max_value
            )

        if config.field == "velocity y":
            self.draw_field(
                self.state.velocity_y,
                auto_colour_scale=config.auto_colour_scale,
                auto_value_scale=config.auto_value_scale,
                colour_min=config.colour_min,
                colour_max=config.colour_max,
                colour_min_value=config.colour_min_value,
                colour_max_value=config.colour_max_value
            )

        if config.field == "momentum x":
            self.draw_field(
                self.state.momentum_x,
                auto_colour_scale=config.auto_colour_scale,
                auto_value_scale=config.auto_value_scale,
                colour_min=config.colour_min,
                colour_max=config.colour_max,
                colour_min_value=config.colour_min_value,
                colour_max_value=config.colour_max_value
            )

        if config.field == "momentum y":
            self.draw_field(
                self.state.momentum_y,
                auto_colour_scale=config.auto_colour_scale,
                auto_value_scale=config.auto_value_scale,
                colour_min=config.colour_min,
                colour_max=config.colour_max,
                colour_min_value=config.colour_min_value,
                colour_max_value=config.colour_max_value
            )

        if config.field == "energy":
            self.draw_field(
                self.state.energy,
                auto_colour_scale=config.auto_colour_scale,
                auto_value_scale=config.auto_value_scale,
                colour_min=config.colour_min,
                colour_max=config.colour_max,
                colour_min_value=config.colour_min_value,
                colour_max_value=config.colour_max_value
            )

        if config.field == "temperature":
            self.draw_field(
                self.state.temperature,
                auto_colour_scale=config.auto_colour_scale,
                auto_value_scale=config.auto_value_scale,
                colour_min=config.colour_min,
                colour_max=config.colour_max,
                colour_min_value=config.colour_min_value,
                colour_max_value=config.colour_max_value
            )

        if config.field == "vorticity":
            self.draw_field(
                self.state.vorticity,
                auto_colour_scale=config.auto_colour_scale,
                auto_value_scale=config.auto_value_scale,
                colour_min=config.colour_min,
                colour_max=config.colour_max,
                colour_min_value=config.colour_min_value,
                colour_max_value=config.colour_max_value
            )

        if config.field == "strain rate":
            self.draw_field(
                self.state.strain_rate_magnitude,
                auto_colour_scale=config.auto_colour_scale,
                auto_value_scale=config.auto_value_scale,
                colour_min=config.colour_min,
                colour_max=config.colour_max,
                colour_min_value=config.colour_min_value,
                colour_max_value=config.colour_max_value
            )

        if config.field == "shear rate":
            self.draw_field(
                self.state.shear_rate,
                auto_colour_scale=config.auto_colour_scale,
                auto_value_scale=config.auto_value_scale,
                colour_min=config.colour_min,
                colour_max=config.colour_max,
                colour_min_value=config.colour_min_value,
                colour_max_value=config.colour_max_value
            )

        self.draw_solids()

        if config.vector_field == "velocity":
            self.draw_vectors(self.state.velocity, vector_spacing=config.vector_spacing, vector_scale=config.vector_scale)

        if config.vector_field == "acceleration":
            self.draw_vectors(self.state.acceleration, vector_spacing=config.vector_spacing, vector_scale=config.vector_scale)
        
        if config.vector_field == "pressure gradient":
            self.draw_vectors(self.state.pressure_gradient, vector_spacing=config.vector_spacing, vector_scale=config.vector_scale)

        if config.vector_field == "density gradient":
            self.draw_vectors(self.state.density_gradient, vector_spacing=config.vector_spacing, vector_scale=config.vector_scale)

        if config.vector_field == "temperature gradient":
                self.draw_vectors(self.state.temperature_gradient, vector_spacing=config.vector_spacing, vector_scale=config.vector_scale)        

        pygame.display.flip()

    def update(self, dt: float, config):

        cfl = self.calculate_cfl()

        if cfl > 1:
            print("Unstable CFL. Reduce timestep")
            return

        if cfl != self.cfl_num:
            self.cfl_num = cfl
            self.config.cfl_number = cfl
            self.update_cfl_number()

        self.handle_events()

        # Update solver inflow numbers
        self.solver.gamma = config.gamma
        self.solver.rho_inf = config.rho_inf
        self.solver.u_inf = config.velocity_x_inf
        self.solver.v_inf = config.velocity_y_inf
        # self.solver.p_inf = config.pressure_inf
        self.solver.T_inf = config.temperature_inf
        # self.solver.E_inf = config.energy_inf
        self.solver.k = config.thermal_conductivity
        self.solver.mu = config.dynamic_viscosity
        self.solver.R = config.gas_constant

        # Update state's shape if it has changed
        if config.shape_has_changed:
            self.state.reset_solid()
            self.state.add_shape(config.shape)
            config.shape_has_changed = False

        if not config.paused:
            for _ in range(config.sim_speed):
                self.state = self.solver.step(self.state, dt)
        if config.reset: 
            self.state = self.solver.reset(self.state)
            self.solver.apply_inflow(self.state)
            self.solver.apply_outflow(self.state)
            config.reset = False
        if config.step: 
            # Performs exactly one physics update
            self.state = self.solver.step(self.state, dt)
            config.step = False

        self.render(config=config)

        self.clock.tick(60)
        self.time_passed += dt
        self.frame += 1

        self.update_data_collection()

    def update_data_collection(self):
        for metric in self.data_collection_dict:

            if metric == DataMetric.CFL_VALUE:
                value = self.config.cfl_number

            elif metric == DataMetric.FRAME:
                value = self.frame

            elif metric == DataMetric.TIMESTAMP:
                value = self.time_passed

            else:
                value = self.data_metric_functions[metric]()

            self.data_collection_dict[metric].append(value)

        return self.data_collection_dict


    def run(self, field=None, dt=0.0001):
        while self.running:
            self.handle_events()
            self.state = self.solver.step(self.state, dt)
            # self.render(self.state.density)
            self.clock.tick(60)

        pygame.quit()

    def close(self):
        pygame.quit()
