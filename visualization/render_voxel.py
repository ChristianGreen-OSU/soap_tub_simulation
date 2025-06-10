"""
This module handles 3D visualization of the voxelized soap bar.

Plans:
- Use `pyvista` or `matplotlib` for 3D rendering.
- Render full voxel volume or only surface voxels.
- Color by value (density/intactness).
- Optionally export rendered voxel cloud as a 3D mesh (.obj) for external analysis or visualization tools.

Nuclear Engineering Parallel:
Reactor engineers use 3D visualizations to examine flux maps, temperature distributions,
and CRUD patterns. This tool mimics core-level diagnostics visualization.
"""

import os
import numpy as np
import pyvista as pv

def render_voxel_grid(grid, threshold=0.0, export_mesh=True, mesh_filename="assets/meshes/final_frame.obj"):
    """
    Render voxel grid using PyVista and optionally export to a 3D object file.

    Parameters:
    - grid (np.ndarray): 3D voxel array with float values representing intactness.
    - threshold (float): Minimum voxel value to render.
    - export_mesh (bool): If True, save visible voxels as a 3D .obj file.
    - mesh_filename (str): Path for saving the output mesh (default: ./assets/meshes/final_frame.obj).
    """
    nx, ny, nz = grid.shape
    voxels = []
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                if grid[x, y, z] > threshold:
                    voxels.append([x, y, z])

    voxels = np.array(voxels, dtype=np.float32)  # Required float type for PyVista

    if len(voxels) == 0:
        print("No voxels to render.")
        return

    point_cloud = pv.PolyData(voxels)
    point_cloud['intactness'] = grid[tuple(voxels.astype(int).T)]

    # Export to .obj mesh if requested
    if export_mesh:
        os.makedirs("assets/meshes", exist_ok=True)
        point_cloud.save(mesh_filename)
        print(f"Exported mesh to {mesh_filename}")

    # Render interactively
    plotter = pv.Plotter()
    plotter.add_mesh(point_cloud, render_points_as_spheres=True, point_size=10,
                     scalars='intactness', cmap='viridis')
    plotter.show()
