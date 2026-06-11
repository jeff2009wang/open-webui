import { writable } from 'svelte/store';
import { browser } from '$app/environment';

type Theme = 'light' | 'dark';

function getInitialTheme(): Theme {
	if (!browser) return 'light';
	const stored = localStorage.getItem('theme') as Theme | null;
	if (stored) return stored;
	return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function createThemeStore() {
	const { subscribe, set } = writable<Theme>(getInitialTheme());

	return {
		subscribe,
		set: (theme: Theme) => {
			if (!browser) return;
			localStorage.setItem('theme', theme);
			document.documentElement.setAttribute('data-theme', theme);
			set(theme);
		},
		toggle: () => {
			if (!browser) return;
			const current = (document.documentElement.getAttribute('data-theme') as Theme) || 'light';
			const next = current === 'light' ? 'dark' : 'light';
			localStorage.setItem('theme', next);
			document.documentElement.setAttribute('data-theme', next);
			set(next);
		}
	};
}

export const theme = createThemeStore();
