"""
Main script to initialize and run the soap erosion simulation.

Plans:
- Parse YAML config file.
- Instantiate voxel model and erosion engine.
- Run time integrator.
- Plot or export mass loss and voxel grid visualization.
- Optionally animate or analyze erosion maps from voxel snapshots.

Nuclear Engineering Parallel:
This is akin to a primary driver in simulation software (e.g., OpenMC input processor),
responsible for wiring together physics modules and execution.
"""

import yaml
import pprint
import numpy as np
import pyvista as pv
from core_geometry.voxel_model import VoxelModel
from physics_models.deterministic_erosion import DeterministicErosionModel
from physics_models.stochastic_erosion import StochasticErosionModel
from simulation_engine.time_integrator import TimeIntegrator
from visualization.render_voxel import render_voxel_grid
from visualization.animate import animate_voxel_series, make_label
from visualization.flow_vector import visualize_flow_debug_scene
from analysis_tools.mass_tracker import MassTracker

def load_config(path="parameters.yaml"):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def main():
    cfg = load_config()

    # Print config summary
    print("\n[Simulation Configuration Loaded]")
    pprint.pprint(cfg)
    print("\nParsed Inputs Summary:")
    print(f" - Soap size (voxels): {cfg['soap']['size']}")
    print(f" - Geometry shape: {cfg['soap'].get('geometry', 'cuboid')}")
    print(f" - Voxel resolution: {cfg['soap']['voxel_resolution']} mm/voxel")
    print(f" - Erosion model: {cfg['erosion_model']['type']}")
    print(f"   • Flow vector: {cfg['erosion_model']['flow_vector']}")
    print(f"   • Erosion rate: {cfg['erosion_model']['erosion_rate']}")
    if cfg['erosion_model']['type'] == 'stochastic':
        print(f"   • Std dev: {cfg['erosion_model']['erosion_std']}")
        print(f"   • Fraction of surface affected: {cfg['erosion_model']['erosion_fraction']}")
        if 'seed' in cfg['erosion_model']:
            print(f"   • Random seed: {cfg['erosion_model']['seed']}")
    print(f" - Total time steps: {cfg['simulation']['steps']}")
    print(f" - Log interval: {cfg['simulation']['log_interval']}")
    print("--------------------------------------\n")

    # Geometry setup
    size = tuple(cfg['soap']['size'])
    res = cfg['soap']['voxel_resolution']
    vm = VoxelModel(size=size, voxel_resolution=res, geometry=cfg['soap'].get('geometry', 'cuboid'))

    # Select erosion model
    em_cfg = cfg['erosion_model']
    if em_cfg['type'] == 'deterministic':
        eroder = DeterministicErosionModel(
            flow_vector=em_cfg['flow_vector'],
            erosion_rate=em_cfg['erosion_rate']
        )
    elif em_cfg['type'] == 'stochastic':
        eroder = StochasticErosionModel(
            flow_vector=em_cfg['flow_vector'],
            erosion_mean=em_cfg['erosion_rate'],
            erosion_std=em_cfg['erosion_std'],
            erosion_fraction=em_cfg['erosion_fraction'],
            seed=em_cfg.get('seed', None)
        )
    else:
        raise ValueError("Unsupported erosion model type.")
    
    visualize_flow_debug_scene(vm, flow_vector=em_cfg['flow_vector'], water_source_height=em_cfg['water_source_height'])

    # Run simulation
    steps = cfg['simulation']['steps']
    log_int = cfg['simulation']['log_interval']
    sim = TimeIntegrator(vm, eroder, steps=steps)
    sim.run(log_interval=log_int, save_snapshots=True, water_source_height=em_cfg['water_source_height'])

    # Analyze results
    tracker = MassTracker(sim.mass_history)
    summary = tracker.compute_summary()
    if summary is None:
        print("No summary stats available.")
        return
    for key, value in summary.items():
        print(f"{key}: {value}")

    print("Final grid stats:")
    print("Min value:", np.min(vm.grid))
    print("Max value:", np.max(vm.grid))

    tracker.plot()
    render_voxel_grid(vm.grid)

    # Generate animation from snapshots
    snapshots = sim.get_snapshots()
    animate_voxel_series(snapshots, label=make_label(cfg))

    # Show final erosion map (delta from start to end)
    # erosion_map = compute_erosion_map(snapshots[0], snapshots[-1])
    # plot_erosion_heatmap(erosion_map, threshold=0.01)


if __name__ == '__main__':
    main()
