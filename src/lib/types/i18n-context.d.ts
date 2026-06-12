import type { Writable } from 'svelte/store';
import type { i18n as i18nType } from 'i18next';

declare module 'svelte' {
	// Provide a precise return type for the i18n context so components don't need
	// to cast getContext('i18n') everywhere.
	export function getContext(key: 'i18n'): Writable<i18nType>;
}
