#!/usr/bin/env node
import { spawn } from 'node:child_process';
import { mkdir } from 'node:fs/promises';
import { chromium } from '@playwright/test';

const port = process.env.PORT || '5174';
const baseUrl = `http://127.0.0.1:${port}`;
const outputDir = 'test-results/ba-ui';

const server = spawn('npm', ['run', 'dev', '--', '--port', port], {
	stdio: ['ignore', 'pipe', 'pipe'],
	detached: true,
	env: { ...process.env, CI: '1' }
});

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function waitForServer() {
	for (let i = 0; i < 60; i += 1) {
		try {
			const res = await fetch(`${baseUrl}/dev/ba-preview`);
			if (res.ok) return;
		} catch {
			// keep polling
		}
		await wait(1000);
	}
	throw new Error(`Timed out waiting for ${baseUrl}`);
}

async function run() {
	await mkdir(outputDir, { recursive: true });
	await waitForServer();

	const launchOptions = {};
	if (process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH) {
		launchOptions.executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH;
	}

	const browser = await chromium.launch(launchOptions);
	const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });

	for (const route of ['/dev/ba-preview', '/auth']) {
		await page.goto(`${baseUrl}${route}`, { waitUntil: 'networkidle', timeout: 60000 });
		await page.locator('.ba-background').first().waitFor({ timeout: 15000 });
		await page.locator('.ba-dialog-panel, .ba-card').first().waitFor({ timeout: 15000 });
		const name = route === '/auth' ? 'auth' : 'preview';
		await page.screenshot({ path: `${outputDir}/${name}.png`, fullPage: true });
	}

	await browser.close();
	console.log(`Blue Archive UI screenshots written to ${outputDir}`);
}

run()
	.catch((error) => {
		console.error(error);
		if (`${error?.message ?? ''}`.includes("Executable doesn't exist")) {
			console.error(
				'Playwright browser is missing. Run `npx playwright install chromium` or set PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH to a system Chromium.'
			);
		}
		process.exitCode = 1;
	})
	.finally(() => {
		try {
			process.kill(-server.pid, 'SIGTERM');
		} catch {
			server.kill('SIGTERM');
		}
	});
