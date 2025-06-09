import numpy as np
import pyvista as pv
from core_geometry.voxel_model import VoxelModel
from physics_models.vector_utils import compute_center, normalize_vector
def visualize_flow_debug_scene(voxel_model: VoxelModel, flow_vector, water_source_height):
    """
    Visualizes the flow vector, shifted erosion center, and center plane.
    """
    normalized_flow_vector = normalize_vector(flow_vector)

    center = compute_center(voxel_model, normalized_flow_vector, water_source_height)

    # Voxel positions
    voxels = np.argwhere(voxel_model.grid > 0.0).astype(float)
    cloud = pv.PolyData(voxels)

    # PyVista setup
    plotter = pv.Plotter()
    plotter.add_mesh(cloud, render_points_as_spheres=True, point_size=8, color="lightblue")

    # Flow vector arrow (scaled for visibility)
    arrow = pv.Arrow(start=center, direction=normalized_flow_vector, scale=10.0, tip_length=1.0)
    plotter.add_mesh(arrow, color="red", label="Flow Vector")

    # Shifted center sphere
    plotter.add_mesh(pv.Sphere(radius=1.0, center=center), color="orange", label="Shifted Center")

    # Mid-plane for reference (XY plane at original grid center)
    mid_plane_center = np.array(voxel_model.grid.shape) / 2.0
    plane = pv.Plane(center=(mid_plane_center[0], mid_plane_center[1], mid_plane_center[2]),
                     direction=(0, 0, 1),
                     i_size=voxel_model.grid.shape[0], j_size=voxel_model.grid.shape[1])
    plotter.add_mesh(plane, color="green", opacity=0.3, label="Original Z Center Plane")

    plotter.add_legend()
    plotter.show()