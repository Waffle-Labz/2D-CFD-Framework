import numpy as np

def lax_friedrichs_x(left, right, gamma):
    rho_l, mx_l, my_l, E_l = left
    rho_r, mx_r, my_r, E_r = right

    u_l = mx_l / rho_l
    u_r = mx_r / rho_r

    p_l = (gamma - 1) * (
        E_l - 0.5 * (mx_l**2 + my_l**2) / rho_l
    )

    p_r = (gamma - 1) * (
        E_r - 0.5 * (mx_r**2 + my_r**2) / rho_r
    )

    c_l = (gamma * p_l / rho_l) ** 0.5
    c_r = (gamma * p_r / rho_r) ** 0.5
  
    alpha = np.maximum(
        np.abs(u_l) + c_l,
        np.abs(u_r) + c_r
    )

    F_l = np.array([
        mx_l,
        mx_l * u_l + p_l,
        mx_l * (my_l / rho_l),
        u_l * (E_l + p_l)
    ], dtype=np.float64)

    F_r = np.array([
        mx_r,
        mx_r * u_r + p_r,
        mx_r * (my_r / rho_r),
        u_r * (E_r + p_r)
    ], dtype=np.float64)

    return 0.5 * (F_l + F_r - alpha * (right - left))

def lax_friedrichs_y(bottom, top, gamma):
    rho_b, mx_b, my_b, E_b = bottom
    rho_t, mx_t, my_t, E_t = top

    v_b = my_b / rho_b
    v_t = my_t / rho_t

    p_b = (gamma - 1) * (
        E_b - 0.5 * (mx_b**2 + my_b**2) / rho_b
    )

    p_t = (gamma - 1) * (
        E_t - 0.5 * (mx_t**2 + my_t**2) / rho_t
    )

    c_b = (gamma * p_b / rho_b) ** 0.5
    c_t = (gamma * p_t / rho_t) ** 0.5

    alpha = np.maximum(
        np.abs(v_b) + c_b,
        np.abs(v_t) + c_t
    )

    G_b = np.array([
        my_b,
        my_b * (mx_b / rho_b),
        my_b * v_b + p_b,
        v_b * (E_b + p_b)
    ], dtype=np.float64)

    G_t = np.array([
        my_t,
        my_t * (mx_t / rho_t),
        my_t * v_t + p_t,
        v_t * (E_t + p_t)
    ], dtype=np.float64)

    return 0.5 * (G_b + G_t - alpha * (top - bottom))


def hll_x(left, right, gamma):
    rho_l, mx_l, my_l, E_l = left
    rho_r, mx_r, my_r, E_r = right

    # Primitive variables
    u_l = mx_l / rho_l
    v_l = my_l / rho_l

    u_r = mx_r / rho_r
    v_r = my_r / rho_r

    # Pressure
    p_l = (gamma - 1) * (
        E_l - 0.5 * (mx_l**2 + my_l**2) / rho_l
    )

    p_r = (gamma - 1) * (
        E_r - 0.5 * (mx_r**2 + my_r**2) / rho_r
    )

    # Speed of sound
    c_l = (gamma * p_l / rho_l) ** 0.5
    c_r = (gamma * p_r / rho_r) ** 0.5

    # Wave speeds
    S_l = np.minimum(
        u_l - c_l,
        u_r - c_r
    )

    S_r = np.maximum(
        u_l + c_l,
        u_r + c_r
    )

    # Physical fluxes
    F_l = np.array([
        mx_l,
        mx_l * u_l + p_l,
        mx_l * v_l,
        u_l * (E_l + p_l)
    ], dtype=np.float64)

    F_r = np.array([
        mx_r,
        mx_r * u_r + p_r,
        mx_r * v_r,
        u_r * (E_r + p_r)
    ], dtype=np.float64)

    # Determine HLL flux using np.where for vectorization
    F_star = (S_r * F_l - S_l * F_r + S_l * S_r * (right - left)) / (S_r - S_l)
    
    # Use np.where to select flux based on wave speeds
    result = np.where(S_l >= 0, F_l, np.where(S_r <= 0, F_r, F_star))
    
    return result

