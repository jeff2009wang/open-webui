<script lang="ts">
	export let src = '/assets/ba/mascots/arona.png';
	export let alt = 'Blue Archive character';
	export let side: 'left' | 'right' = 'left';
	export let compact = false;
	export let className = '';
</script>

<div
	class="ba-character-portrait ba-character-portrait-{side} {compact
		? 'ba-character-portrait-compact'
		: ''} {className}"
>
	<div class="ba-character-halo"></div>
	<img {src} {alt} draggable="false" />
</div>
