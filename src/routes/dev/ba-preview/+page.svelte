<script lang="ts">
	import BaBackground from '$lib/components/ba/BaBackground.svelte';
	import BaCharacterPortrait from '$lib/components/ba/BaCharacterPortrait.svelte';
	import BaDialogPanel from '$lib/components/ba/BaDialogPanel.svelte';
	import BaNameplate from '$lib/components/ba/BaNameplate.svelte';
	import BaButton from '$lib/components/ba/BaButton.svelte';
	import { getMascotImagePath, getStudentDecorations } from '$lib/utils/ba-assets';
	import { theme } from '$lib/stores/theme';

	$: students = getStudentDecorations($theme);
</script>

<svelte:head>
	<title>Blue Archive UI Preview</title>
</svelte:head>

<div class="relative min-h-screen overflow-hidden text-[var(--ba-text-primary)]">
	<BaBackground dense={true} />

	<main
		class="relative z-10 mx-auto flex min-h-screen w-full max-w-6xl flex-col justify-center gap-8 px-6 py-12"
	>
		<section class="grid items-end gap-6 md:grid-cols-[12rem_1fr]">
			<BaCharacterPortrait
				src={getMascotImagePath($theme, 'portrait')}
				alt="Arona"
				className="!flex"
			/>
			<BaDialogPanel side="assistant">
				<svelte:fragment slot="nameplate">
					<BaNameplate title="阿罗娜" subtitle="Schale OS" />
				</svelte:fragment>
				<div class="space-y-3 text-base leading-7">
					<p>Sensei，欢迎回到 Schale！这是重构后的蔚蓝档案式对话框预览。</p>
					<p>这里使用角色立绘、名牌、对白框和背景素材层，而不是只靠原始聊天 DOM 上套 CSS。</p>
				</div>
			</BaDialogPanel>
		</section>

		<section class="flex justify-end">
			<BaDialogPanel side="user" className="ba-user-dialog-panel max-w-2xl">
				<svelte:fragment slot="nameplate">
					<BaNameplate side="user" title="Sensei" subtitle="Preview" />
				</svelte:fragment>
				<p>这次需要看起来像游戏里的对话 UI，而不是普通网页聊天气泡。</p>
			</BaDialogPanel>
		</section>

		<section class="grid gap-4 md:grid-cols-4">
			{#each students as student}
				<div class="ba-card p-4 text-center">
					<img src={student.collection} alt={student.name} class="mx-auto h-36 object-contain" />
					<div class="mt-2 text-sm font-bold">{student.name}</div>
					<div class="text-xs text-[var(--ba-text-secondary)]">{student.devName}</div>
				</div>
			{/each}
		</section>

		<div class="flex justify-center gap-3">
			<BaButton className="px-5 py-2.5">开始对话</BaButton>
			<BaButton variant="ghost" className="px-5 py-2.5">查看素材</BaButton>
		</div>
	</main>
</div>
