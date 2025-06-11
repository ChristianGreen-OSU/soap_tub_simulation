<script>
    let yamlConfig = `soap:
        size: [50, 75, 20]
        voxel_resolution: 1.0
        geometry: 'cuboid'

simulation:
        steps: 50
        log_interval: 10
        heat_map: false
        debug_vectors: false

erosion_model:
        type: stochastic
        flow_vector: [0, 0, -1]
        erosion_rate: 1.5
        water_source_height: 1.0
        erosion_std: 0.1
        erosion_fraction: 0.75
        seed: 43`;

    let previewUrl = "http://localhost:5000/preview.png";
    let isLoading = false;
    async function updatePreview() {
        isLoading = true;
        const res = await fetch("http://localhost:5000/generate_preview", {
            method: "POST",
            headers: { "Content-Type": "application/x-yaml" },
            body: yamlConfig
        });

        if (res.ok) {
            previewUrl = "http://localhost:5000/preview.png?ts=" + Date.now(); // force refresh
        } else {
            console.error(await res.text());
        }
    }
</script>

<h2>Soap Simulation Preview</h2>

<textarea bind:value={yamlConfig} rows="20" cols="80"></textarea>
<br />
<button on:click={updatePreview}>Update Preview</button>
<br />

{#if isLoading}
  <p style="color: gray;">Generating preview...</p>
{/if}

<img
  src={previewUrl}
  alt="Soap Voxel Preview"
  style="margin-top: 10px; display: {isLoading ? 'none' : 'block'}"
  on:load={() => (isLoading = false)}
/>