def hll_y(bottom, top, gamma):
    rho_b, mx_b, my_b, E_b = bottom
    rho_t, mx_t, my_t, E_t = top

    # Primitive variables
    u_b = mx_b / rho_b
    v_b = my_b / rho_b

    u_t = mx_t / rho_t
    v_t = my_t / rho_t

    # Pressure
    p_b = (gamma - 1) * (
        E_b - 0.5 * (mx_b**2 + my_b**2) / rho_b
    )

    p_t = (gamma - 1) * (
        E_t - 0.5 * (mx_t**2 + my_t**2) / rho_t
    )

    # Speed of sound
    c_b = (gamma * p_b / rho_b) ** 0.5
    c_t = (gamma * p_t / rho_t) ** 0.5

    # Wave speeds
    S_b = np.minimum(
        v_b - c_b,
        v_t - c_t
    )

    S_t = np.maximum(
        v_b + c_b,
        v_t + c_t
    )

    # Physical fluxes
    G_b = np.array([
        my_b,
        my_b * u_b,
        my_b * v_b + p_b,
        v_b * (E_b + p_b)
    ], dtype=np.float64)

    G_t = np.array([
        my_t,
        my_t * u_t,
        my_t * v_t + p_t,
        v_t * (E_t + p_t)
    ], dtype=np.float64)

    # Determine HLL flux using np.where for vectorization
    G_star = (S_t * G_b - S_b * G_t + S_b * S_t * (top - bottom)) / (S_t - S_b)
    
    # Use np.where to select flux based on wave speeds
    result = np.where(S_b >= 0, G_b, np.where(S_t <= 0, G_t, G_star))
    
    return result


def hllc_x(left, right, gamma):
    rho_l, mx_l, my_l, E_l = left
    rho_r, mx_r, my_r, E_r = right

    # Primitive variables
    u_l = mx_l / rho_l
    v_l = my_l / rho_l

    u_r = mx_r / rho_r
    v_r = my_r / rho_r

    # Pressure
    p_l = (gamma - 1) * (
        E_l - 0.5 * (mx_l**2 + my_l**2) / rho_l
    )

    p_r = (gamma - 1) * (
        E_r - 0.5 * (mx_r**2 + my_r**2) / rho_r
    )

    # Speed of sound
    c_l = (gamma * p_l / rho_l) ** 0.5
    c_r = (gamma * p_r / rho_r) ** 0.5

    # Wave speeds
    S_l = np.minimum(
        u_l - c_l,
        u_r - c_r
    )

    S_r = np.maximum(
        u_l + c_l,
        u_r + c_r
    )

    # Contact wave speed
    denominator = (
        rho_l * (S_l - u_l)
        - rho_r * (S_r - u_r)
    )

    denominator = np.where(
        np.abs(denominator) < 1e-12,
        1e-12,
        denominator
    )

    S_m = (
        p_r - p_l
        + rho_l * u_l * (S_l - u_l)
        - rho_r * u_r * (S_r - u_r)
    ) / denominator

    # Physical fluxes
    F_l = np.array([
        mx_l,
        mx_l * u_l + p_l,
        mx_l * v_l,
        u_l * (E_l + p_l)
    ], dtype=np.float64)

    F_r = np.array([
        mx_r,
        mx_r * u_r + p_r,
        mx_r * v_r,
        u_r * (E_r + p_r)
    ], dtype=np.float64)

    # Left star density
    denominator_l = S_l - S_m

    denominator_l = np.where(
        np.abs(denominator_l) < 1e-12,
        1e-12,
        denominator_l
    )

    rho_star_l = rho_l * (
        (S_l - u_l) / denominator_l
    )

    # Left star energy
    E_star_l = (
        (S_l - u_l) * E_l
        - p_l * u_l
        + p_l * S_m
    ) / denominator_l

    # Left star state
    U_star_l = np.array([
        rho_star_l,
        rho_star_l * S_m,
        rho_star_l * v_l,
        E_star_l
    ], dtype=np.float64)

    # Right star density
    denominator_r = S_r - S_m

    denominator_r = np.where(
        np.abs(denominator_r) < 1e-12,
        1e-12,
        denominator_r
    )

    rho_star_r = rho_r * (
        (S_r - u_r) / denominator_r
    )

    # Right star energy
    E_star_r = (
        (S_r - u_r) * E_r
        - p_r * u_r
        + p_r * S_m
    ) / denominator_r

    # Right star state
    U_star_r = np.array([
        rho_star_r,
        rho_star_r * S_m,
        rho_star_r * v_r,
        E_star_r
    ], dtype=np.float64)

    # HLLC star fluxes
    F_star_l = F_l + S_l * (U_star_l - left)
    F_star_r = F_r + S_r * (U_star_r - right)

    # Select correct flux
    result = np.where(
        S_l >= 0,
        F_l,
        np.where(
            S_m >= 0,
            F_star_l,
            np.where(
                S_r > 0,
                F_star_r,
                F_r
            )
        )
    )

    return result

