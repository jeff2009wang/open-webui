// Global ambient patches for pre-existing strict-type gaps in the codebase.
// These augmentations silence common DOM and library interface mismatches
// without changing runtime behavior.

declare global {
	const google: any;
	const pdfjsLib: any;

	interface Window {
		electronAPI?: any;
		applyTheme?: any;
		pdfjsLib?: any;
	}

	interface Navigator {
		keyboard?: any;
		userLanguage?: string;
	}

	interface EventTarget {
		value?: any;
		click?: any;
		style?: any;
		classList?: any;
		src?: any;
		select?: any;
		path?: any;
		contentWindow?: any;
		error?: any;
		closest?: any;
		checked?: any;
	}

	interface Node {
		style?: any;
		classList?: any;
	}

	interface Element {
		click?: any;
		style?: any;
	}

	interface HTMLElement {
		select?: any;
	}

	interface CustomEvent<T = any> {
		key?: any;
	}
}

export {};
