import tkinter as tk
from tkinter import colorchooser

from .config import Config
from ..constants import *
from ..custom_shapes import SHAPES

class GuiRenderer:
    def __init__(self, width, height, config: Config = Config()):

        self.width = width
        self.height = height
        self.config = config

        self.paused = self.config.paused

        self.running = True
        self.shape_has_changed = False

        # -------------------------
        # Colours
        # -------------------------

        self.bg = "#1e1e1e"
        self.panel = "#252526"
        self.button = "#333333"
        self.button_hover = "#444444"

        self.text = "#ffffff"
        self.secondary_text = "#aaaaaa"
        self.accent = "#4fc3f7"

        # -------------------------
        # Main window
        # -------------------------

        self.root = tk.Tk()
        self.root.title("2D CFD Simulator")
        self.root.configure(bg=self.bg)

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

        # -------------------------
        # Title
        # -------------------------

        title = tk.Label(
            self.root,
            text="2D CFD SIMULATOR",
            bg=self.bg,
            fg=self.text,
            font=("Segoe UI", 16, "bold")
        )

        title.pack(pady=(15, 10))

        # -------------------------
        # UI container
        # -------------------------

        self.ui = tk.Frame(
            self.root,
            bg=self.bg,
            width=500
        )

        self.ui.pack()

        # -------------------------
        # Columns
        # -------------------------

        self.left_column = tk.Frame(
            self.ui,
            bg=self.bg,
            width=250,
            padx=0,
            pady=4
        )

        self.left_column.pack(
            side="left",
            fill="y",
            anchor="n",
            padx=(0, 8)
        )

        self.right_column = tk.Frame(
            self.ui,
            bg=self.bg,
            width=250,
            padx=0,
            pady=4
        )

        self.right_column.pack(
            side="left",
            fill="y",
            anchor="n",
            padx=(0, 0)
        )

        # -------------------------
        # Sections
        # -------------------------

        self.create_simulation_section(self.left_column)
        self.create_physics_section(self.left_column)
        self.create_current_cell_section(self.left_column)

        self.create_visualisation_section(self.right_column)
        self.create_inflow_section(self.right_column)
        self.create_shape_section(self.right_column)

        self.update_inflow()

    # ==================================================
    # Section helper
    # ==================================================

    def create_section(self, parent, title):

        frame = tk.Frame(
            parent,
            bg=self.panel,
            width=250,
            padx=15,
            pady=10
        )

        frame.pack(
            fill="x",
            padx=0,
            pady=(0, 10)
        )

        label = tk.Label(
            frame,
            text=title,
            bg=self.panel,
            fg=self.accent,
            font=("Segoe UI", 10, "bold")
        )

        label.pack(
            anchor="w",
            pady=(0, 8)
        )

        return frame

    # ==================================================
    # Simulation
    # ==================================================

    def create_simulation_section(self, parent):

        frame = self.create_section(
            parent,
            "SIMULATION"
        )

        button_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        button_frame.pack(
            anchor="w",
            pady=(0, 10)
        )

        self.pause_button = self.create_button(
            button_frame,
            "PAUSE",
            self.pause
        )

        self.reset_button = self.create_button(
            button_frame,
            "RESET",
            self.reset
        )

        self.step_button = self.create_button(
            button_frame,
            "STEP",
            self.step
        )

        # dt
        dt_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        dt_frame.pack(
            fill="x"
        )

        tk.Label(
            dt_frame,
            text="Timestep (dt)",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(
            side="left"
        )

        self.dt_entry = tk.Entry(
            dt_frame,
            width=10,
            bg=self.button,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9)
        )

        self.dt_entry.insert(0, str(DEFAULT_DT))

        self.dt_entry.pack(
            side="right"
        )

        # sim speed
        sim_speed_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        sim_speed_frame.pack(
            fill="x"
        )

        tk.Label(
            sim_speed_frame,
            text="Simulation speed",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(
            side="left"
        )

        self.sim_speed_entry = tk.Entry(
            sim_speed_frame,
            width=10,
            bg=self.button,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9)
        )

        self.sim_speed_entry.insert(0, str(DEFAULT_SIM_SPEED))

        self.sim_speed_entry.pack(
            side="right"
        )

        self.dt_entry.bind(
            "<KeyRelease>",
            self.update_config
        )

        self.sim_speed_entry.bind(
            "<KeyRelease>",
            self.update_config
        )

    # ==================================================
    # Visualisation
    # ==================================================

    def create_visualisation_section(self, parent):

        frame = self.create_section(
            parent,
            "VISUALISATION"
        )

        # Field selection
        field_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        field_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        tk.Label(
            field_frame,
            text="Field",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.field = tk.StringVar(
            value=DEFAULT_FIELD
        )

        self.field_menu = tk.OptionMenu(
            field_frame,
            self.field,
            *FIELD_MENU_OPTIONS
        )

        self.field_menu.config(
            bg=self.button,
            fg=self.text,
            activebackground=self.button_hover,
            activeforeground=self.text,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            font=("Segoe UI", 9)
        )

        self.field_menu["menu"].config(
            bg=self.button,
            fg=self.text,
            activebackground=self.button_hover,
            activeforeground=self.text
        )

        self.field_menu.pack(side="right")

        # Colour selection
        self.colour_min = DEFAULT_COLOUR_MIN
        self.colour_max = DEFAULT_COLOUR_MAX

        self.colour_min_value = DEFAULT_MIN_COLOUR_VALUE
        self.colour_max_value = DEFAULT_MAX_COLOUR_VALUE


        # Minimum colour
        colour_min_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        colour_min_frame.pack(
            fill="x",
            pady=(0, 8)
        )

        tk.Label(
            colour_min_frame,
            text="Minimum colour",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.colour_min_button = tk.Button(
            colour_min_frame,
            bg=self.colour_min,
            activebackground=self.colour_min,
            relief="flat",
            borderwidth=0,
            width=8,
            command=self.choose_min_colour
        )

        self.colour_min_button.pack(
            side="left",
            padx=(10, 10)
        )

        tk.Label(
            colour_min_frame,
            text="Value",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.colour_min_entry = tk.Entry(
            colour_min_frame,
            width=8,
            bg=self.button,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9)
        )

        self.colour_min_entry.insert(
            0,
            str(self.colour_min_value)
        )

        self.colour_min_entry.pack(
            side="right"
        )


        # Maximum colour
        colour_max_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        colour_max_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        tk.Label(
            colour_max_frame,
            text="Maximum colour",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.colour_max_button = tk.Button(
            colour_max_frame,
            bg=self.colour_max,
            activebackground=self.colour_max,
            relief="flat",
            borderwidth=0,
            width=8,
            command=self.choose_max_colour
        )

        self.colour_max_button.pack(
            side="left",
            padx=(10, 10)
        )

        tk.Label(
            colour_max_frame,
            text="Value",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.colour_max_entry = tk.Entry(
            colour_max_frame,
            width=8,
            bg=self.button,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9)
        )

        self.colour_max_entry.insert(
            0,
            str(self.colour_max_value)
        )

        self.colour_max_entry.pack(
            side="right"
        )

        # Auto colour scale
        self.auto_colour_scale = tk.BooleanVar(
            value=DEFAULT_AUTO_COLOUR_SCALE
        )

        self.auto_colour_check = tk.Checkbutton(
            frame,
            text="Auto colour scale",
            variable=self.auto_colour_scale,
            bg=self.panel,
            fg=self.text,
            activebackground=self.panel,
            activeforeground=self.text,
            selectcolor=self.button,
            font=("Segoe UI", 9),
            relief="flat",
            borderwidth=0
        )

        self.auto_colour_check.pack(
            anchor="w"
        )

        # Auto value scale
        self.auto_value_scale = tk.BooleanVar(
            value=DEFAULT_AUTO_VALUE_SCALE
        )

        self.auto_value_check = tk.Checkbutton(
            frame,
            text="Auto value scale",
            variable=self.auto_value_scale,
            bg=self.panel,
            fg=self.text,
            activebackground=self.panel,
            activeforeground=self.text,
            selectcolor=self.button,
            font=("Segoe UI", 9),
            relief="flat",
            borderwidth=0
        )

        self.auto_value_check.pack(
            anchor="w",
            pady=(0, 10)
        )

        # Vector Field selection
        vector_frame = tk.Frame(
            frame,
            bg=self.panel
        )
        vector_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        tk.Label(
            vector_frame,
            text="Vector Field",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.vector = tk.StringVar(
            value=DEFAULT_VECTOR_FIELD
        )

        self.vector_menu = tk.OptionMenu(
            vector_frame,
            self.vector,
            *VECTOR_FIELD_MENU_OPTIONS
        )

        self.vector_menu.config(
            bg=self.button,
            fg=self.text,
            activebackground=self.button_hover,
            activeforeground=self.text,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            font=("Segoe UI", 9)
        )

        self.vector_menu["menu"].config(
            bg=self.button,
            fg=self.text,
            activebackground=self.button_hover,
            activeforeground=self.text
        )

        self.vector_menu.pack(side="right")

        # Vector spacing
        spacing_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        spacing_frame.pack(
            fill="x",
            pady=(0, 8)
        )

        tk.Label(
            spacing_frame,
            text="Vector spacing",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.vector_spacing_entry = tk.Entry(
            spacing_frame,
            width=10,
            bg=self.button,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9)
        )

        self.vector_spacing_entry.insert(0, str(DEFAULT_VECTOR_SPACING))

        self.vector_spacing_entry.pack(
            side="right"
        )


        # Vector scale
        scale_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        scale_frame.pack(
            fill="x"
        )

        tk.Label(
            scale_frame,
            text="Vector scale",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.vector_scale_entry = tk.Entry(
            scale_frame,
            width=10,
            bg=self.button,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9)
        )

        self.vector_scale_entry.insert(0, str(DEFAULT_VECTOR_SCALE))

        self.vector_scale_entry.pack(
            side="right"
        )

        self.field.trace_add(
            "write",
            self.update_config
        )

        self.colour_min_entry.bind(
            "<KeyRelease>",
            self.update_config
        )

        self.colour_max_entry.bind(
            "<KeyRelease>",
            self.update_config
        )

        self.auto_colour_scale.trace_add(
            "write",
            self.update_config
        )

        self.auto_value_scale.trace_add(
            "write",
            self.update_config
        )

        self.vector.trace_add(
            "write",
            self.update_config
        )

        self.vector_spacing_entry.bind(
            "<KeyRelease>",
            self.update_config
        )

        self.vector_scale_entry.bind(
            "<KeyRelease>",
            self.update_config
        )

    def choose_min_colour(self):
        colour = colorchooser.askcolor(
            color=self.colour_min,
            title="Choose minimum colour"
        )

        if colour[1] is not None:
            self.colour_min = colour[1]
            self.colour_min_button.config(
                bg=self.colour_min,
                activebackground=self.colour_min
            )

            self.update_config()

    def choose_max_colour(self):
        colour = colorchooser.askcolor(
            color=self.colour_max,
            title="Choose maximum colour"
        )

        if colour[1] is not None:
            self.colour_max = colour[1]
            self.colour_max_button.config(
                bg=self.colour_max,
                activebackground=self.colour_max
            )

            self.update_config()

    # ==================================================
    # Physics
    # ==================================================

    def create_physics_section(self, parent):

        frame = self.create_section(
            parent,
            "PHYSICS"
        )

        # Equation set
        equation_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        equation_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        tk.Label(
            equation_frame,
            text="Equation set",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.equation_set = tk.StringVar(
            value=DEFAULT_EQUATION_SET
        )

        self.equation_menu = tk.OptionMenu(
            equation_frame,
            self.equation_set,
            *EQUATION_MENU_OPTIONS
        )

        self.equation_menu.config(
            bg=self.button,
            fg=self.text,
            activebackground=self.button_hover,
            activeforeground=self.text,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            font=("Segoe UI", 9)
        )

        self.equation_menu["menu"].config(
            bg=self.button,
            fg=self.text,
            activebackground=self.button_hover,
            activeforeground=self.text
        )

        self.equation_menu.pack(side="right")

        # Fluxes

        flux_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        flux_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        tk.Label(
            flux_frame,
            text="Flux",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.flux_set = tk.StringVar(
            value=DEFAULT_FLUX_METHOD
        )

        self.flux_menu = tk.OptionMenu(
            flux_frame,
            self.flux_set,
            *FLUX_MENU_OPTIONS
        )

        self.flux_menu.config(
            bg=self.button,
            fg=self.text,
            activebackground=self.button_hover,
            activeforeground=self.text,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            font=("Segoe UI", 9)
        )

        self.flux_menu["menu"].config(
            bg=self.button,
            fg=self.text,
            activebackground=self.button_hover,
            activeforeground=self.text
        )

        self.flux_menu.pack(side="right")        

        # Gamma
        gamma_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        gamma_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        tk.Label(
            gamma_frame,
            text="Specific heat ratio (γ)",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.gamma_entry = tk.Entry(
            gamma_frame,
            width=8,
            bg=self.button,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9)
        )

        self.gamma_entry.insert(0, str(DEFAULT_GAMMA))

        self.gamma_entry.pack(side="right")

        # Dynamic viscosity
        dynamic_viscosity_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        dynamic_viscosity_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        tk.Label(
            dynamic_viscosity_frame,
            text="Dynamic viscosity (μ)",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.dynamic_viscosity_entry = tk.Entry(
            dynamic_viscosity_frame,
            width=8,
            bg=self.button,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9)
        )

        self.dynamic_viscosity_entry.insert(
            0,
            str(DEFAULT_DYNAMIC_VISCOSITY)
        )

        self.dynamic_viscosity_entry.pack(side="right")


        # Thermal conductivity
        thermal_conductivity_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        thermal_conductivity_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        tk.Label(
            thermal_conductivity_frame,
            text="Thermal conductivity (k)",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.thermal_conductivity_entry = tk.Entry(
            thermal_conductivity_frame,
            width=8,
            bg=self.button,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9)
        )

        self.thermal_conductivity_entry.insert(
            0,
            str(DEFAULT_THERMAL_CONDUCTIVITY)
        )

        self.thermal_conductivity_entry.pack(side="right")


        # Gas Constant
        gas_constant_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        gas_constant_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        tk.Label(
            gas_constant_frame,
            text="Gas Constant (R)",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.gas_constant_entry = tk.Entry(
            gas_constant_frame,
            width=8,
            bg=self.button,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9)
        )

        self.gas_constant_entry.insert(
            0,
            str(DEFAULT_GAS_CONSTANT)
        )

        self.gas_constant_entry.pack(side="right")


        # CFL number
        cfl_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        cfl_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        tk.Label(
            cfl_frame,
            text="CFL number",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.cfl_label = tk.Label(
            cfl_frame,
            text=f"{self.config.cfl_number:.3f}",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        )

        self.cfl_label.pack(side="right")
        
        self.gamma_entry.bind(
            "<KeyRelease>",
            self.update_inflow
        )

        self.equation_set.trace_add(
            "write",
            self.update_config
        )

        self.flux_set.trace_add(
            "write",
            self.update_config
        )

        self.dynamic_viscosity_entry.bind(
            "write",
            self.update_config
        )

        self.thermal_conductivity_entry.bind(
            "write",
            self.update_config
        )

        self.gas_constant_entry.bind(
            "write",
            self.update_config
        )

    def update_cfl_number(self):
        self.cfl_label.config(
            text=f"{self.config.cfl_number:.{CFL_DECIMAL_PLACES}f}"
        )

    # ==================================================
    # Boundary conditions
    # ==================================================

    def create_boundary_section(self, parent):

        frame = self.create_section(
            parent,
            "BOUNDARY CONDITIONS"
        )

        tk.Label(
            frame,
            text="Left",
            bg=self.panel,
            fg=self.text
        ).pack(anchor="w")

    # ==================================================
    # Inflow conditions
    # ==================================================

    def create_inflow_section(self, parent):

        frame = self.create_section(
            parent,
            "INFLOW"
        )

        # Density
        density_frame = tk.Frame(
            frame,
            bg=self.panel
        )
        density_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            density_frame,
            text="Density (ρ)",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.density_entry = tk.Entry(
            density_frame,
            width=10,
            bg=self.button,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9)
        )
        self.density_entry.insert(0, str(DEFAULT_DENSITY_INF))
        self.density_entry.pack(side="right")

        # X velocity
        vx_frame = tk.Frame(
            frame,
            bg=self.panel
        )
        vx_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            vx_frame,
            text="X velocity (u)",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.vx_entry = tk.Entry(
            vx_frame,
            width=10,
            bg=self.button,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9)
        )
        self.vx_entry.insert(0, str(DEFAULT_VELOCITY_X_INF))
        self.vx_entry.pack(side="right")

        # Y velocity
        vy_frame = tk.Frame(
            frame,
            bg=self.panel
        )
        vy_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            vy_frame,
            text="Y velocity (v)",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.vy_entry = tk.Entry(
            vy_frame,
            width=10,
            bg=self.button,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9)
        )
        self.vy_entry.insert(0, str(DEFAULT_VELOCITY_Y_INF))
        self.vy_entry.pack(side="right")

        # Temperature
        temperature_frame = tk.Frame(
            frame,
            bg=self.panel
        )
        temperature_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            temperature_frame,
            text="Temperature (T)",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.temperature_entry = tk.Entry(
            temperature_frame,
            width=10,
            bg=self.button,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9)
        )
        self.temperature_entry.insert(0, str(DEFAULT_TEMPERATURE_INF))
        self.temperature_entry.pack(side="right")

        # Energy - read only
        energy_frame = tk.Frame(
            frame,
            bg=self.panel
        )
        energy_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            energy_frame,
            text="Energy (E)",
            bg=self.panel,
            fg=self.secondary_text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.energy_value = tk.Label(
            energy_frame,
            text="1.00",
            bg=self.panel,
            fg=self.secondary_text,
            font=("Segoe UI", 9)
        )
        self.energy_value.pack(side="right")

        # Pressure - read only
        pressure_frame = tk.Frame(
            frame,
            bg=self.panel
        )
        pressure_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            pressure_frame,
            text="Pressure (p)",
            bg=self.panel,
            fg=self.secondary_text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.pressure_value = tk.Label(
            pressure_frame,
            text="1.00",
            bg=self.panel,
            fg=self.secondary_text,
            font=("Segoe UI", 9)
        )
        self.pressure_value.pack(side="right")

        # Mach number - read only
        mach_frame = tk.Frame(
            frame,
            bg=self.panel
        )
        mach_frame.pack(fill="x")

        tk.Label(
            mach_frame,
            text="Mach number",
            bg=self.panel,
            fg=self.secondary_text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.mach_value = tk.Label(
            mach_frame,
            text="0.00",
            bg=self.panel,
            fg=self.accent,
            font=("Segoe UI", 9, "bold")
        )
        self.mach_value.pack(side="right")

        self.density_entry.bind(
            "<KeyRelease>",
            lambda e: self.update_inflow()
        )

        self.vx_entry.bind(
            "<KeyRelease>",
            lambda e: self.update_inflow()
        )

        self.vy_entry.bind(
            "<KeyRelease>",
            lambda e: self.update_inflow()
        )

        self.temperature_entry.bind(
            "<KeyRelease>",
            lambda e: self.update_inflow()
        )

    def update_inflow(self, *args):

        try:
            rho = float(self.density_entry.get())
            vx = float(self.vx_entry.get())
            vy = float(self.vy_entry.get())
            T = float(self.temperature_entry.get())
            R = float(self.gas_constant_entry.get())
            gamma = float(self.gamma_entry.get())

            # Velocities are entered directly as primitive variables.
            u = vx
            v = vy

            # Internal energy
            E = (
                rho * R * T / (gamma - 1)
                + 0.5 * rho * (u**2 + v**2)
            )

            # Pressure
            pressure = rho * R * T

            # Speed of sound
            if pressure > 0 and rho > 0:
                c = (gamma * pressure / rho) ** 0.5

                a = (gamma * R * T) ** 0.5
                mach = (u**2 + v**2) ** 0.5
                mach /= a

                self.energy_value.config(
                    text=f"{E:.3f}"
                )

                self.pressure_value.config(
                    text=f"{pressure:.3f}"
                )

                self.mach_value.config(
                    text=f"{mach:.3f}"
                )

            else:
                self.pressure_value.config(
                    text="Invalid"
                )

                self.mach_value.config(
                    text="Invalid"
                )

            self.update_config()
            
        except (ValueError, ZeroDivisionError):
            self.pressure_value.config(
                text="---"
            )

            self.mach_value.config(
                text="---"
            )

    # ==================================================
    # Shapes
    # ==================================================

    def create_shape_section(self, parent):

        frame = self.create_section(
            parent,
            "SHAPE"
        )
        
        # Shape selection
        shape_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        shape_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        tk.Label(
            shape_frame,
            text="Shape",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.shape = tk.StringVar(
            value=DEFAULT_SHAPE
        )

        self.shape_menu = tk.OptionMenu(
            shape_frame,
            self.shape,
            *SHAPES.keys()
        )

        self.shape_menu.config(
            bg=self.button,
            fg=self.text,
            activebackground=self.button_hover,
            activeforeground=self.text,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            font=("Segoe UI", 9)
        )

        self.shape_menu["menu"].config(
            bg=self.button,
            fg=self.text,
            activebackground=self.button_hover,
            activeforeground=self.text
        )

        self.shape_menu.pack(
            side="right"
        )


        # X offset
        x_offset_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        x_offset_frame.pack(
            fill="x",
            pady=(0, 8)
        )

        tk.Label(
            x_offset_frame,
            text="X offset",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.x_offset_entry = tk.Entry(
            x_offset_frame,
            width=10,
            bg=self.button,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9)
        )

        self.x_offset_entry.insert(
            0,
            str(DEFAULT_X_OFFSET)
        )

        self.x_offset_entry.pack(
            side="right"
        )


        # Y offset
        y_offset_frame = tk.Frame(
            frame,
            bg=self.panel
        )

        y_offset_frame.pack(
            fill="x"
        )

        tk.Label(
            y_offset_frame,
            text="Y offset",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.y_offset_entry = tk.Entry(
            y_offset_frame,
            width=10,
            bg=self.button,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9)
        )

        self.y_offset_entry.insert(
            0,
            str(DEFAULT_Y_OFFSET)
        )

        self.y_offset_entry.pack(
            side="right"
        )


        # Configuration bindings
        self.shape.trace_add(
            "write",
            self.update_shape
        )

        self.x_offset_entry.bind(
            "<KeyRelease>",
            self.update_shape
        )

        self.y_offset_entry.bind(
            "<KeyRelease>",
            self.update_shape
        )

    def update_shape(self, *args):
        self.shape_has_changed = True
        self.update_config()

    # ==================================================
    # Current cell
    # ==================================================

    def create_current_cell_section(self, parent):
        frame = self.create_section(
            parent,
            "CURRENT CELL"
        )

        # Cell
        cell_frame = tk.Frame(
            frame,
            bg=self.panel
        )
        cell_frame.pack(
            fill="x",
            pady=(0, 8)
        )

        tk.Label(
            cell_frame,
            text="Cell",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.current_cell_label = tk.Label(
            cell_frame,
            text="(0, 0)",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        )
        self.current_cell_label.pack(side="right")


        # Density
        density_frame = tk.Frame(
            frame,
            bg=self.panel
        )
        density_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            density_frame,
            text="Density",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.current_density_label = tk.Label(
            density_frame,
            text="0.0000",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        )
        self.current_density_label.pack(side="right")


        # Pressure
        pressure_frame = tk.Frame(
            frame,
            bg=self.panel
        )
        pressure_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            pressure_frame,
            text="Pressure",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.current_pressure_label = tk.Label(
            pressure_frame,
            text="0.0000",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        )
        self.current_pressure_label.pack(side="right")


        # Velocity
        velocity_frame = tk.Frame(
            frame,
            bg=self.panel
        )
        velocity_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            velocity_frame,
            text="Velocity",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.current_velocity_label = tk.Label(
            velocity_frame,
            text="(0.0000, 0.0000)",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        )
        self.current_velocity_label.pack(side="right")

        # Temperature
        temperature_frame = tk.Frame(
            frame,
            bg=self.panel
        )
        temperature_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            temperature_frame,
            text="Temperature",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.current_temperature_label = tk.Label(
            temperature_frame,
            text="0.0000",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        )
        self.current_temperature_label.pack(side="right")

        # Energy
        energy_frame = tk.Frame(
            frame,
            bg=self.panel
        )
        energy_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            energy_frame,
            text="Energy",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.current_energy_label = tk.Label(
            energy_frame,
            text="0.0000",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        )
        self.current_energy_label.pack(side="right")


        # Mach
        mach_frame = tk.Frame(
            frame,
            bg=self.panel
        )
        mach_frame.pack(fill="x")

        tk.Label(
            mach_frame,
            text="Mach",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.current_mach_label = tk.Label(
            mach_frame,
            text="0.0000",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 9)
        )
        self.current_mach_label.pack(side="right")

    def update_cell_display(self):

        if not self.running: return

        self.current_cell_label.config(
            text=str(self.config.current_cell)
        )

        self.current_density_label.config(
            text=f"{self.config.current_density:.4f}"
        )

        self.current_pressure_label.config(
            text=f"{self.config.current_pressure:.4f}"
        )

        self.current_velocity_label.config(
            text=f"({self.config.current_velocity[0]:.4f}, "
                f"{self.config.current_velocity[1]:.4f})"
        )

        self.current_energy_label.config(
            text=f"{self.config.current_energy:.4f}"
        )

        self.current_mach_label.config(
            text=f"{self.config.current_mach:.4f}"
        )

        self.current_temperature_label.config(
            text=f"{self.config.current_temperature:.4f}"
        )

    # ==================================================
    # Buttons
    # ==================================================

    def create_button(self, parent, text, command):

        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=self.button,
            fg=self.text,
            activebackground=self.button_hover,
            activeforeground=self.text,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            borderwidth=0,
            padx=12,
            pady=6,
            cursor="hand2"
        )

        button.pack(
            side="left",
            padx=3
        )

        return button

    # ==================================================
    # Controls
    # ==================================================

    def pause(self):
        self.paused = not self.paused
        self.update_config()

    def reset(self):
        self.config.reset = True

    def step(self):
        self.config.step = True

    # ==================================================
    # Update Config
    # ==================================================
    
    def update_config(self, *args):

        # Simulation
        self.config.paused = self.paused

        # Change text on pause/resume button
        if self.paused:
            self.pause_button.config(text="RESUME")
        else:
            self.pause_button.config(text="PAUSE")

        self.config.dt = float(self.dt_entry.get())
        self.config.sim_speed = int(self.sim_speed_entry.get())

        # Visualisation
        self.config.field = self.field.get()
        self.config.colour_min = self.colour_min
        self.config.colour_max = self.colour_max

        try:
            self.config.colour_min_value = float(self.colour_min_entry.get())
            self.config.colour_max_value = float(self.colour_max_entry.get())
        except ValueError:
            pass   
        
        self.config.auto_colour_scale = self.auto_colour_scale.get()
        self.config.auto_value_scale = self.auto_value_scale.get()
        self.config.vector_field = self.vector.get()
        self.config.vector_spacing = int(self.vector_spacing_entry.get())
        self.config.vector_scale = float(self.vector_scale_entry.get())

        # Physics
        self.config.equation_set = self.equation_set.get()
        self.config.flux_set = self.flux_set.get()
        self.config.gamma = float(self.gamma_entry.get())
        self.config.dynamic_viscosity = float(self.dynamic_viscosity_entry.get())
        self.config.thermal_conductivity = float(self.thermal_conductivity_entry.get())
        self.config.gas_constant = float(self.gas_constant_entry.get())

        # Inflow
        self.config.rho_inf = float(self.density_entry.get())
        self.config.velocity_x_inf = float(self.vx_entry.get())
        self.config.velocity_y_inf = float(self.vy_entry.get())
        self.config.temperature_inf = float(self.temperature_entry.get())
        self.config.energy_inf = float(self.energy_value.cget("text"))
        self.config.pressure_inf = float(self.pressure_value.cget("text"))

        # Shape
        self.config.shape = self.shape.get().upper()
        self.config.x_offset = int(self.x_offset_entry.get())
        self.config.y_offset = int(self.y_offset_entry.get())
        self.config.shape_has_changed = self.shape_has_changed
        self.shape_has_changed = False

    # ==================================================
    # Run
    # ==================================================

    def update(self):
        self.root.update_idletasks()
        self.root.update()

    def run(self):
        self.root.mainloop()

    def close(self):
        if not self.running: return

        self.running = False
        self.root.destroy()