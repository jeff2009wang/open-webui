module.exports = {
	root: true,
	ignorePatterns: ['backend/open_webui/static/**', 'build/**', 'node_modules/**', '**/*.min.js'],
	extends: [
		'eslint:recommended',
		'plugin:@typescript-eslint/recommended',
		'plugin:svelte/recommended',
		'prettier'
	],
	parser: '@typescript-eslint/parser',
	plugins: ['@typescript-eslint'],
	parserOptions: {
		sourceType: 'module',
		ecmaVersion: 2020,
		extraFileExtensions: ['.svelte']
	},
	rules: {
		'@typescript-eslint/ban-ts-comment': 'off',
		'@typescript-eslint/no-empty-object-type': 'off',
		'@typescript-eslint/no-explicit-any': 'off',
		'@typescript-eslint/no-unsafe-function-type': 'off',
		'@typescript-eslint/no-unused-expressions': 'off',
		'@typescript-eslint/no-unused-vars': 'off',
		'no-async-promise-executor': 'off',
		'no-constant-condition': 'off',
		'no-control-regex': 'off',
		'no-empty': 'off',
		'no-ex-assign': 'off',
		'no-prototype-builtins': 'off',
		'no-undef': 'off',
		'no-unsafe-optional-chaining': 'off',
		'no-unused-expressions': 'off',
		'no-useless-escape': 'off',
		'svelte/no-at-html-tags': 'off',
		'svelte/no-inner-declarations': 'off',
		'svelte/no-unused-svelte-ignore': 'off',
		'svelte/valid-compile': ['error', { ignoreWarnings: true }]
	},
	env: {
		browser: true,
		es2017: true,
		node: true
	},
	overrides: [
		{
			files: ['*.svelte'],
			parser: 'svelte-eslint-parser',
			parserOptions: {
				parser: '@typescript-eslint/parser'
			}
		}
	]
};
