from numpy import stack, savez_compressed

class SnapshotExporter:
    def __init__(self, path, frequency=100):
        self.sim_renderer = None
        self.path = path
        self.frequency = frequency

    def export_snapshot(self, frame_num):
        if frame_num % self.frequency != 0: return
        if self.sim_renderer is None: return

        snapshot = self.get_snapshot()
        if snapshot is not None: self.save_snapshot(snapshot, frame_num)

    def get_snapshot(self):
        # Get all 4 conservative variables from the simulator.state
        if self.sim_renderer is not None:
            density = self.sim_renderer.state.density
            momentum_x = self.sim_renderer.state.momentum_x
            momentum_y = self.sim_renderer.state.momentum_y
            energy = self.sim_renderer.state.energy
            solid = self.sim_renderer.state.solid

            # Stack into single array
            return [density, momentum_x, momentum_y, energy, solid]

    def save_snapshot(self, snapshot, frame_num):
        filename = f"{self.path}/snapshot_{frame_num}.npz"
        savez_compressed(filename, density=snapshot[0], momentum_x=snapshot[1], momentum_y=snapshot[2], energy=snapshot[3], solid=snapshot[4])
