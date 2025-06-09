"""
This module controls the time-stepping loop of the simulation.

Plans:
- Initialize voxel model and erosion model (deterministic or stochastic).
- For a set number of timesteps:
    - Apply erosion model.
    - Record mass, surface area, or other observables.
    - Optionally visualize or log state every N steps.
- Allow plug-in models via simple interface (must have .apply(voxel_model)).
- Output history for analysis.

Nuclear Engineering Parallel:
This plays the role of a transient solver driver (e.g., like in RELAP5 or COBRA).
It integrates the physical model forward in time and collects diagnostics — similar to burnup solvers.
"""

from copy import deepcopy
import matplotlib.pyplot as plt
import numpy as np
from core_geometry.voxel_model import VoxelModel

class TimeIntegrator:
    def __init__(self, voxel_model: VoxelModel, erosion_model, steps=100):
        """
        Initialize the simulation driver.
        :param voxel_model: Instance of VoxelModel.
        :param erosion_model: Instance with an .apply() method.
        :param steps: Number of simulation timesteps.
        """
        self.vm = voxel_model
        self.eroder = erosion_model
        self.steps = steps
        self.mass_history = []
        self.grid_snapshots = []  # Store grids for animation

    def run(self, log_interval=10, save_snapshots=True, water_source_height=1.0):
        """
        Run the simulation.
        :param log_interval: Print status every N steps.
        :param save_snapshots: Store voxel grid at each step.
        """
        for step in range(self.steps):
            if save_snapshots:
                self.grid_snapshots.append(deepcopy(self.vm.grid))

            self.eroder.apply(self.vm, water_source_height=1.0)
            mass = self.vm.get_mass()
            self.mass_history.append(mass)

            if step % log_interval == 0:
                print(f"Step {step:4d}: Mass = {mass:.3f}")

        # Save final grid if needed
        if save_snapshots:
            self.grid_snapshots.append(deepcopy(self.vm.grid))

    def plot_mass_history(self):
        """
        Plot soap mass over time.
        """
        plt.plot(self.mass_history)
        plt.xlabel("Time step")
        plt.ylabel("Soap mass")
        plt.title("Mass Loss Over Time")
        plt.grid(True)
        plt.show()

    def get_snapshots(self):
        """
        Return the list of voxel grid snapshots (3D numpy arrays).
        """
        return self.grid_snapshots
