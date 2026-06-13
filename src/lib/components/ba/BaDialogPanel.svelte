<script lang="ts">
	export let side: 'assistant' | 'user' = 'assistant';
	export let className = '';
	export let contentClassName = '';
</script>

<section class="ba-dialog-panel ba-dialog-panel-{side} {className}">
	<div class="ba-dialog-corner ba-dialog-corner-left"></div>
	<div class="ba-dialog-corner ba-dialog-corner-right"></div>
	<div class="ba-dialog-panel-header">
		<slot name="nameplate" />
	</div>
	<div class="ba-dialog-content {contentClassName}">
		<slot />
	</div>
</section>