def hllc_y(bottom, top, gamma):
    rho_b, mx_b, my_b, E_b = bottom
    rho_t, mx_t, my_t, E_t = top

    # Primitive variables
    u_b = mx_b / rho_b
    v_b = my_b / rho_b

    u_t = mx_t / rho_t
    v_t = my_t / rho_t

    # Pressure
    p_b = (gamma - 1) * (
        E_b - 0.5 * (mx_b**2 + my_b**2) / rho_b
    )

    p_t = (gamma - 1) * (
        E_t - 0.5 * (mx_t**2 + my_t**2) / rho_t
    )

    # Speed of sound
    c_b = (gamma * p_b / rho_b) ** 0.5
    c_t = (gamma * p_t / rho_t) ** 0.5

    # Wave speeds
    S_l = np.minimum(
        v_b - c_b,
        v_t - c_t
    )

    S_r = np.maximum(
        v_b + c_b,
        v_t + c_t
    )

    # Contact wave speed
    denominator = (
        rho_b * (S_l - v_b)
        - rho_t * (S_r - v_t)
    )

    denominator = np.where(
        np.abs(denominator) < 1e-12,
        1e-12,
        denominator
    )

    S_m = (
        p_t - p_b
        + rho_b * v_b * (S_l - v_b)
        - rho_t * v_t * (S_r - v_t)
    ) / denominator

    # Physical fluxes
    G_b = np.array([
        my_b,
        my_b * u_b,
        my_b * v_b + p_b,
        v_b * (E_b + p_b)
    ], dtype=np.float64)

    G_t = np.array([
        my_t,
        my_t * u_t,
        my_t * v_t + p_t,
        v_t * (E_t + p_t)
    ], dtype=np.float64)

    # Bottom star density
    denominator_b = S_l - S_m

    denominator_b = np.where(
        np.abs(denominator_b) < 1e-12,
        1e-12,
        denominator_b
    )

    rho_star_b = rho_b * (
        (S_l - v_b) / denominator_b
    )

    # Bottom star energy
    E_star_b = (
        (S_l - v_b) * E_b
        - p_b * v_b
        + p_b * S_m
    ) / denominator_b

    # Bottom star state
    U_star_b = np.array([
        rho_star_b,
        rho_star_b * u_b,
        rho_star_b * S_m,
        E_star_b
    ], dtype=np.float64)

    # Top star density
    denominator_t = S_r - S_m

    denominator_t = np.where(
        np.abs(denominator_t) < 1e-12,
        1e-12,
        denominator_t
    )

    rho_star_t = rho_t * (
        (S_r - v_t) / denominator_t
    )

    # Top star energy
    E_star_t = (
        (S_r - v_t) * E_t
        - p_t * v_t
        + p_t * S_m
    ) / denominator_t

    # Top star state
    U_star_t = np.array([
        rho_star_t,
        rho_star_t * u_t,
        rho_star_t * S_m,
        E_star_t
    ], dtype=np.float64)

    # HLLC star fluxes
    G_star_b = G_b + S_l * (U_star_b - bottom)
    G_star_t = G_t + S_r * (U_star_t - top)

    # Select correct flux
    result = np.where(
        S_l >= 0,
        G_b,
        np.where(
            S_m >= 0,
            G_star_b,
            np.where(
                S_r > 0,
                G_star_t,
                G_t
            )
        )
    )

    return result


