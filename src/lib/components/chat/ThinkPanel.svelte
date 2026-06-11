<script lang="ts">
  import { theme } from '$lib/stores/theme';
  import { slide } from 'svelte/transition';

  export let content: string;
  export let isThinking = false;

  let expanded = false;

  $: label = $theme === 'dark' ? '普拉纳分析中...' : '阿罗纳正在思考...';
  $: icon = $theme === 'dark' ? '🌙' : '💭';
</script>

<div class="mb-2 rounded-lg overflow-hidden"
     style="background-color: var(--ba-think-bg); border: 1px solid var(--ba-border);">
  <button
    class="w-full flex items-center gap-2 px-3 py-2 text-sm hover:opacity-80 transition-opacity"
    on:click={() => expanded = !expanded}
  >
    <span>{icon}</span>
    <span class="font-medium text-[var(--ba-text-secondary)]">{label}</span>
    {#if isThinking}
      <span class="ml-auto animate-pulse text-[var(--ba-accent-primary)]">●</span>
    {/if}
    <span class="ml-auto text-[var(--ba-text-secondary)]">
      {expanded ? '▲' : '▼'}
    </span>
  </button>

  {#if expanded}
    <div class="px-3 pb-3" transition:slide={{ duration: 200 }}>
      <pre class="text-xs text-[var(--ba-text-secondary)] whitespace-pre-wrap font-mono leading-relaxed">
{content}
      </pre>
    </div>
  {/if}
</div>
