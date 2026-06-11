<script lang="ts">
  import { onDestroy } from 'svelte';
  import { HermesParser, type HermesSegment } from '$lib/utils/hermes-parser';
  import ThinkPanel from './ThinkPanel.svelte';
  import ToolCallCard from './ToolCallCard.svelte';
  import ToolResponseCard from './ToolResponseCard.svelte';

  export let content: string = '';
  export let streaming = false;

  const parser = new HermesParser();
  let segments: HermesSegment[] = [];
  let partial: HermesSegment | null = null;

  // Re-parse when content changes (for streaming)
  $: {
    if (content) {
      const newSegments = parser.feed(content);
      segments = [...segments, ...newSegments];
    }
  }

  // Update partial for streaming display
  $: if (streaming) {
    partial = parser.getPartial();
  } else {
    partial = null;
  }

  // On final message, flush any remaining content
  $: if (!streaming && content) {
    const flushed = parser.flush();
    segments = [...segments, ...flushed];
  }

  onDestroy(() => {
    // Cleanup if needed
  });
</script>

<div class="hermes-message">
  {#each segments as segment (segment.type + segment.content.slice(0, 20))}
    {#if segment.type === 'text'}
      <div class="prose prose-sm max-w-none text-[var(--ba-text-primary)]">
        {@html segment.content}
      </div>

    {:else if segment.type === 'think' || segment.type === 'reasoning'}
      <ThinkPanel content={segment.content} isThinking={streaming} />

    {:else if segment.type === 'tool_call'}
      <ToolCallCard
        name={segment.name || 'unknown'}
        args={segment.arguments || ''}
        status={streaming ? 'running' : 'success'}
      />

    {:else if segment.type === 'tool_response'}
      <ToolResponseCard
        name={segment.name || 'unknown'}
        output={segment.output || ''}
      />
    {/if}
  {/each}

  <!-- Show partial content while streaming -->
  {#if streaming && partial}
    <div class="text-[var(--ba-text-secondary)] opacity-50 animate-pulse">
      {partial.content}
    </div>
  {/if}
</div>
