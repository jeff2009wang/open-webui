#!/usr/bin/env python3
"""Recon script to inspect auth flow DOM structure"""
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5174"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1366, "height": 768})

    # Step 1: Load page and inspect initial state
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    print("=== INITIAL PAGE STATE ===")
    print(f"URL: {page.url}")
    print(f"Title: {page.title()}")

    # List all buttons
    buttons = page.locator("button").all()
    print(f"\nButtons ({len(buttons)}):")
    for i, btn in enumerate(buttons):
        text = btn.inner_text().strip() if btn.is_visible() else "(hidden)"
        print(f"  [{i}] text='{text}' class='{btn.get_attribute('class') or ''}'")

    # List all links
    links = page.locator("a").all()
    print(f"\nLinks ({len(links)}):")
    for i, link in enumerate(links[:20]):
        text = link.inner_text().strip() if link.is_visible() else "(hidden)"
        href = link.get_attribute("href") or ""
        print(f"  [{i}] text='{text}' href='{href}'")

    # List all inputs
    inputs = page.locator("input").all()
    print(f"\nInputs ({len(inputs)}):")
    for i, inp in enumerate(inputs):
        type_ = inp.get_attribute("type") or "text"
        name = inp.get_attribute("name") or ""
        placeholder = inp.get_attribute("placeholder") or ""
        print(f"  [{i}] type={type_} name={name} placeholder='{placeholder}'")

    # Check for form
    forms = page.locator("form").all()
    print(f"\nForms ({len(forms)}):")
    for i, form in enumerate(forms):
        action = form.get_attribute("action") or ""
        print(f"  [{i}] action='{action}'")

    # Try to find and click "Get Started" or similar
    print("\n=== LOOKING FOR AUTH ENTRY POINT ===")
    possible = page.locator("text=/get started|sign up|register|login|sign in/i").all()
    for el in possible:
        if el.is_visible():
            print(f"Found: '{el.inner_text().strip()}' tag={el.evaluate('el => el.tagName')}")

    # Screenshot for visual inspection
    page.screenshot(path="/root/open-webui/test_output/recon_initial.png", full_page=True)
    print("\nScreenshot saved: recon_initial.png")

    # Step 2: Try clicking first visible auth-related link/button
    get_started = page.locator("text=/get started/i").first
    if get_started.count() > 0 and get_started.is_visible():
        print("\nClicking 'Get Started'...")
        get_started.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)
        print(f"After click URL: {page.url}")

        # Re-inspect
        inputs = page.locator("input").all()
        print(f"Inputs now ({len(inputs)}):")
        for i, inp in enumerate(inputs):
            type_ = inp.get_attribute("type") or "text"
            name = inp.get_attribute("name") or ""
            print(f"  [{i}] type={type_} name={name}")

        page.screenshot(path="/root/open-webui/test_output/recon_after_click.png", full_page=True)
        print("Screenshot saved: recon_after_click.png")

    browser.close()
