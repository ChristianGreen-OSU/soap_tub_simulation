import numpy as np

def compute_exposures(surface_voxels, center_point, flow_vector):
    """
    Compute directional exposure of each surface voxel to an incoming flow vector.
    Exposure is the cosine of the angle between surface normal and flow.

    :param surface_voxels: (N, 3) array of voxel indices.
    :param center_point: (3,) array representing a reference point (e.g., water source).
    :param flow_vector: (3,) array indicating incoming flow direction.
    :return: (N,) array of exposure values in [0, 1].
    """
    flow_vector = np.array(flow_vector)
    flow_vector = flow_vector / np.linalg.norm(flow_vector)

    exposure = []
    for idx in surface_voxels:
        direction = np.array(idx, dtype=float) - center_point
        norm = np.linalg.norm(direction)
        if norm == 0:
            dot = 1.0
        else:
            normal = direction / norm
            dot = np.dot(normal, flow_vector)
            dot = max(0.0, dot)  # Only consider surfaces facing toward the flow
        exposure.append(dot)

    return np.array(exposure)