def viscous_flux(state, dx, dy, k, mu):
    """Return the 2D compressible Navier-Stokes viscous fluxes for the
    left/right and bottom/top cell interfaces.

    The solver expects values shaped like the interior conservative state arrays:
    (4, height-2, width-2). The fluxes are computed in the standard finite-volume
    form using the viscous stress tensor and conductive heat flux.
    """
    gamma = state.config.gamma
    gas_constant = state.config.gas_constant

    def safe_divide(a, b):
        return np.divide(
            a,
            b,
            out=np.zeros_like(a, dtype=np.float64),
            where=np.abs(b) > 1e-12
        )

    y_slice = slice(1, state.height - 1)
    x_slice = slice(1, state.width - 1)

    rho_c = np.asarray(state.density[y_slice, x_slice], dtype=np.float64)
    rho_l = np.asarray(state.density[y_slice, :-2], dtype=np.float64)
    rho_r = np.asarray(state.density[y_slice, 2:], dtype=np.float64)
    rho_b = np.asarray(state.density[:-2, x_slice], dtype=np.float64)
    rho_t = np.asarray(state.density[2:, x_slice], dtype=np.float64)

    m_x_c = np.asarray(state.momentum_x[y_slice, x_slice], dtype=np.float64)
    m_x_l = np.asarray(state.momentum_x[y_slice, :-2], dtype=np.float64)
    m_x_r = np.asarray(state.momentum_x[y_slice, 2:], dtype=np.float64)
    m_x_b = np.asarray(state.momentum_x[:-2, x_slice], dtype=np.float64)
    m_x_t = np.asarray(state.momentum_x[2:, x_slice], dtype=np.float64)

    m_y_c = np.asarray(state.momentum_y[y_slice, x_slice], dtype=np.float64)
    m_y_l = np.asarray(state.momentum_y[y_slice, :-2], dtype=np.float64)
    m_y_r = np.asarray(state.momentum_y[y_slice, 2:], dtype=np.float64)
    m_y_b = np.asarray(state.momentum_y[:-2, x_slice], dtype=np.float64)
    m_y_t = np.asarray(state.momentum_y[2:, x_slice], dtype=np.float64)

    e_c = np.asarray(state.energy[y_slice, x_slice], dtype=np.float64)
    e_l = np.asarray(state.energy[y_slice, :-2], dtype=np.float64)
    e_r = np.asarray(state.energy[y_slice, 2:], dtype=np.float64)
    e_b = np.asarray(state.energy[:-2, x_slice], dtype=np.float64)
    e_t = np.asarray(state.energy[2:, x_slice], dtype=np.float64)

    u_c = safe_divide(m_x_c, rho_c)
    u_l = safe_divide(m_x_l, rho_l)
    u_r = safe_divide(m_x_r, rho_r)
    u_b = safe_divide(m_x_b, rho_b)
    u_t = safe_divide(m_x_t, rho_t)

    v_c = safe_divide(m_y_c, rho_c)
    v_l = safe_divide(m_y_l, rho_l)
    v_r = safe_divide(m_y_r, rho_r)
    v_b = safe_divide(m_y_b, rho_b)
    v_t = safe_divide(m_y_t, rho_t)

    p_c = (gamma - 1.0) * (e_c - 0.5 * (m_x_c**2 + m_y_c**2) / rho_c)
    p_l = (gamma - 1.0) * (e_l - 0.5 * (m_x_l**2 + m_y_l**2) / rho_l)
    p_r = (gamma - 1.0) * (e_r - 0.5 * (m_x_r**2 + m_y_r**2) / rho_r)
    p_b = (gamma - 1.0) * (e_b - 0.5 * (m_x_b**2 + m_y_b**2) / rho_b)
    p_t = (gamma - 1.0) * (e_t - 0.5 * (m_x_t**2 + m_y_t**2) / rho_t)

    T_c = p_c / (rho_c * gas_constant)
    T_l = p_l / (rho_l * gas_constant)
    T_r = p_r / (rho_r * gas_constant)
    T_b = p_b / (rho_b * gas_constant)
    T_t = p_t / (rho_t * gas_constant)

    # Gradients on the cell-centered stencil.
    du_dx_c = (u_r - u_l) / (2.0 * dx)
    dv_dx_c = (v_r - v_l) / (2.0 * dx)
    du_dy_c = (u_t - u_b) / (2.0 * dy)
    dv_dy_c = (v_t - v_b) / (2.0 * dy)

    dT_dx_c = (T_r - T_l) / (2.0 * dx)
    dT_dy_c = (T_t - T_b) / (2.0 * dy)

    # One-sided gradients at the left/right faces.
    du_dx_left = (u_c - u_l) / dx
    du_dx_right = (u_r - u_c) / dx
    dv_dx_left = (v_c - v_l) / dx
    dv_dx_right = (v_r - v_c) / dx

    dT_dx_left = (T_c - T_l) / dx
    dT_dx_right = (T_r - T_c) / dx

    # One-sided gradients at the bottom/top faces.
    du_dy_bottom = (u_c - u_b) / dy
    du_dy_top = (u_t - u_c) / dy
    dv_dy_bottom = (v_c - v_b) / dy
    dv_dy_top = (v_t - v_c) / dy

    dT_dy_bottom = (T_c - T_b) / dy
    dT_dy_top = (T_t - T_c) / dy

    # Newtonian viscous stress tensor.
    div_u_left = du_dx_left + dv_dy_c
    div_u_right = du_dx_right + dv_dy_c
    div_u_bottom = du_dx_c + dv_dy_bottom
    div_u_top = du_dx_c + dv_dy_top

    tau_xx_left = mu * (2.0 * du_dx_left - (2.0 / 3.0) * div_u_left)
    tau_xx_right = mu * (2.0 * du_dx_right - (2.0 / 3.0) * div_u_right)
    tau_yy_bottom = mu * (2.0 * dv_dy_bottom - (2.0 / 3.0) * div_u_bottom)
    tau_yy_top = mu * (2.0 * dv_dy_top - (2.0 / 3.0) * div_u_top)

    tau_xy_left = mu * (du_dy_c + dv_dx_left)
    tau_xy_right = mu * (du_dy_c + dv_dx_right)
    tau_xy_bottom = mu * (du_dy_bottom + dv_dx_c)
    tau_xy_top = mu * (du_dy_top + dv_dx_c)

    u_face_left = 0.5 * (u_c + u_l)
    v_face_left = 0.5 * (v_c + v_l)
    u_face_right = 0.5 * (u_r + u_c)
    v_face_right = 0.5 * (v_r + v_c)

    u_face_bottom = 0.5 * (u_c + u_b)
    v_face_bottom = 0.5 * (v_c + v_b)
    u_face_top = 0.5 * (u_t + u_c)
    v_face_top = 0.5 * (v_t + v_c)

    F_viscous_left = np.stack([
        np.zeros_like(rho_c, dtype=np.float64),
        tau_xx_left,
        tau_xy_left,
        u_face_left * tau_xx_left + v_face_left * tau_xy_left - k * dT_dx_left
    ], axis=0)

    F_viscous_right = np.stack([
        np.zeros_like(rho_c, dtype=np.float64),
        tau_xx_right,
        tau_xy_right,
        u_face_right * tau_xx_right + v_face_right * tau_xy_right - k * dT_dx_right
    ], axis=0)

    G_viscous_bottom = np.stack([
        np.zeros_like(rho_c, dtype=np.float64),
        tau_xy_bottom,
        tau_yy_bottom,
        u_face_bottom * tau_xy_bottom + v_face_bottom * tau_yy_bottom - k * dT_dy_bottom
    ], axis=0)

    G_viscous_top = np.stack([
        np.zeros_like(rho_c, dtype=np.float64),
        tau_xy_top,
        tau_yy_top,
        u_face_top * tau_xy_top + v_face_top * tau_yy_top - k * dT_dy_top
    ], axis=0)

    return F_viscous_left, F_viscous_right, G_viscous_bottom, G_viscous_top



