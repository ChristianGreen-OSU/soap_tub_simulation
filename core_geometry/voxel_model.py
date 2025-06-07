"""
This module defines the voxel-based geometry representation of the soap bar.
It will be used throughout the simulation to hold the 3D grid data structure
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
from shape_generator import make_cuboid, make_ellipsoid, make_cylinder, make_rounded_cuboid

class VoxelModel:
    def __init__(self, size: Tuple[int, int, int] = (30, 30, 10), voxel_resolution: float = 1.0, geometry: str = 'cuboid') -> None:
        """
        Initialize the voxel grid.
        :param size: Tuple of (nx, ny, nz) dimensions.
        :param voxel_resolution: Physical size of each voxel in mm or cm.
        :param geometry: Form of soap bar.
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
        Compute total mass of the soap bar.
        :param density: Mass per voxel unit.
        :return: Total mass.
        """
        return float(np.sum(self.grid) * density * (self.res ** 3))

    def get_surface_voxels(self) -> np.ndarray:
        """
        Identify voxels on the surface of the soap block.
        Surface is defined as any voxel with a 6-neighbor that is empty (0).
        :return: Array of index tuples of surface voxels.
        """
        from scipy.ndimage import binary_erosion
        mask = self.grid > 0.0
        eroded = binary_erosion(mask)
        surface = mask & ~eroded
        return np.argwhere(surface)

    def erode_voxels(self, indices: Union[List[Tuple[int, int, int]], np.ndarray], rate: float) -> None:
        """
        Erode a list of voxels by a given rate.
        :param indices: List or array of voxel index tuples.
        :param rate: Float erosion amount to subtract.
        """
        for idx in indices:
            self.grid[tuple(idx)] = max(0.0, self.grid[tuple(idx)] - rate)

    def reset(self) -> None:
        """
        Reset the soap bar to a full (uneaten) state.
        """
        self.grid[:] = 1.0

    def summary(self) -> None:
        """
        Print summary stats: current mass, nonzero voxels, etc.
        """
        mass = self.get_mass()
        active_voxels = np.count_nonzero(self.grid > 0.0)
        print(f"Soap mass: {mass:.2f}, active voxels: {active_voxels}")

# Example usage:
if __name__ == "__main__":
    vm = VoxelModel((10, 10, 10))
    print("Initial mass:", vm.get_mass())
    surf = vm.get_surface_voxels()
    print(f"Surface voxels: {len(surf)}")
    vm.erode_voxels(surf[:10], rate=0.1)
    print("Mass after erosion:", vm.get_mass())
