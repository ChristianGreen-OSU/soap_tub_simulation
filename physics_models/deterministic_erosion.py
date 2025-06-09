"""
This module implements a deterministic erosion model.

Plans:
- Apply erosion uniformly or directionally across surface voxels.
- Define a flow field as a constant or spatially varying vector field.
- At each timestep:
    - Identify surface voxels.
    - Compute local exposure to flow (e.g., dot product with surface normal).
    - Erode voxels by amount proportional to local exposure.
- This model is useful as a baseline reference for comparisons.

Nuclear Engineering Parallel:
This is analogous to deterministic thermal-hydraulic modeling, where erosion
or heat flux is computed from field equations without randomness (e.g., as in
RELAP5 or CTF). It resembles CRUD growth modeling where flux and coolant flow
fields determine deposition or erosion deterministically.
"""

import numpy as np
from core_geometry.voxel_model import VoxelModel
from physics_models.vector_utils import compute_exposures, compute_center, normalize_vector

class DeterministicErosionModel:
    def __init__(self, flow_vector=(0, 0, -1), erosion_rate=0.01):
        """
        Initialize with a fixed flow vector.
        :param flow_vector: 3D tuple representing direction of water flow.
        :param erosion_rate: Base erosion rate per time step.
        """
        self.flow_vector = np.array(flow_vector) / np.linalg.norm(flow_vector)
        self.erosion_rate = erosion_rate

    def apply(self, voxel_model: VoxelModel, water_source_height=1.0):
        """
        Apply one timestep of erosion.
        :param voxel_model: Instance of VoxelModel.
        """
        surface_voxels = voxel_model.get_exposed_surface_voxels(self.flow_vector)

        normalized_flow_vector = normalize_vector(self.flow_vector)

        center = compute_center(voxel_model, normalized_flow_vector, water_source_height)

        exposure = compute_exposures(surface_voxels, center, normalized_flow_vector)

        erosion_values = np.array(exposure) * self.erosion_rate

        for idx, er in zip(surface_voxels, erosion_values):
            voxel_model.erode_voxels([idx], rate=er)
