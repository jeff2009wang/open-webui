<script lang="ts">
	// @ts-nocheck
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';
  import { HermesParser, type HermesSegment } from '$lib/utils/hermes-parser';
  import { getMascotImagePath } from '$lib/utils/ba-assets';
  import { theme } from '$lib/stores/theme';
  import ThinkPanel from './ThinkPanel.svelte';
  import ToolCallCard from './ToolCallCard.svelte';
  import ToolResponseCard from './ToolResponseCard.svelte';

  export let content: string = '';
  export let streaming = false;
  export let showAvatar = true;

  const parser = new HermesParser();
  let segments: HermesSegment[] = [];
  let partial: HermesSegment | null = null;
  let lastProcessedContent = '';
  let DOMPurify: typeof import('dompurify').default | null = null;

  onMount(async () => {
    if (browser) {
      DOMPurify = (await import('dompurify')).default;
    }
  });

  // Re-parse when content changes (for streaming)
  // Only feed the delta (new content since last update) to avoid duplication
  $: {
    if (content !== lastProcessedContent) {
      // If content was reset or replaced (doesn't start with previous), reset parser
      if (lastProcessedContent !== '' && !content.startsWith(lastProcessedContent)) {
        segments = [];
        parser.flush();
      }
      const delta = content.slice(lastProcessedContent.length);
      lastProcessedContent = content;
      if (delta) {
        const newSegments = parser.feed(delta);
        segments = [...segments, ...newSegments];
      }
    }
  }

  // Update partial for streaming display
  $: if (streaming) {
    partial = parser.getPartial();
  } else {
    partial = null;
  }

  // On final message, flush any remaining content
  $: if (!streaming && content !== undefined) {
    const flushed = parser.flush();
    if (flushed.length > 0) {
      segments = [...segments, ...flushed];
    }
  }

  onDestroy(() => {
    // Cleanup if needed
  });
</script>

<div class="hermes-message flex items-start gap-2">
  {#if showAvatar}
    <img
      src={getMascotImagePath($theme, 'icon')}
      alt="AI"
      class="w-6 h-6 rounded-full object-cover flex-shrink-0 mt-1"
      on:error={(e) => { e.currentTarget.style.display = 'none'; }}
    />
  {/if}
  <div class="flex-1">
    {#each segments as segment, index (`${segment.type}-${index}`)}
    {#if segment.type === 'text'}
      <div class="prose prose-sm max-w-none text-[var(--ba-text-primary)]">
        {#if DOMPurify}
          {@html DOMPurify.sanitize(segment.content)}
        {:else}
          {segment.content}
        {/if}
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
</div>
