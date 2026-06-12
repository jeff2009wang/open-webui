/**
 * Blue Archive asset utilities.
 * Maps theme to character images, with fallback to SVG placeholders.
 */

import { resolveEffectiveTheme, type Theme } from '$lib/stores/theme';

export interface MascotInfo {
	id: string;
	name: string;
	icon: string;
	portrait: string;
	collection: string;
}

const MASCOT_MAP: Record<string, MascotInfo> = {
	light: {
		id: 'arona',
		name: '阿罗娜',
		icon: '/assets/ba/mascots/arona-icon.png',
		portrait: '/assets/ba/mascots/arona.png',
		collection: '/assets/ba/mascots/arona.png'
	},
	dark: {
		id: 'plana',
		name: '普拉娜',
		icon: '/assets/ba/mascots/plana-icon.png',
		portrait: '/assets/ba/mascots/plana.png',
		collection: '/assets/ba/mascots/plana.png'
	}
};

export function getMascotForTheme(theme: Theme): MascotInfo {
	const effective = resolveEffectiveTheme(theme);
	return MASCOT_MAP[effective] ?? MASCOT_MAP['light'];
}

/**
 * Get mascot image path for a theme and image type.
 */
export function getMascotImagePath(
	theme: Theme,
	type: 'icon' | 'portrait' | 'collection'
): string {
	const mascot = getMascotForTheme(theme);
	return mascot[type];
}

/**
 * Generate CSS style for portrait background with fallback color.
 */
export function getPortraitBgStyle(theme: Theme): string {
	const path = getMascotImagePath(theme, 'portrait');
	const effective = resolveEffectiveTheme(theme);
	const fallback = effective === 'dark' ? '#0a0a0a' : '#ffffff';
	return `background-image: url(${path}); background-size: cover; background-position: top center; background-color: ${fallback};`;
}
