import numpy as np
from core_geometry.voxel_model import VoxelModel

def compute_exposures(surface_voxels, water_source, normalized_flow_vector):
    """
    Compute directional exposure of each surface voxel to an incoming flow vector.
    Exposure is the cosine of the angle between surface normal and flow.

    :param surface_voxels: (N, 3) array of voxel indices.
    :param water_source: (3,) array representing a reference point (e.g., water source).
    :param flow_vector: (3,) array indicating incoming flow direction.
    :return: (N,) array of exposure values in [0, 1].
    """

    exposures = []
    for voxel in surface_voxels:
        source_to_voxel_vector = np.array(voxel, dtype=float) - water_source # displacement vector
        distance: int = np.linalg.norm(source_to_voxel_vector)

        if distance == 0:
            exposure_scalar = 1.0
        else:
            incident_direction = source_to_voxel_vector / distance
            exposure_scalar = np.dot(incident_direction, normalized_flow_vector) # cosine
            exposure_scalar = max(0.0, exposure_scalar)  # Only consider surfaces facing toward the flow

        exposures.append(exposure_scalar)

    # untested vectorization with numpy
    # directions = surface_voxels - center_point  # shape (N, 3)
    # norms = np.linalg.norm(directions, axis=1, keepdims=True)
    # normals = np.divide(directions, norms, out=np.zeros_like(directions), where=(norms != 0))
    # dot_products = np.einsum('ij,j->i', normals, normalized_flow_vector)
    # exposure = np.clip(dot_products, 0.0, None)

    return np.array(exposures)

def compute_center(voxel_model: VoxelModel, normalized_flow_vector, water_source_height=0.0):
    grid_shape = np.array(voxel_model.grid.shape, dtype=float)
    baseline_offset = compute_baseline_offset(voxel_model, normalized_flow_vector)

    # Effective offset is baseline + user-provided height
    total_offset = baseline_offset + water_source_height

    center = grid_shape / 2.0
    center = center + (-normalized_flow_vector) * total_offset
    return center

def normalize_vector(vector):
    normalized_vector = np.array(vector, dtype=float) / np.linalg.norm(vector)
    return normalized_vector

def compute_baseline_offset(voxel_model, normalized_flow_vector):
    # Half-size of the soap in each direction
    half_extents = np.array(voxel_model.size) / 2.0

    # Project the half-extents onto the flow direction
    # This gives how far the soap extends in the flow direction
    directional_extent = np.abs(np.dot(half_extents, normalized_flow_vector))

    return directional_extent
