<script lang="ts">
	export let type: 'button' | 'submit' | 'reset' = 'button';
	export let variant: 'primary' | 'ghost' = 'primary';
	export let className = '';
</script>

<button {type} class="ba-button ba-button-{variant} {className}" on:click>
	<slot />
</button>
