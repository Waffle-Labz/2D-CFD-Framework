import time
from typing import Literal, overload

from .gui.renderer import GuiRenderer

from .sim.renderer import SimRenderer
from .sim.state import State
from .sim.solver import Solver

from .constants import *

# Combines the GUI and Pygame
# Acts as the public-facing interface for the sim
class CFDSimulator:
    def __init__(
        self,
        data_metric_list=None,
        snapshot_exporter=None,
        cell_x_count=CELL_X_COUNT,
        cell_y_count=CELL_Y_COUNT,
        screen_width=SCREEN_WIDTH,
        screen_height=SCREEN_HEIGHT,
        default_shape=DEFAULT_SHAPE,
        vector_spacing=DEFAULT_VECTOR_SPACING
    ):

        self.gui_renderer = GuiRenderer(width=500, height=500)
        self.config = self.gui_renderer.config
        self.config.vector_spacing = vector_spacing

        # Data collection
        if data_metric_list is None:
            data_metric_list = []

        data_metric_list.insert(0, DataMetric.FRAME)
        data_metric_list.insert(1, DataMetric.TIMESTAMP)
        self.data_collection_dict = {i: [] for i in data_metric_list}

        # Create the state
        self.state = State(
            width=cell_x_count,
            height=cell_y_count,
            config=self.config,
            dx=screen_width / cell_x_count,
            dy=screen_height / cell_y_count,
            init_shape=default_shape
        )

        self.solver = Solver(
            screen_width / cell_x_count,
            screen_height / cell_y_count,
            k=self.config.thermal_conductivity,
            mu=self.config.dynamic_viscosity,
            gamma=self.config.gamma,
            R=self.config.gas_constant
        )

        self.sim_renderer = SimRenderer(
            width=screen_width,
            height=screen_height,
            config=self.config,
            solver=self.solver,
            state=self.state,
            current_cell_update_method=self.gui_renderer.update_cell_display,
            cfl_update_method=self.gui_renderer.update_cfl_number,
            data_collection_dict=self.data_collection_dict
        )

        if snapshot_exporter is not None:
            snapshot_exporter.sim_renderer = self.sim_renderer
            self.snapshot_exporter = snapshot_exporter
        else:
            self.snapshot_exporter = None


    def add_shape(self, shape, offset=None):
        self.state.add_shape(shape, offset)

    @overload
    def run(
        self,
        benchmark_mode: Literal[False] = False,
        warmup_frames: int = 20,
        max_frames_to_run: int = 100
    ) -> dict[DataMetric, list]: ...

    @overload
    def run(
        self,
        benchmark_mode: Literal[True],
        warmup_frames: int = 20,
        max_frames_to_run: int = 100
    ) -> tuple[list[float], list[float], list[float]]: ...

    @overload
    def run(
        self,
        benchmark_mode: bool,
        warmup_frames: int = 20,
        max_frames_to_run: int = 100
    ) -> dict[DataMetric, list] | tuple[list[float], list[float], list[float]]: ...

    def run(self, benchmark_mode=False, warmup_frames=20, max_frames_to_run=None):
        if benchmark_mode and max_frames_to_run is not None:
            return self.run_benchmark_mode(warmup_frames, max_frames_to_run)

        frame_num = 0
        # Holds the main loop
        # Each iteration steps the gui and sim 1 frame forward
        while self.gui_renderer.running and self.sim_renderer.running:

            if max_frames_to_run is not None and frame_num > max_frames_to_run:
                break

            # Step the GUI forward
            self.gui_renderer.update()

            # Hook up equation set and flux set to solver
            self.solver.update_method(
                equation_set = self.config.equation_set.lower(),
                flux_set = self.config.flux_set.lower()
            )

            # Step the sim forward
            self.sim_renderer.update(
                dt = self.config.dt,
                config = self.config
            )

            if self.snapshot_exporter is not None:
                self.snapshot_exporter.export_snapshot(frame_num)

            frame_num += 1

        # If either stops running
        self.gui_renderer.close()
        self.sim_renderer.close()
        
        return self.data_collection_dict

    def run_benchmark_mode(self, warmup_frames, max_frames_to_run):
        frame_num = 1

        calc_times = []
        render_times = []
        total_times = []

        # Holds the main loop
        # Each iteration steps the GUI and sim 1 frame forward
        while self.gui_renderer.running and self.sim_renderer.running:

            # Stop after warm-up + benchmark frames
            if frame_num > warmup_frames + max_frames_to_run:
                break

            start_time = time.perf_counter()

            # Step the GUI forward
            self.gui_renderer.update()

            # Hook up equation set and flux set to solver
            self.solver.update_method(
                equation_set=self.config.equation_set.lower(),
                flux_set=self.config.flux_set.lower()
            )

            calc_time = time.perf_counter()

            # Step the sim forward
            self.sim_renderer.update(
                dt=self.config.dt,
                config=self.config
            )

            render_time = time.perf_counter()

            # Only record timings after the warm-up period
            if frame_num > warmup_frames:
                calc_times.append(calc_time - start_time)
                render_times.append(render_time - calc_time)
                total_times.append(render_time - start_time)

            frame_num += 1

        # Always closes windows after running
        self.gui_renderer.close()
        self.sim_renderer.close()

        return calc_times, render_times, total_times
