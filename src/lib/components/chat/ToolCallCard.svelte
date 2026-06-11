<script lang="ts">
  import { slide } from 'svelte/transition';

  export let name: string;
  export let arguments: string = '';
  export let status: 'running' | 'success' | 'error' = 'running';

  let expanded = false;

  $: statusIcon = status === 'running' ? '⏳' : status === 'success' ? '✅' : '❌';
  $: statusColor = status === 'running' ? 'var(--ba-accent-primary)'
    : status === 'success' ? 'var(--ba-success)'
    : 'var(--ba-error)';
</script>

<div class="mb-2 rounded-lg overflow-hidden"
     style="background-color: var(--ba-tool-call-bg); border: 1px solid var(--ba-tool-call-border);">
  <button
    class="w-full flex items-center gap-2 px-3 py-2 text-sm hover:opacity-80 transition-opacity"
    on:click={() => expanded = !expanded}
  >
    <span>🔧</span>
    <span class="font-medium text-[var(--ba-text-primary)]">工具调用: {name}</span>
    <span class="ml-auto" style="color: {statusColor}">{statusIcon}</span>
    <span class="ml-1 text-[var(--ba-text-secondary)]">{expanded ? '▲' : '▼'}</span>
  </button>

  {#if expanded && arguments}
    <div class="px-3 pb-3" transition:slide={{ duration: 200 }}>
      <pre class="text-xs text-[var(--ba-text-secondary)] whitespace-pre-wrap font-mono leading-relaxed bg-black/5 dark:bg-white/5 p-2 rounded">
{arguments}
      </pre>
    </div>
  {/if}
</div>
