<script lang="ts">
  import { slide } from 'svelte/transition';

  export let name: string;
  export let output: string = '';

  let expanded = false;
</script>

<div class="mb-2 rounded-lg overflow-hidden"
     style="background-color: var(--ba-tool-response-bg); border: 1px solid var(--ba-tool-response-border);">
  <button
    class="w-full flex items-center gap-2 px-3 py-2 text-sm hover:opacity-80 transition-opacity"
    on:click={() => expanded = !expanded}
  >
    <span>✅</span>
    <span class="font-medium text-[var(--ba-text-primary)]">工具返回: {name}</span>
    <span class="ml-auto text-[var(--ba-text-secondary)]">{expanded ? '▲' : '▼'}</span>
  </button>

  {#if expanded && output}
    <div class="px-3 pb-3" transition:slide={{ duration: 200 }}>
      <pre class="text-xs text-[var(--ba-text-secondary)] whitespace-pre-wrap font-mono leading-relaxed bg-black/5 dark:bg-white/5 p-2 rounded">
{output}
      </pre>
    </div>
  {/if}
</div>
