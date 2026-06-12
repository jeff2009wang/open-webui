#!/usr/bin/env python3
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

    page.wait_for_timeout(3000)
    print(f"URL: {page.url}")

    # Inspect chat-container HTML
    chat_container = page.locator("#chat-container").first
    if chat_container.count() > 0:
        html = chat_container.evaluate("el => el.outerHTML")
        print(f"\n=== CHAT CONTAINER HTML (first 2000 chars) ===\n{html[:2000]}")
    else:
        print("No chat-container found")

    # Inspect modal HTML
    modal = page.locator("[role='dialog']").first
    if modal.count() > 0:
        html = modal.evaluate("el => el.outerHTML")
        print(f"\n=== MODAL HTML ===\n{html[:1500]}")

        # Try clicking the first button inside modal
        btns = modal.locator("button").all()
        print(f"\nModal buttons ({len(btns)}):")
        for i, b in enumerate(btns):
            txt = b.inner_text().strip()[:50]
            print(f"  [{i}] '{txt}'")
            if "确认" in txt or "开始" in txt:
                print(f"    Clicking button {i}...")
                b.click()
                page.wait_for_timeout(1000)
                break

    page.wait_for_timeout(2000)

    # After clicking, check chat container again
    chat_container = page.locator("#chat-container").first
    if chat_container.count() > 0:
        html = chat_container.evaluate("el => el.outerHTML")
        print(f"\n=== CHAT CONTAINER AFTER CLICK (first 3000 chars) ===\n{html[:3000]}")

    # Check for any placeholder text in the chat area
    placeholders = page.locator("[placeholder], [data-placeholder]").all()
    print(f"\nPlaceholders ({len(placeholders)}):")
    for p_el in placeholders:
        ph = p_el.get_attribute("placeholder") or p_el.get_attribute("data-placeholder") or ""
        print(f"  placeholder='{ph}'")

    page.screenshot(path="/root/open-webui/test_output/recon_chat_container.png", full_page=True)

    browser.close()
