# flask_app.py
from flask import Flask, request, send_file
from flask_cors import CORS
import yaml
import os
import pyvista as pv

from core_geometry.voxel_model import VoxelModel
from visualization.flow_vector import visualize_flow_debug_scene

# Enable offscreen rendering on Windows/macOS
pv.global_theme.window_size = [800, 600]

app = Flask(__name__, static_folder="static")
CORS(app)

@app.route("/generate_preview", methods=["POST"])
def generate_preview():
    try:
        config = yaml.safe_load(request.data)

        vm = VoxelModel(
            size=tuple(config['soap']['size']),
            voxel_resolution=config['soap']['voxel_resolution'],
            geometry=config['soap'].get('geometry', 'cuboid')
        )

        flow_vector = config['erosion_model'].get('flow_vector', [0, 0, -1])
        water_source_height = config['erosion_model'].get('water_source_height', 1.0)

        # Offscreen rendering
        plotter = pv.Plotter(off_screen=True)
        visualize_flow_debug_scene(vm, flow_vector, water_source_height, plotter=plotter)
        plotter.screenshot("./static/preview.png")
        plotter.close()

        return {"status": "ok"}

    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/preview.png")
def serve_preview():
    return send_file("./static/preview.png", mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
