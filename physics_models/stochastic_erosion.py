"""
This module implements a stochastic erosion model using directional bias.

Plans:
- At each timestep:
    - Identify surface voxels.
    - Compute directional exposure to incoming flow using a pseudo-normal vector from a shifted "source".
    - Sample a subset of surface voxels with probability proportional to their exposure.
    - Apply random erosion amounts to the selected voxels.
- This mimics probabilistic damage due to turbulent or uneven droplet flow.

Nuclear Engineering Parallel:
This parallels stochastic transport or CRUD spallation effects seen in reactor simulation codes like OpenMC.
Unlike deterministic field-based erosion, this reflects randomness in local flux interactions.
"""

import numpy as np
from core_geometry.voxel_model import VoxelModel
from physics_models.vector_utils import compute_exposures, compute_center, normalize_vector

class StochasticErosionModel:
    def __init__(self, erosion_mean=0.01, erosion_std=0.005, erosion_fraction=0.2, seed=None, flow_vector=(0, 0, -1)):
        """
        Initialize stochastic erosion parameters.
        :param erosion_mean: Mean erosion per event.
        :param erosion_std: Std dev of erosion amount.
        :param erosion_fraction: Fraction of surface voxels to erode per timestep.
        :param seed: RNG seed for reproducibility.
        :param flow_vector: Direction of water flow (e.g., top-down = (0, 0, -1)).
        """
        self.mean = erosion_mean
        self.std = erosion_std
        self.fraction = erosion_fraction
        self.rng = np.random.default_rng(seed)
        self.normalized_flow_vector = normalize_vector(flow_vector)

    def apply(self, voxel_model: VoxelModel, water_source_height=1.0):
        """
        Apply one timestep of stochastic erosion, with flow-aware exposure bias.
        :param voxel_model: Instance of VoxelModel.
        :param water_source_height: Controls source position for directional bias.
        """
        surface_voxels = voxel_model.get_exposed_surface_voxels(self.normalized_flow_vector)
        if len(surface_voxels) == 0:
            return

        center = compute_center(voxel_model, self.normalized_flow_vector, water_source_height)

        exposures = compute_exposures(surface_voxels, center, self.normalized_flow_vector)
        exposures = np.array(exposures)
        total = exposures.sum()
        if total == 0:
            return  # No erosion if no voxel is facing the source

        exposures += 1e-6  # Tiny background exposure
        probabilities = exposures / exposures.sum()
        k = int(len(surface_voxels) * self.fraction)

        sampled_indices = self.rng.choice(len(surface_voxels), size=k, replace=False, p=probabilities)
        selected_voxels = [surface_voxels[i] for i in sampled_indices]
        raw_amounts = self.rng.normal(loc=self.mean, scale=self.std, size=k)
        raw_amounts = np.clip(raw_amounts, 0.0, None)  # Avoid negative erosion
        erosion_amounts = raw_amounts * exposures[sampled_indices]


        for idx, amt in zip(selected_voxels, erosion_amounts):
            voxel_model.erode_voxels([idx], rate=amt)
