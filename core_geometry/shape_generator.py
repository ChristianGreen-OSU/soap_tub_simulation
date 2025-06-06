"""
This module generates voxelized 3D shapes for use in the VoxelModel.
It returns 3D NumPy arrays where voxel values are either 1.0 (material present)
or 0.0 (empty space).

Plans:
- Support creation of basic soap bar shapes:
    - Cuboid (box)
    - Cylinder (axis-aligned)
    - Ellipsoid (oval soap-like shape)
    - Rounded cuboid (box with softened corners)
- Ensure compatibility with voxel model shape and resolution.
- Enable future expansion for more complex parametric or imported CAD geometry.

Nuclear Engineering Parallel:
This mirrors the geometry generation process in reactor simulations — e.g.,
parametric definition of fuel rods, pellets, or assemblies in tools like
Serpent, OpenMC, or MCNP.
"""

import numpy as np

def make_cuboid(shape):
    """
    Create a full cuboid (solid block).
    :param shape: Tuple of (nx, ny, nz)
    :return: 3D numpy array
    """
    return np.ones(shape, dtype=np.float32)

def make_ellipsoid(shape):
    """
    Create an ellipsoid centered in the array.
    :param shape: Tuple of (nx, ny, nz)
    :return: 3D numpy array with ellipsoid voxels set to 1.0
    """
    nx, ny, nz = shape
    x = np.linspace(-1, 1, nx)
    y = np.linspace(-1, 1, ny)
    z = np.linspace(-1, 1, nz)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    mask = (X**2 + Y**2 + Z**2) <= 1.0
    grid = np.zeros(shape, dtype=np.float32)
    grid[mask] = 1.0
    return grid

def make_cylinder(shape, axis='z'):
    """
    Create a cylinder aligned along the specified axis.
    :param shape: Tuple of (nx, ny, nz)
    :param axis: 'x', 'y', or 'z'
    :return: 3D numpy array
    """
    nx, ny, nz = shape
    grid = np.zeros(shape, dtype=np.float32)

    if axis == 'z':
        x = np.linspace(-1, 1, nx)
        y = np.linspace(-1, 1, ny)
        X, Y = np.meshgrid(x, y, indexing='ij')
        mask = (X**2 + Y**2) <= 1.0
        for z in range(nz):
            grid[:, :, z][mask] = 1.0
    elif axis == 'y':
        x = np.linspace(-1, 1, nx)
        z = np.linspace(-1, 1, nz)
        X, Z = np.meshgrid(x, z, indexing='ij')
        mask = (X**2 + Z**2) <= 1.0
        for y in range(ny):
            grid[:, y, :][mask] = 1.0
    elif axis == 'x':
        y = np.linspace(-1, 1, ny)
        z = np.linspace(-1, 1, nz)
        Y, Z = np.meshgrid(y, z, indexing='ij')
        mask = (Y**2 + Z**2) <= 1.0
        for x in range(nx):
            grid[x, :, :][mask] = 1.0

    return grid

def make_rounded_cuboid(shape, exponent=6):
    """
    Create a superellipsoid-like shape (cuboid with rounded edges).
    More similar to a bar of soap.
    :param shape: Tuple of (nx, ny, nz)
    :param exponent: Controls roundness; higher = boxier.
    :return: 3D numpy array
    """
    nx, ny, nz = shape
    x = np.linspace(-1, 1, nx)
    y = np.linspace(-1, 1, ny)
    z = np.linspace(-1, 1, nz)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    mask = (np.abs(X) ** exponent + np.abs(Y) ** exponent + np.abs(Z) ** exponent) <= 1.0
    grid = np.zeros(shape, dtype=np.float32)
    grid[mask] = 1.0
    return grid
