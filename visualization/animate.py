"""
This module creates a time-lapse animation of the soap erosion simulation.
It uses PyVista to render voxel grids across time steps and exports the result
as a video (MP4) or animated GIF.

Plans:
- Accept a list of 3D voxel grids or snapshots.
- Use PyVista to render each frame.
- Save as an animation.

Nuclear Engineering Parallel:
This is similar to time-evolving visualizations of core simulations — e.g.,
CRUD propagation, thermal field evolution, or depletion effects.
"""
import os
from datetime import datetime
from typing import List
import pyvista as pv
import numpy as np

def animate_voxel_series(voxel_grids: List[np.ndarray], threshold=0.0, label="run", filename="erosion.gif", fps=5):
    """
    Animate a list of voxel grids using PyVista and export as GIF.
    :param voxel_grids: List of 3D numpy arrays.
    :param threshold: Minimum voxel value to render.
    :param filename: Output filename (GIF or MP4).
    :param fps: Frames per second.
    """
    

    os.makedirs("./assets/gifs", exist_ok=True)
    timestamp = datetime.now().strftime("%d_%H%M")
    filename = f"./assets/gifs/{timestamp}_{label}.gif"
    plotter = pv.Plotter(off_screen=True)
    plotter.open_gif(filename)

    for grid in voxel_grids:
        voxels = np.argwhere(grid > threshold)
        voxels_int = np.array(voxels, dtype=int)         # For indexing
        voxels_float = np.array(voxels, dtype=np.float32)  # For PyVista

        if voxels.size == 0:
            continue

        cloud = pv.PolyData(voxels_float)
        cloud['intactness'] = grid[tuple(voxels_int.T)]

        plotter.clear()
        plotter.camera_position = [
            (-grid.shape[0],
            -grid.shape[1],
            -grid.shape[2] * 6.0),    # straight above
            (grid.shape[0] / 2,
            grid.shape[1] / 2,
            grid.shape[2] / 2),      # focal point
            (1, 1, 1)                
        ]   
        plotter.add_mesh(cloud, render_points_as_spheres=True, point_size=10,
                         scalars='intactness', cmap='viridis')
        plotter.write_frame()

    plotter.close()
    print(f"Saved animation to {filename}")

def make_label(config) -> str:
    # Build descriptive label
    geo = config['soap'].get('geometry', 'cuboid')
    erosion_type = config['erosion_model']['type']
    flow = config['erosion_model'].get('flow_vector', [0, 0, -1])
    rate = config['erosion_model'].get('erosion_rate', config['erosion_model'].get('erosion_rate', 0.1))
    water_source_height = config['erosion_model'].get('water_source_height', 1.0)

    label = f"{erosion_type}_{geo}_v-{flow}_r-{rate}_w-{water_source_height}"
    label = label.replace(" ", "").replace("[", "").replace("]", "").replace(",", "_")

    return label