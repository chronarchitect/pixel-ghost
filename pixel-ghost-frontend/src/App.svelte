<script lang="ts">
  import { Play } from '@lucide/svelte';
  import RippleGrid from './components/RippleGrid.svelte';
  let name = "";
</script>

<div>
  <!-- Background effect -->
  <RippleGrid />
  <!-- Main content -->
  <nav class="relative bg-gray">
    <div class="text-white text-lg font-semibold">
      Pixel Ghost Menu
    </div>
  </nav>  
  <div class="h-screen flex flex-col justify-center items-center bg-linear-to-b from-[rgba(0,0,0,0)] to-[rgba(10,11,18,0.95)] via-[rgba(0,0,0,0.6)]">
    <div class="logo basis-1 text-9xl object-center text-center text-white">
      <div class="pixel">
        Pixel
      </div>
      <div class="ghost">
        Ghost
      </div>
    </div>
    <div class="button rounded-full bg-yellow-500 hover:bg-lime-400 text-black font-bold py-4 px-8 transition duration-300 ease-in-out transform hover:scale-105">
        <Play class="inline-block mr-2" />Start
    </div>
    
  </div>
  
</div>
