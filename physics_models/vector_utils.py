import numpy as np
from core_geometry.voxel_model import VoxelModel

def compute_exposures(surface_voxels, center_point, normalized_flow_vector):
    """
    Compute directional exposure of each surface voxel to an incoming flow vector.
    Exposure is the cosine of the angle between surface normal and flow.

    :param surface_voxels: (N, 3) array of voxel indices.
    :param center_point: (3,) array representing a reference point (e.g., water source).
    :param flow_vector: (3,) array indicating incoming flow direction.
    :return: (N,) array of exposure values in [0, 1].
    """

    exposure = []
    for idx in surface_voxels:
        direction = np.array(idx, dtype=float) - center_point
        magnitude_direction = np.linalg.norm(direction)
        if magnitude_direction == 0:
            dot = 1.0
        else:
            normal = direction / magnitude_direction
            dot = np.dot(normal, normalized_flow_vector)
            dot = max(0.0, dot)  # Only consider surfaces facing toward the flow
        exposure.append(dot)

    # untested vectorization with numpy
    # directions = surface_voxels - center_point  # shape (N, 3)
    # norms = np.linalg.norm(directions, axis=1, keepdims=True)
    # normals = np.divide(directions, norms, out=np.zeros_like(directions), where=(norms != 0))
    # dot_products = np.einsum('ij,j->i', normals, normalized_flow_vector)
    # exposure = np.clip(dot_products, 0.0, None)

    return np.array(exposure)

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