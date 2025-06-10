import numpy as np
import pyvista as pv
from core_geometry.voxel_model import VoxelModel
from physics_models.vector_utils import compute_center, normalize_vector

def visualize_flow_debug_scene(voxel_model: VoxelModel, flow_vector, water_source_height):
    """
    Visualizes the geometry and directional inputs of the simulation using PyVista.

    This scene helps debug how the erosion model will interpret the spatial
    setup. It shows:
    - The actual occupied voxels (soap structure)
    - The normalized water flow vector (as an arrow)
    - The erosion 'center' reference point used in computing exposure
    - A green center-plane representing the original midpoint of the voxel grid

    Parameters:
    - voxel_model (VoxelModel): The geometry object containing the voxel grid.
    - flow_vector (tuple or array): The direction from which water is assumed to arrive.
    - water_source_height (float): The scalar offset upstream (against the flow vector)
      used to define the erosion center (like a virtual water source).
    """
    # Normalize the flow vector to ensure consistent magnitude and direction
    normalized_flow_vector = normalize_vector(flow_vector)

    # Compute the upstream-shifted center used for directional exposure calculations
    center = compute_center(voxel_model, normalized_flow_vector, water_source_height)

    # Identify positions of all nonzero voxels (i.e., existing soap)
    voxels = np.argwhere(voxel_model.grid > 0.0).astype(float)
    cloud = pv.PolyData(voxels)

    # Initialize the 3D plot
    plotter = pv.Plotter()
    plotter.add_mesh(cloud, render_points_as_spheres=True, point_size=8, color="lightblue")

    # Create and render an arrow representing the flow vector direction
    arrow = pv.Arrow(start=center,
                     direction=flow_vector,
                     scale=10.0,         # Length scaling for visibility
                     tip_length=1.0)     # Arrowhead size
    plotter.add_mesh(arrow, color="red", label="Flow Vector")

    # Visualize the shifted 'source' center as a small orange sphere
    plotter.add_mesh(pv.Sphere(radius=1.0, center=center), color="orange", label="Shifted Center")

    # Reference plane to indicate the middle of the voxel grid (XY plane at midpoint in Z)
    mid_plane_center = np.array(voxel_model.grid.shape) / 2.0
    plane = pv.Plane(center=mid_plane_center,
                     direction=(0, 0, 1),  # Oriented in XY plane
                     i_size=voxel_model.grid.shape[0],
                     j_size=voxel_model.grid.shape[1])
    plotter.add_mesh(plane, color="green", opacity=0.3, label="Original Z Center Plane")

    # Show a legend and open the interactive viewer
    plotter.add_legend()
    plotter.show()
