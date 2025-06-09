"""
This module analyzes erosion patterns between successive voxel grid states.
It highlights where and how much material was lost spatially.

Plans:
- Compare two voxel grids.
- Output difference (erosion) map.
- Visualize it as a heatmap (matplotlib) or point cloud (pyvista).

Nuclear Engineering Parallel:
This is like CRUD delta maps or power shape comparisons over burnup steps.
Useful for spatial sensitivity analysis and identifying erosion hotspots.
"""

import numpy as np
import matplotlib.pyplot as plt
import pyvista as pv

def compute_erosion_map(grid_before, grid_after):
    """
    Compute the voxel-wise erosion amount.
    :param grid_before: 3D numpy array before erosion.
    :param grid_after: 3D numpy array after erosion.
    :return: 3D numpy array of erosion amounts.
    """
    erosion = grid_before - grid_after
    erosion[erosion < 0] = 0  # no negative erosion
    return erosion

def plot_erosion_heatmap(erosion_grid, threshold=0.0):
    """
    Visualize erosion grid as a 3D scatter plot.
    :param erosion_grid: 3D numpy array of erosion deltas.
    :param threshold: Only show values above this.
    """
    indices = np.argwhere(erosion_grid > threshold)
    values = erosion_grid[tuple(indices.T)]

    indices = np.array(indices, dtype=np.float32)

    cloud = pv.PolyData(indices)
    cloud['erosion'] = values

    plotter = pv.Plotter()
    plotter.add_mesh(cloud, render_points_as_spheres=True, point_size=10,
                     scalars='erosion', cmap='hot')
    plotter.show()
