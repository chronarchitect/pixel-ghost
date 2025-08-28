<script lang="ts">
  let name = "";
</script>

<main>
  <p>What is your name?</p>
  <form>
    <input bind:value={name} placeholder="Enter your name" />
  </form>
  {#if name == ""}
    <p>Please enter your name above.</p>
  {:else}
    <p>Hello {name}!</p>
  {/if}
</main>
