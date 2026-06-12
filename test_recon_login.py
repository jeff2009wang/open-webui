#!/usr/bin/env python3
"""Recon: inspect post-login page DOM"""
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5174"
TEST_EMAIL = "testuser_webapp@example.com"
TEST_PASSWORD = "TestPass123!"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1366, "height": 768})

    # Login
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    if "/auth" in page.url:
        page.locator("input[name='email']").fill(TEST_EMAIL)
        page.locator("input[name='password']").fill(TEST_PASSWORD)
        page.locator("button[type='submit']").click()
        page.wait_for_url(lambda url: "/auth" not in url, timeout=10000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

    print(f"URL: {page.url}")
    print(f"Title: {page.title()}")

    # Screenshot
    page.screenshot(path="/root/open-webui/test_output/recon_post_login.png", full_page=True)
    print("Screenshot: recon_post_login.png")

    # Body text
    text = page.inner_text("body")
    print(f"\nBody text (first 800 chars):\n{text[:800]}")

    # All inputs
    inputs = page.locator("input, textarea, [contenteditable='true']").all()
    print(f"\nInputs/textarea/contenteditable ({len(inputs)}):")
    for i, inp in enumerate(inputs):
        tag = inp.evaluate("el => el.tagName")
        type_ = inp.get_attribute("type") or ""
        placeholder = inp.get_attribute("placeholder") or ""
        cls = (inp.get_attribute("class") or "")[:50]
        print(f"  [{i}] <{tag}> type={type_} placeholder='{placeholder}' class='{cls}'")

    # All buttons
    buttons = page.locator("button").all()
    print(f"\nButtons ({len(buttons)}):")
    for i, btn in enumerate(buttons[:15]):
        txt = btn.inner_text().strip()[:60]
        print(f"  [{i}] '{txt}'")

    # Check for models loaded
    print("\nChecking if models are loaded...")
    # Try calling API via page evaluate
    try:
        models = page.evaluate("""
            async () => {
                const res = await fetch('/api/models');
                return { status: res.status, text: await res.text() };
            }
        """)
        print(f"Models API: status={models['status']}, body={models['text'][:200]}")
    except Exception as e:
        print(f"Models API error: {e}")

    browser.close()
