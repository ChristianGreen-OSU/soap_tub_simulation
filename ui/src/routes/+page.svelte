<script>
  import FlowVectorEditor from '$lib/FlowVectorEditor.svelte';
  let flowVectorStr = "[0, 0, -1]";
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
      previewUrl = "http://localhost:5000/preview.png?ts=" + Date.now();
    } else {
      console.error(await res.text());
    }
  }
</script>

<div class="min-h-screen bg-[#0d1117] text-[#c9d1d9] p-8">
  <h2 class="text-2xl font-semibold mb-4">🧼 Soap Simulation Preview</h2>

  <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
    <!-- YAML editor -->
    <div>
      <label class="block text-sm mb-2 font-mono text-[#8b949e]">Simulation Config (YAML)
        <textarea
            bind:value={yamlConfig}
            rows="20"
            class="w-full p-4 text-sm font-mono bg-[#161b22] border border-[#30363d] rounded resize-none focus:outline-none focus:ring-2 focus:ring-[#58a6ff]">
        </textarea>
      </label>
      <FlowVectorEditor bind:flowVectorStr />
      <button
        on:click={updatePreview}
        class="mt-4 bg-[#238636] hover:bg-[#2ea043] text-white font-semibold px-4 py-2 rounded"
      >
        Update Preview
      </button>

      {#if isLoading}
        <p class="text-[#8b949e] mt-2 animate-pulse">🌀 Generating preview...</p>
      {/if}
    </div>

    <!-- Image preview -->
    <div class="flex justify-center items-start mt-6 md:mt-0">
      <img
        src={previewUrl}
        alt="Soap Preview"
        class="rounded-lg border border-[#30363d] max-w-full shadow-md"
        style="display: {isLoading ? 'none' : 'block'}"
        on:load={() => (isLoading = false)}
      />
    </div>
  </div>
</div>
