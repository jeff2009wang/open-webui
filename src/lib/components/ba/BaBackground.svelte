<script lang="ts">
	import { theme } from '$lib/stores/theme';
	import { getMascotImagePath, getStudentDecorations } from '$lib/utils/ba-assets';

	export let dense = false;
	$: decorations = getStudentDecorations($theme);
	$: mascot = getMascotImagePath($theme, 'portrait');
</script>

<div class="ba-background {dense ? 'ba-background-dense' : ''}" aria-hidden="true">
	<div class="ba-background-grid"></div>
	<div class="ba-background-glow ba-background-glow-a"></div>
	<div class="ba-background-glow ba-background-glow-b"></div>
	<img class="ba-background-mascot" src={mascot} alt="" draggable="false" />
	{#each decorations as item, idx}
		<img
			class="ba-background-student ba-background-student-{idx}"
			src={item.collection}
			alt=""
			draggable="false"
		/>
	{/each}
</div>
