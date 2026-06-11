import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';

type Theme = 'light' | 'dark';

const VALID_THEMES: Theme[] = ['light', 'dark'];

function normalizeTheme(value: string | null): Theme {
	if (value === 'dark') return 'dark';
	// Map old values and system preference to concrete theme
	if (value === 'system') {
		return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
	}
	// 'oled-dark', 'her', or any unknown → light as safe default
	return 'light';
}

function getInitialTheme(): Theme {
	if (!browser) return 'light';
	const stored = localStorage.getItem('theme');
	if (stored) return normalizeTheme(stored);
	return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function createThemeStore() {
	const { subscribe, set: _set } = writable<Theme>(getInitialTheme());

	return {
		subscribe,
		set: (theme: Theme) => {
			if (!browser) return;
			const normalized = VALID_THEMES.includes(theme) ? theme : normalizeTheme(theme);
			localStorage.setItem('theme', normalized);
			document.documentElement.setAttribute('data-theme', normalized);
			_set(normalized);
		},
		toggle: () => {
			if (!browser) return;
			const current = get({ subscribe });
			const next = current === 'light' ? 'dark' : 'light';
			localStorage.setItem('theme', next);
			document.documentElement.setAttribute('data-theme', next);
			_set(next);
		}
	};
}

export const theme = createThemeStore();
