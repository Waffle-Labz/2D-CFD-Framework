import numpy as np

from ..constants import *
from .state import State
from .numerical_fluxes import lax_friedrichs_x, lax_friedrichs_y, hll_x, hll_y, hllc_x, hllc_y, viscous_flux

class Solver():
    def __init__(self, dx, dy, k, mu, gamma, R):
        self.dx = dx
        self.dy = dy
        self.k = k
        self.mu = mu
        self.gamma = gamma
        self.R = R

        self.rho_inf = DEFAULT_DENSITY_INF
        self.u_inf = DEFAULT_VELOCITY_X_INF
        self.v_inf = DEFAULT_VELOCITY_Y_INF
        self.T_inf = DEFAULT_TEMPERATURE_INF

        self.flux_set_x = None
        self.flux_set_y = None

        self.navier_stokes = False # Flag to dis/enable navier-stokes terms

    def step(self, state, dt) -> State:

        if self.flux_set_x is None or self.flux_set_y is None: 
            raise ValueError("Flux set is not defined. Please set the flux set before calling step().")

        # state.momentum_x[:, 0] = 2 * self.rho_inf * self.u_inf

        new_state = State(state.width, state.height, config=state.config, solid=state.solid, dx=state.dx, dy=state.dy)

        # Copy input state to new_state (will update interior cells below)
        new_state.density = np.copy(state.density)
        new_state.momentum_x = np.copy(state.momentum_x)
        new_state.momentum_y = np.copy(state.momentum_y)
        new_state.energy = np.copy(state.energy)

        # Determine update region based on boundary flags
        # If PERSISTENT_INFLOW=True, column 0 is treated as boundary (not updated)
        # If PERSISTENT_INFLOW=False, column 0 is treated as fluid (updated normally)
        # If PERSISTENT_OUTFLOW=True, column -1 is treated as boundary (not updated)
        # If PERSISTENT_OUTFLOW=False, column -1 is treated as fluid (updated normally)
        x_start = 1 if PERSISTENT_INFLOW else 0
        x_end = state.width - 1 if PERSISTENT_OUTFLOW else state.width

        # Define interior region (1 to height-1, x_start to x_end)
        y_slice = slice(1, state.height - 1)
        x_slice = slice(x_start, x_end)

        # Get interior cells
        interior_solid = state.solid[y_slice, x_slice]
        
        # Create conservative state arrays for interior region and neighbors
        U_center = np.stack([
            state.density[y_slice, x_slice],
            state.momentum_x[y_slice, x_slice],
            state.momentum_y[y_slice, x_slice],
            state.energy[y_slice, x_slice]
        ], axis=0)

        # Build left neighbor states
        if PERSISTENT_INFLOW:
            # Left boundary is maintained by apply_boundary_conditions(), read it normally
            U_left = np.stack([
                state.density[y_slice, x_start-1:x_end-1],
                state.momentum_x[y_slice, x_start-1:x_end-1],
                state.momentum_y[y_slice, x_start-1:x_end-1],
                state.energy[y_slice, x_start-1:x_end-1]
            ], axis=0)
        else:
            # Closed left boundary: create reflected ghost state for column -1
            U_boundary = np.stack([
                state.density[y_slice, 0:1],
                state.momentum_x[y_slice, 0:1],
                state.momentum_y[y_slice, 0:1],
                state.energy[y_slice, 0:1]
            ], axis=0)
            U_ghost = self.wall_state_bulk(U_boundary, "x")
            U_left = np.stack([
                np.concatenate([U_ghost[0], state.density[y_slice, 0:x_end-1]], axis=1),
                np.concatenate([U_ghost[1], state.momentum_x[y_slice, 0:x_end-1]], axis=1),
                np.concatenate([U_ghost[2], state.momentum_y[y_slice, 0:x_end-1]], axis=1),
                np.concatenate([U_ghost[3], state.energy[y_slice, 0:x_end-1]], axis=1)
            ], axis=0)

        # Build right neighbor states
        if PERSISTENT_OUTFLOW:
            # Right boundary is maintained by apply_boundary_conditions(), read it normally
            U_right = np.stack([
                state.density[y_slice, x_start+1:x_end+1],
                state.momentum_x[y_slice, x_start+1:x_end+1],
                state.momentum_y[y_slice, x_start+1:x_end+1],
                state.energy[y_slice, x_start+1:x_end+1]
            ], axis=0)
        else:
            # Closed right boundary: create reflected ghost state for column width
            U_boundary = np.stack([
                state.density[y_slice, -1:],
                state.momentum_x[y_slice, -1:],
                state.momentum_y[y_slice, -1:],
                state.energy[y_slice, -1:]
            ], axis=0)
            U_ghost = self.wall_state_bulk(U_boundary, "x")
            U_right = np.stack([
                np.concatenate([state.density[y_slice, x_start+1:], U_ghost[0]], axis=1),
                np.concatenate([state.momentum_x[y_slice, x_start+1:], U_ghost[1]], axis=1),
                np.concatenate([state.momentum_y[y_slice, x_start+1:], U_ghost[2]], axis=1),
                np.concatenate([state.energy[y_slice, x_start+1:], U_ghost[3]], axis=1)
            ], axis=0)

        U_bottom = np.stack([
            state.density[0:-2, x_slice],
            state.momentum_x[0:-2, x_slice],
            state.momentum_y[0:-2, x_slice],
            state.energy[0:-2, x_slice]
        ], axis=0)

        U_top = np.stack([
            state.density[2:, x_slice],
            state.momentum_x[2:, x_slice],
            state.momentum_y[2:, x_slice],
            state.energy[2:, x_slice]
        ], axis=0)

        # Handle solid boundaries (match dimensions with U_left/U_right)
        if PERSISTENT_INFLOW:
            solid_left = state.solid[y_slice, x_start-1:x_end-1]
        else:
            solid_left = np.concatenate([state.solid[y_slice, 0:1], state.solid[y_slice, 0:x_end-1]], axis=1)
        
        if PERSISTENT_OUTFLOW:
            solid_right = state.solid[y_slice, x_start+1:x_end+1]
        else:
            solid_right = np.concatenate([state.solid[y_slice, x_start+1:], state.solid[y_slice, -1:]], axis=1)
        
        solid_bottom = state.solid[0:-2, x_slice]
        solid_top = state.solid[2:, x_slice]

        # Apply wall states where needed
        U_left_wall = self.wall_state_bulk(U_center, "x")
        U_right_wall = self.wall_state_bulk(U_center, "x")
        U_bottom_wall = self.wall_state_bulk(U_center, "y")
        U_top_wall = self.wall_state_bulk(U_center, "y")

        # Select between neighbor state and wall state based on solid
        U_left = np.where(solid_left[None, :, :], U_left_wall, U_left)
        U_right = np.where(solid_right[None, :, :], U_right_wall, U_right)
        U_bottom = np.where(solid_bottom[None, :, :], U_bottom_wall, U_bottom)
        U_top = np.where(solid_top[None, :, :], U_top_wall, U_top)

        # Calculate inviscid fluxes
        F_left = self.flux_set_x(U_left, U_center, self.gamma)
        F_right = self.flux_set_x(U_center, U_right, self.gamma)
        G_bottom = self.flux_set_y(U_bottom, U_center, self.gamma)
        G_top = self.flux_set_y(U_center, U_top, self.gamma)

        if self.navier_stokes:
          
            (
                F_viscous_left,
                F_viscous_right,
                G_viscous_bottom,
                G_viscous_top
            ) = viscous_flux(
                state,
                self.dx,
                self.dy,
                self.k,
                self.mu
            )

            # Viscous fluxes are computed for the interior region (1:height-1, 1:width-1)
            # which has width-2 and height-2 dimensions.
            # F_viscous_left/right represent fluxes at interfaces for interior cells at columns 1 to width-2.
            # We need to map these to the corresponding positions in F_left/F_right.
            
            # Determine which columns in U_center correspond to interior cells
            # Interior cells are in columns 1 to state.width-2
            interior_start = max(1, x_start)
            interior_end = min(state.width - 1, x_end)
            
            if interior_start < interior_end:
                # Indices in F_left/F_right arrays (relative to their own slicing)
                # When x_start=0: U_center has columns 0 to x_end-1, so column 1 is at index 1
                # When x_start=1: U_center has columns 1 to x_end-1, so column 1 is at index 0
                f_start_idx = interior_start - x_start
                f_end_idx = interior_end - x_start
                
                # Indices in viscous flux arrays (always for interior cells 1 to width-2)
                v_start_idx = interior_start - 1
                v_end_idx = interior_end - 1
                
                # Subtract viscous fluxes from inviscid fluxes
                # F arrays have shape (4, height-2, width), columns are in last dimension
                F_left[:, :, f_start_idx:f_end_idx] -= F_viscous_left[:, :, v_start_idx:v_end_idx]
                F_right[:, :, f_start_idx:f_end_idx] -= F_viscous_right[:, :, v_start_idx:v_end_idx]
                
                # G arrays have shape (4, height-2, width), columns are in last dimension
                G_bottom[:, :, v_start_idx:v_end_idx] -= G_viscous_bottom[:, :, v_start_idx:v_end_idx]
                G_top[:, :, v_start_idx:v_end_idx] -= G_viscous_top[:, :, v_start_idx:v_end_idx]

        # Update conservative state
        U_new = U_center - dt / self.dx * (F_right - F_left) - dt / self.dy * (G_top - G_bottom)

        # Store updated values (skip solid cells)
        non_solid = ~interior_solid
        new_state.density[y_slice, x_slice] = np.where(non_solid, U_new[0], state.density[y_slice, x_slice])
        new_state.momentum_x[y_slice, x_slice] = np.where(non_solid, U_new[1], state.momentum_x[y_slice, x_slice])
        new_state.momentum_y[y_slice, x_slice] = np.where(non_solid, U_new[2], state.momentum_y[y_slice, x_slice])
        new_state.energy[y_slice, x_slice] = np.where(non_solid, U_new[3], state.energy[y_slice, x_slice])

        self.apply_boundary_conditions(new_state)

        return new_state
                
    def conservative_state(self, state, x, y):
        return np.array([
            state.density[y, x],
            state.momentum_x[y, x],
            state.momentum_y[y, x],
            state.energy[y, x]
        ], dtype=np.float64)

    def apply_boundary_conditions(self, state: State):

        # Handle left boundary (column 0)
        if PERSISTENT_INFLOW:
            self.apply_inflow(state)

        # Handle right boundary (column -1)
        if PERSISTENT_OUTFLOW:
            self.apply_outflow(state)

        if SLIP_WALLS: self.apply_slip_walls(state)
        elif not SLIP_WALLS: self.apply_no_slip_walls(state)

    def apply_slip_walls(self, state: State):
        # Remove momentum normal to the boundary (y since walls are horizontal)
        # Bottom wall - vectorized
        state.density[0, :] = state.density[1, :]
        state.momentum_x[0, :] = state.momentum_x[1, :]
        state.momentum_y[0, :] = 0.0
        state.energy[0, :] = state.energy[1, :]

        # Top wall - vectorized
        state.density[-1, :] = state.density[-2, :]
        state.momentum_x[-1, :] = state.momentum_x[-2, :]
        state.momentum_y[-1, :] = 0.0
        state.energy[-1, :] = state.energy[-2, :]

    def apply_no_slip_walls(self, state: State):
        # Remove all momentum
        # Bottom wall - vectorized
        state.density[0, :] = state.density[1, :]
        state.momentum_x[0, :] = 0.0
        state.momentum_y[0, :] = 0.0
        state.energy[0, :] = state.energy[1, :]

        # Top wall - vectorized
        state.density[-1, :] = state.density[-2, :]
        state.momentum_x[-1, :] = 0.0
        state.momentum_y[-1, :] = 0.0
        state.energy[-1, :] = state.energy[-2, :]

    def apply_inflow(self, state: State):
        # Vectorized inflow boundary condition
        state.density[:, 0] = self.rho_inf
        state.momentum_x[:, 0] = self.rho_inf * self.u_inf
        state.momentum_y[:, 0] = self.rho_inf * self.v_inf
        pressure = self.rho_inf * self.R * self.T_inf
        kinetic_energy = 0.5 * self.rho_inf * (
            self.u_inf**2 + self.v_inf**2
        )
        state.energy[:, 0] = pressure / (self.gamma - 1.0) + kinetic_energy

    def apply_outflow(self, state: State):
        # Vectorized outflow boundary condition
        state.density[:, -1] = state.density[:, -2]
        state.momentum_x[:, -1] = state.momentum_x[:, -2]
        state.momentum_y[:, -1] = state.momentum_y[:, -2]
        state.energy[:, -1] = state.energy[:, -2]

    def wall_state_bulk(self, U, direction):
        """Vectorized wall state calculation for 3D arrays (4, height, width)"""
        result = np.array(U, dtype=np.float64)

        if direction == "x":
            result[1] = -result[1]  # Negate x-momentum for x-direction walls
        elif direction == "y":
            result[2] = -result[2]  # Negate y-momentum for y-direction walls

        return result

    def update_method(self, equation_set: str, flux_set: str):
        if flux_set == "lax-friedrichs":
            self.flux_set_x = lax_friedrichs_x
            self.flux_set_y = lax_friedrichs_y

        elif flux_set == "hll":
            self.flux_set_x = hll_x
            self.flux_set_y = hll_y

        elif flux_set == "hllc":
            self.flux_set_x = hllc_x
            self.flux_set_y = hllc_y

        else:
            raise ValueError(f"Unknown flux set: {flux_set}")

        if equation_set == "euler":
            self.navier_stokes = False

        elif equation_set == "navier-stokes":
            self.navier_stokes = True

        else:
            raise ValueError(f"Unknown equation set: {equation_set}")


    def reset(self, state: State):
        return State(state.width, state.height, config=state.config, solid=state.solid, dx=state.dx, dy=state.dy)


        