<script lang="ts">
	export let title = 'Arona';
	export let subtitle = '';
	export let side: 'assistant' | 'user' = 'assistant';
	export let className = '';
</script>

<div class="ba-nameplate ba-nameplate-{side} {className}">
	<span class="ba-nameplate-kicker">{side === 'assistant' ? 'Schale' : 'Sensei'}</span>
	<span class="ba-nameplate-title">{title}</span>
	{#if subtitle}
		<span class="ba-nameplate-subtitle">{subtitle}</span>
	{/if}
</div>
