#!/usr/bin/env python3
"""Deep recon: inspect login page for register toggle, hidden elements"""
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5174"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    print("=== FULL PAGE TEXT ===")
    text = page.inner_text("body")
    print(text[:2000])

    print("\n=== BUTTON DETAILS ===")
    buttons = page.locator("button").all()
    for i, btn in enumerate(buttons):
        print(f"  [{i}] text='{btn.inner_text().strip()}' outerHTML={btn.evaluate('el => el.outerHTML')[:100]}")

    print("\n=== LOOKING FOR REGISTER/创建账号/Sign up ===")
    # Search in full HTML
    html = page.content()
    if "注册" in html:
        print("Found '注册' in HTML")
    if "创建" in html:
        print("Found '创建' in HTML")
    if "signup" in html.lower():
        print("Found 'signup' in HTML")
    if "register" in html.lower():
        print("Found 'register' in HTML")

    # Check for any clickable elements that might toggle signup
    all_clickable = page.locator("a, button, [role='button']").all()
    print(f"\nAll clickable elements ({len(all_clickable)}):")
    for i, el in enumerate(all_clickable):
        if el.is_visible():
            txt = el.inner_text().strip()[:50]
            tag = el.evaluate("el => el.tagName")
            print(f"  [{i}] <{tag}> '{txt}'")

    # Try clicking the first empty button (might be theme toggle)
    empty_btn = page.locator("button[class*='bg-transparent']").first
    if empty_btn.count() > 0:
        print("\nClicking transparent button...")
        empty_btn.click()
        page.wait_for_timeout(300)
        print(f"Theme after click: {page.evaluate('() => document.documentElement.getAttribute(\"data-theme\")')}")

    # Try to find toggle between login/signup (tab-like)
    print("\n=== LOOKING FOR TABS ===")
    tabs = page.locator("[role='tab'], .tab, [class*='tab']").all()
    for t in tabs:
        if t.is_visible():
            print(f"Tab: '{t.inner_text().strip()}'")

    browser.close()
