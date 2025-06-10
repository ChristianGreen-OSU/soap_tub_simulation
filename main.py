"""
Main script to initialize and run the soap erosion simulation.

Responsibilities:
- Load and parse configuration from YAML.
- Construct the voxel-based soap geometry.
- Select and initialize the erosion model (deterministic or stochastic).
- Evolve the simulation over time using the TimeIntegrator.
- Visualize flow vector alignment and erosion process.
- Output final erosion metrics and visualizations.

Nuclear Engineering Parallel:
This script functions as a high-level simulation driver, analogous to
the input deck processor or solver harness in core simulators like OpenMC,
RELAP5, or MOOSE-based applications.
"""

import yaml
import pprint
import numpy as np

# Core simulation components
from core_geometry.voxel_model import VoxelModel
from physics_models.deterministic_erosion import DeterministicErosionModel
from physics_models.stochastic_erosion import StochasticErosionModel
from simulation_engine.time_integrator import TimeIntegrator

# Visualization utilities
from visualization.render_voxel import render_voxel_grid
from visualization.animate import animate_voxel_series, make_label
from visualization.flow_vector import visualize_flow_debug_scene

# Analysis utilities
from analysis_tools.mass_tracker import MassTracker
from analysis_tools.erosion_map import compute_erosion_map, plot_erosion_heatmap

def load_config(path="parameters.yaml"):
    """Load simulation parameters from YAML file."""
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def main():
    cfg = load_config()

    # Echo simulation setup
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

    # Initialize geometry (voxelized soap bar)
    size = tuple(cfg['soap']['size'])
    res = cfg['soap']['voxel_resolution']
    vm = VoxelModel(size=size, voxel_resolution=res, geometry=cfg['soap'].get('geometry', 'cuboid'))

    # Initialize erosion model based on type
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

    # Visualize initial flow direction and voxel structure for debugging
    if cfg['simulation']['debug_vectors']: 
        visualize_flow_debug_scene(vm, flow_vector=em_cfg['flow_vector'], water_source_height=em_cfg['water_source_height'])

    # Run the simulation for configured number of steps
    steps = cfg['simulation']['steps']
    log_int = cfg['simulation']['log_interval']
    sim = TimeIntegrator(vm, eroder, steps=steps)
    sim.run(log_interval=log_int, save_snapshots=True, water_source_height=em_cfg['water_source_height'])

    # Analyze and report final results
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

    # Plot mass loss curve
    tracker.plot()

    # Render final voxel state
    render_voxel_grid(vm.grid)

    # Generate animated GIF of voxel snapshots over time
    snapshots = sim.get_snapshots()
    animate_voxel_series(snapshots, label=make_label(cfg))

    # Optional: heatmap of erosion change
    if(cfg['simulation']['heat_map']):
        erosion_map = compute_erosion_map(snapshots[0], snapshots[-1])
        plot_erosion_heatmap(erosion_map, threshold=0.01)

if __name__ == '__main__':
    main()
