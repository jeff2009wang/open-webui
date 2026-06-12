#!/usr/bin/env python3
"""Debug: force loading=false and inspect chat UI"""
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5174"
TEST_EMAIL = "testuser_webapp@example.com"
TEST_PASSWORD = "TestPass123!"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1366, "height": 768})

    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    if "/auth" in page.url:
        page.locator("input[name='email']").fill(TEST_EMAIL)
        page.locator("input[name='password']").fill(TEST_PASSWORD)
        page.locator("button[type='submit']").click()
        page.wait_for_url(lambda url: "/auth" not in url, timeout=10000)
        page.wait_for_load_state("networkidle")

    page.wait_for_timeout(5000)
    print(f"URL: {page.url}")

    # Try to find and click modal dismiss
    for text in ["确认，开始使用！", "Get Started", "开始使用", "Confirm"]:
        btn = page.locator(f"button:has-text('{text}')").first
        if btn.count() > 0 and btn.is_visible():
            btn.click()
            page.wait_for_timeout(500)
            break

    page.wait_for_timeout(2000)

    # Check if chat-input exists
    chat_input = page.locator("#chat-input, textarea, [contenteditable='true']").first
    print(f"Chat input visible: {chat_input.count() > 0 and chat_input.is_visible()}")

    # Get all body text for debugging
    body_text = page.inner_text("body")
    print(f"\nBody text (first 800 chars):\n{body_text[:800]}")

    # Look for any error messages or empty states
    if "没有" in body_text or "No" in body_text or "available" in body_text.lower():
        print("\nFound empty-state message!")

    # Check models via evaluate
    models_info = page.evaluate("""
        async () => {
            try {
                const res = await fetch('http://localhost:8080/api/models', {
                    headers: { 'Authorization': 'Bearer ' + localStorage.token }
                });
                const data = await res.json();
                return { count: data.data?.length || 0, models: data.data?.map(m => m.id) || [] };
            } catch(e) {
                return { error: e.message };
            }
        }
    """)
    print(f"\nModels: {models_info}")

    page.screenshot(path="/root/open-webui/test_output/recon_loading_debug.png", full_page=True)
    browser.close()
