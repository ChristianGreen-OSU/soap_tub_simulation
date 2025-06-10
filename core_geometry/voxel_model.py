"""
This module defines the voxel-based geometry representation of the soap bar.
It is used throughout the simulation to hold the 3D grid data structure
representing the soap, where each voxel can represent soap presence (binary)
or local soap density (float).

Plans:
- Represent the soap bar as a 3D numpy array.
- Allow initialization of standard shapes (cube, cylinder, ellipsoid).
- Provide helper functions to:
    - Access surface voxels (for erosion algorithms).
    - Compute total mass and surface area.
    - Optionally assign material properties per voxel.
- This abstraction will be updated in-place by the erosion engine.
- Later, this can be extended to load real 3D mesh data or support unstructured grids.

Nuclear Engineering Parallel:
This mimics how reactor geometry is spatially discretized into lattices or
meshes in codes like OpenMC or Serpent. Each voxel here is like a fuel pin or
cell in a core simulator.
"""

from typing import Tuple, List, Union
import numpy as np
from .shape_generator import make_cuboid, make_ellipsoid, make_cylinder, make_rounded_cuboid


class VoxelModel:
    def __init__(self, size: Tuple[int, int, int] = (30, 30, 10), voxel_resolution: float = 1.0, geometry: str = 'cuboid') -> None:
        """
        Initialize the voxel grid representing the soap bar.

        :param size: Dimensions of the voxel grid (nx, ny, nz).
        :param voxel_resolution: Real-world size of each voxel in mm or cm.
        :param geometry: Shape of the soap bar ('cuboid', 'ellipsoid', 'cylinder', 'rounded_cuboid').
        """
        self.size: Tuple[int, int, int] = size
        self.res: float = voxel_resolution

        if geometry == 'cuboid':
            self.grid = make_cuboid(size)
        elif geometry == 'ellipsoid':
            self.grid = make_ellipsoid(size)
        elif geometry == 'cylinder':
            self.grid = make_cylinder(size)
        elif geometry == 'rounded_cuboid':
            self.grid = make_rounded_cuboid(size, exponent=6)
        else:
            raise ValueError(f"Unsupported geometry: {geometry}")

    def get_mass(self, density: float = 1.0) -> float:
        """
        Compute the total mass of the soap bar.

        :param density: Mass per voxel unit (adjustable for different materials).
        :return: Total mass as a float.
        """
        return float(np.sum(self.grid) * density * (self.res ** 3))

    def get_exposed_surface_voxels(self, flow_vector: Tuple[int, int, int]) -> np.ndarray:
        """
        Return surface voxels that are directly exposed to the incoming flow.

        A voxel is considered exposed if it:
        - Contains soap (value > 0), AND
        - Has a neighboring voxel upstream (in the opposite direction of flow) that is empty (value ≤ 0),
          OR lies on the edge of the grid.

        :param flow_vector: Direction of incoming water flow (e.g., (0, 0, -1) for top-down).
        :return: Numpy array of index tuples (x, y, z) for exposed surface voxels.
        """
        direction = np.round(flow_vector).astype(int)
        mask = self.grid > 0.0
        exposed_voxels = []

        nx, ny, nz = self.grid.shape
        for x in range(nx):
            for y in range(ny):
                for z in range(nz):
                    if not mask[x, y, z]:
                        continue

                    neighbor = np.array([x, y, z]) + direction
                    if (
                        0 <= neighbor[0] < nx and
                        0 <= neighbor[1] < ny and
                        0 <= neighbor[2] < nz
                    ):
                        if self.grid[tuple(neighbor)] <= 0.0:
                            exposed_voxels.append((x, y, z))
                    else:
                        # Voxels on the outer boundary are considered exposed
                        exposed_voxels.append((x, y, z))

        return np.array(exposed_voxels)

    def erode_voxels(self, indices: Union[List[Tuple[int, int, int]], np.ndarray], rate: float) -> None:
        """
        Reduce the density value of each voxel by a fixed rate.

        If a voxel drops below a small threshold, it is considered fully eroded and set to zero.

        :param indices: List or array of voxel (x, y, z) indices.
        :param rate: Amount to subtract from each voxel's value.
        """
        for idx in indices:
            new_value = self.grid[tuple(idx)] - rate
            self.grid[tuple(idx)] = 0.0 if new_value < 1e-4 else new_value

    def reset(self) -> None:
        """
        Reset the entire voxel grid to a full (uneaten) state of value = 1.0.
        """
        self.grid[:] = 1.0

    def summary(self) -> None:
        """
        Print basic statistics of the current soap state, including mass and voxel count.
        """
        mass = self.get_mass()
        active_voxels = np.count_nonzero(self.grid > 0.0)
        print(f"Soap mass: {mass:.2f}, active voxels: {active_voxels}")


# Example usage:
if __name__ == "__main__":
    vm = VoxelModel((10, 10, 10))
    print("Initial mass:", vm.get_mass())
    surface_voxels = vm.get_exposed_surface_voxels((0, 0, -1))
    print(f"Surface voxels: {len(surface_voxels)}")
    vm.erode_voxels(surface_voxels[:10], rate=0.1)
    print("Mass after erosion:", vm.get_mass())
