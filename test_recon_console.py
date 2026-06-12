#!/usr/bin/env python3
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5174"
TEST_EMAIL = "testuser_webapp@example.com"
TEST_PASSWORD = "TestPass123!"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1366, "height": 768})

    console_logs = []
    page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: console_logs.append(f"[PAGEERROR] {err}"))

    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    if "/auth" in page.url:
        page.locator("input[name='email']").fill(TEST_EMAIL)
        page.locator("input[name='password']").fill(TEST_PASSWORD)
        page.locator("button[type='submit']").click()
        page.wait_for_url(lambda url: "/auth" not in url, timeout=10000)
        page.wait_for_load_state("networkidle")

    page.wait_for_timeout(5000)

    print("=== CONSOLE LOGS ===")
    for log in console_logs:
        print(log)

    # Check network requests
    print("\n=== CHECKING API CALLS VIA PAGE EVALUATE ===")
    models_res = page.evaluate("""
        async () => {
            try {
                const res = await fetch('/api/models', { headers: { 'Authorization': 'Bearer ' + localStorage.token } });
                return { status: res.status, text: await res.text() };
            } catch(e) {
                return { error: e.message };
            }
        }
    """)
    print(f"Models API: {models_res}")

    page.screenshot(path="/root/open-webui/test_output/recon_console.png", full_page=True)
    browser.close()
