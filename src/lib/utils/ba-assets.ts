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

export interface StudentAssetInfo {
	id: string;
	name: string;
	devName: string;
	icon: string;
	portrait: string;
	collection: string;
}

const STUDENT_DECORATIONS: Record<string, StudentAssetInfo[]> = {
	light: [
		{
			id: '10010',
			name: '白子',
			devName: 'Shiroko',
			icon: '/assets/ba/students/icon/10010.webp',
			portrait: '/assets/ba/students/portrait/10010.webp',
			collection: '/assets/ba/students/collection/10010.webp'
		},
		{
			id: '10015',
			name: '爱丽丝',
			devName: 'Aris',
			icon: '/assets/ba/students/icon/10015.webp',
			portrait: '/assets/ba/students/portrait/10015.webp',
			collection: '/assets/ba/students/collection/10015.webp'
		}
	],
	dark: [
		{
			id: '10005',
			name: '星野',
			devName: 'Hoshino',
			icon: '/assets/ba/students/icon/10005.webp',
			portrait: '/assets/ba/students/portrait/10005.webp',
			collection: '/assets/ba/students/collection/10005.webp'
		},
		{
			id: '10059',
			name: '未花',
			devName: 'Mika',
			icon: '/assets/ba/students/icon/10059.webp',
			portrait: '/assets/ba/students/portrait/10059.webp',
			collection: '/assets/ba/students/collection/10059.webp'
		}
	]
};

export function getStudentDecorations(theme: Theme): StudentAssetInfo[] {
	const effective = resolveEffectiveTheme(theme);
	return STUDENT_DECORATIONS[effective] ?? STUDENT_DECORATIONS.light;
}

export function getMascotForTheme(theme: Theme): MascotInfo {
	const effective = resolveEffectiveTheme(theme);
	return MASCOT_MAP[effective] ?? MASCOT_MAP['light'];
}

/**
 * Get mascot image path for a theme and image type.
 */
export function getMascotImagePath(theme: Theme, type: 'icon' | 'portrait' | 'collection'): string {
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
