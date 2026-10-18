"""
CFD Framework — Main Entry Point
===============================

This file demonstrates how to initialise, configure and run a CFD
simulation using the framework.

Run from the project directory:
    python main.py

Edit the configuration section below to customise the simulation.
"""

from pathlib import Path

from CFD import CFDSimulator, DataMetric, export_data, SnapshotExporter
from shape_generators import (
    Airfoil,
    Circle,
    Diamond,
    Ellipse,
    Rectangle,
    RoundedRectangle,
    Wedge,
)


# ============================================================
# 1. SIMULATION CONFIGURATION
# ============================================================

# Select the geometry to simulate.
# Available examples are listed in the geometry section below.
GEOMETRY = "rounded_rectangle"

# Number of simulation frames to execute.
# Increase this for longer simulations.
NUM_FRAMES = 1000

# Directory in which simulation output will be stored.
OUTPUT_DIR = Path("data/geometry") / GEOMETRY

# Enable or disable snapshot export.
# Snapshots are saved as compressed .npz files.
EXPORT_SNAPSHOTS = True

# Save one snapshot every N frames.
SNAPSHOT_FREQUENCY = 100

# Angle of attack, in degrees, for the airfoil example.
ANGLE_OF_ATTACK = 20


# ============================================================
# 2. DATA COLLECTION
# ============================================================

# Select which quantities the simulator should record.
# These metrics are exported to a CSV file after the run.
METRICS = [
    DataMetric.MIN_SPEED,
    DataMetric.MAX_SPEED,
    DataMetric.AVERAGE_SPEED,
    DataMetric.MIN_PRESSURE,
    DataMetric.MAX_PRESSURE,
    DataMetric.AVERAGE_PRESSURE,
    DataMetric.MIN_DENSITY,
    DataMetric.MAX_DENSITY,
    DataMetric.AVERAGE_DENSITY,
    DataMetric.MIN_TEMPERATURE,
    DataMetric.MAX_TEMPERATURE,
    DataMetric.AVERAGE_TEMPERATURE,
    DataMetric.MIN_MACH,
    DataMetric.MAX_MACH,
    DataMetric.AVERAGE_MACH,
    DataMetric.CFL_VALUE,
]


# ============================================================
# 3. INITIALISE THE SIMULATOR
# ============================================================

# The simulator manages the flow field, numerical calculations
# and simulation execution.
#
# A SnapshotExporter periodically saves the simulation state,
# allowing selected frames to be inspected or visualised later.

snapshot_exporter = None

if EXPORT_SNAPSHOTS:
    snapshot_exporter = SnapshotExporter(
        path=str(OUTPUT_DIR / "snapshots"),
        frequency=SNAPSHOT_FREQUENCY,
    )

sim = CFDSimulator(
    METRICS,
    snapshot_exporter=snapshot_exporter,
)


# ============================================================
# 4. ADD GEOMETRY
# ============================================================

# Shapes are added before the simulation starts.
# The offset specifies the position passed to the shape generator.

if GEOMETRY == "circle":
    sim.add_shape(Circle(20), offset=(0, 0))

elif GEOMETRY == "rectangle":
    sim.add_shape(Rectangle(70, 40), offset=(0, 0))

elif GEOMETRY == "rounded_rectangle":
    sim.add_shape(RoundedRectangle(70, 40, 5), offset=(0, 0))

elif GEOMETRY == "ellipse":
    sim.add_shape(Ellipse(70, 40), offset=(0, 0))

elif GEOMETRY == "wedge":
    sim.add_shape(Wedge(70, 40), offset=(0, 0))

elif GEOMETRY == "diamond":
    sim.add_shape(Diamond(60, 60), offset=(0, 0))

elif GEOMETRY == "airfoil":
    # NACA 2412 airfoil.
    # The parameters follow the constructor used in this project.
    sim.add_shape(
        Airfoil(110, 2, 4, 12, ANGLE_OF_ATTACK),
        offset=(0, 0),
    )

else:
    raise ValueError(f"Unknown geometry: {GEOMETRY!r}")


# ============================================================
# 5. RUN THE SIMULATION
# ============================================================

# The simulator advances the flow field for the requested number
# of frames and returns the collected data metrics.
#
# If you want to use the simulator's default stopping behaviour,
# consult CFDSimulator.run() before changing this call.

data_metrics = sim.run(max_frames_to_run=NUM_FRAMES)


# ============================================================
# 6. EXPORT RESULTS
# ============================================================

# Save the collected metrics as a CSV file so they can be
# analysed or plotted separately.
#
# The resulting directory structure is:
#
# data/geometry/rounded_rectangle/
# ├── data.csv
# └── snapshots/
#     ├── ...
#     └── ...

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

export_data(
    data_metrics,
    path=str(OUTPUT_DIR / "data.csv"),
)

print(f"Simulation complete. Results saved to: {OUTPUT_DIR}")
