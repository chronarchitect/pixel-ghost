<script lang="ts">
  import RippleGrid from './components/RippleGrid.svelte';
  let name = "";
</script>

<div style="position: relative; min-height: 100vh; background: #010b12">
  <!-- Background effect -->
  <RippleGrid />
  <!-- Main content -->
  <div class="font-mono text-9xl object-center text-center text-white">
    <h1>Pixel Ghost</h1>
  </div>
</div>
