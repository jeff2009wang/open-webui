import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';

export type Theme = 'light' | 'dark' | 'system' | 'oled-dark' | 'her';

const VALID_THEMES: Theme[] = ['light', 'dark', 'system', 'oled-dark', 'her'];

function getSystemTheme(): 'light' | 'dark' {
	if (typeof window === 'undefined') return 'light';
	return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

/**
 * Resolve any stored theme value to a concrete UI theme.
 * Preserves special Open WebUI themes ('oled-dark', 'her') while mapping
 * 'system' to the current OS preference.
 */
export function normalizeTheme(value: string | null): Theme {
	if (value === 'oled-dark' || value === 'her') return value;
	if (value === 'dark') return 'dark';
	if (value === 'system') return 'system';
	// 'light' or any unknown value defaults to light
	return 'light';
}

/**
 * Return the concrete light/dark variant used for Tailwind classes,
 * Blue Archive mascot selection, and CSS variable application.
 */
export function resolveEffectiveTheme(theme: Theme): 'light' | 'dark' {
	if (theme === 'system') return getSystemTheme();
	if (theme === 'her') return 'dark'; // her theme is visually dark
	if (theme === 'oled-dark') return 'dark';
	return theme;
}

function updateHtmlClasses(effective: 'light' | 'dark', theme: Theme) {
	if (!browser) return;
	const html = document.documentElement;
	html.classList.remove('dark', 'light', 'her');

	if (theme === 'her') {
		// her theme is visually dark; keep 'dark' so Tailwind dark: variants work
		html.classList.add('her', 'dark');
	} else if (theme === 'oled-dark') {
		html.classList.add('dark');
	} else {
		html.classList.add(effective);
	}
}

function updateOledVars(isOled: boolean) {
	if (!browser) return;
	const html = document.documentElement;
	if (isOled) {
		html.style.setProperty('--color-gray-800', '#101010');
		html.style.setProperty('--color-gray-850', '#050505');
		html.style.setProperty('--color-gray-900', '#000000');
		html.style.setProperty('--color-gray-950', '#000000');
	} else {
		html.style.removeProperty('--color-gray-800');
		html.style.removeProperty('--color-gray-850');
		html.style.removeProperty('--color-gray-900');
		html.style.removeProperty('--color-gray-950');
	}
}

function updateMetaThemeColor(theme: Theme, effective: 'light' | 'dark') {
	if (!browser) return;
	const meta = document.querySelector('meta[name="theme-color"]');
	if (!meta) return;

	if (theme === 'oled-dark') {
		meta.setAttribute('content', '#000000');
	} else if (theme === 'her') {
		meta.setAttribute('content', '#983724');
	} else if (effective === 'dark') {
		meta.setAttribute('content', '#171717');
	} else {
		meta.setAttribute('content', '#ffffff');
	}
}

function applyTheme(theme: Theme) {
	if (!browser) return;
	const effective = resolveEffectiveTheme(theme);
	document.documentElement.setAttribute('data-theme', effective);
	updateHtmlClasses(effective, theme);
	updateOledVars(theme === 'oled-dark');
	updateMetaThemeColor(theme, effective);
}

function getInitialTheme(): Theme {
	if (!browser) return 'light';
	const stored = localStorage.getItem('theme');
	return normalizeTheme(stored);
}

function createThemeStore() {
	const initialTheme = getInitialTheme();
	const { subscribe, set: _set } = writable<Theme>(initialTheme);

	// Apply the initial theme immediately on the client so SSR/loader state
	// and the Svelte store stay in sync.
	applyTheme(initialTheme);

	if (browser) {
		const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
		mediaQuery.addEventListener('change', () => {
			const current = get({ subscribe });
			if (current === 'system') {
				applyTheme('system');
			}
		});
	}

	return {
		subscribe,
		set: (theme: Theme) => {
			if (!browser) return;
			const normalized = VALID_THEMES.includes(theme) ? theme : normalizeTheme(theme);
			localStorage.setItem('theme', normalized);
			applyTheme(normalized);
			_set(normalized);
		},
		toggle: () => {
			if (!browser) return;
			const current = get({ subscribe });
			const effective = resolveEffectiveTheme(current);
			const next: Theme = effective === 'light' ? 'dark' : 'light';
			localStorage.setItem('theme', next);
			applyTheme(next);
			_set(next);
		}
	};
}

export const theme = createThemeStore();
