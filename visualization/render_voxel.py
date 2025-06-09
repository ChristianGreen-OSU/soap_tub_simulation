"""
This module handles 3D visualization of the voxelized soap bar.

Plans:
- Use `pyvista` or `matplotlib` for 3D rendering.
- Render full voxel volume or only surface voxels.
- Color by value (density/intactness).
- Export animations or snapshots for reports.

Nuclear Engineering Parallel:
Reactor engineers use 3D visualizations to examine flux maps, temperature distributions,
and CRUD patterns. This tool mimics core-level diagnostics visualization.
"""

import numpy as np
import pyvista as pv

def render_voxel_grid(grid, threshold=0.0):
    """
    Render voxel grid using PyVista.
    :param grid: 3D numpy array.
    :param threshold: Minimum voxel value to be rendered.
    """
    nx, ny, nz = grid.shape
    voxels = []
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                if grid[x, y, z] > threshold:
                    voxels.append([x, y, z])

    voxels = np.array(voxels, dtype=np.float32) # cast to float type for PyVista

    if len(voxels) == 0:
        print("No voxels to render.")
        return

    point_cloud = pv.PolyData(voxels)
    point_cloud['intactness'] = grid[tuple(voxels.astype(int).T)]  # Cast back for indexing

    plotter = pv.Plotter()
    plotter.add_mesh(point_cloud, render_points_as_spheres=True, point_size=10,
                     scalars='intactness', cmap='viridis')
    plotter.show()
