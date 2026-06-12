#!/usr/bin/env python3
"""
Blue Archive Open WebUI - Comprehensive Web Test (Final)
Covers: homepage, theme switching, login + chat flow, responsive layout
"""
import os
import time
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5174"
OUTPUT_DIR = "/root/open-webui/test_output"
TEST_EMAIL = "testuser_webapp@example.com"
TEST_PASSWORD = "TestPass123!"

def log(msg):
    print(f"[TEST] {msg}")

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def test_homepage_screenshots(page):
    """Test 1: Homepage at desktop resolution"""
    log("=== 1. HOMEPAGE SCREENSHOT ===")
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)

    path = os.path.join(OUTPUT_DIR, "homepage_desktop.png")
    page.screenshot(path=path, full_page=True)
    log(f"Screenshot: {path}")

    theme = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
    has_vars = page.evaluate("""() => {
        const s = getComputedStyle(document.documentElement);
        return s.getPropertyValue('--ba-bg-primary').trim() !== '';
    }""")
    log(f"Theme: {theme}, BA CSS vars: {has_vars}")
    return {"theme": theme, "has_css_vars": has_vars}

def test_theme_switching(page):
    """Test 2: Theme light <-> dark via localStorage"""
    log("=== 2. THEME SWITCHING ===")
    page.set_viewport_size({"width": 1366, "height": 768})
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    initial = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
    log(f"Initial: {initial}")

    # Dark
    page.evaluate("() => localStorage.setItem('theme', 'dark')")
    page.reload()
    page.wait_for_load_state("networkidle")
    dark = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
    log(f"After dark: {dark}")

    # Light
    page.evaluate("() => localStorage.setItem('theme', 'light')")
    page.reload()
    page.wait_for_load_state("networkidle")
    light = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
    log(f"After light: {light}")

    return {"initial": initial, "dark": dark, "light": light}

def test_chat_flow(page):
    """Test 3: Login -> Chat -> Send Message"""
    log("=== 3. CHAT FLOW ===")
    page.set_viewport_size({"width": 1366, "height": 768})
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    results = {}

    # We should be on /auth page
    if "/auth" in page.url:
        log("On auth page, logging in...")
        page.locator("input[name='email']").fill(TEST_EMAIL)
        page.locator("input[name='password']").fill(TEST_PASSWORD)
        page.locator("button[type='submit']").click()

        # Wait for redirect to home
        page.wait_for_url(lambda url: "/auth" not in url, timeout=10000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        log(f"Logged in, URL: {page.url}")
        results["login"] = "success"

        # Dismiss changelog/update modal if present
        for btn_text in ["确认，开始使用！", "Get Started", "开始使用", "Confirm"]:
            btn = page.locator(f"button:has-text('{btn_text}')").first
            if btn.count() > 0 and btn.is_visible():
                log(f"Dismissing modal: '{btn_text}'")
                btn.click()
                page.wait_for_timeout(1000)
                break
    else:
        log(f"Not on auth page, URL: {page.url}")
        results["login"] = "skipped"

    # Take screenshot of post-login state
    page.screenshot(path=os.path.join(OUTPUT_DIR, "post_login.png"), full_page=True)

    # Wait for chat UI to load and look for chat input
    page.wait_for_timeout(2000)
    chat_input = page.locator("#chat-input").first
    if chat_input.count() == 0 or not chat_input.is_visible():
        chat_input = page.locator("textarea").first
    if chat_input.count() == 0 or not chat_input.is_visible():
        chat_input = page.locator("[contenteditable='true']").first

    if chat_input.count() > 0 and chat_input.is_visible():
        log("Chat input found")
        results["chat_input"] = "found"

        # Check for Blue Archive themed elements
        body_text = page.inner_text("body")
        if "阿罗纳" in body_text or "普拉纳" in body_text or "Schale" in body_text:
            log("Blue Archive character content detected")
            results["ba_theme"] = True
        else:
            results["ba_theme"] = False

        # Try to send a message
        msg = "Hello Arona! This is an automated test message."
        chat_input.fill(msg)
        page.wait_for_timeout(200)

        # Try to find send button
        send_btn = page.locator("button[aria-label*='send' i], button:has-text('Send')").first
        if send_btn.count() == 0:
            # Look for any button near the input
            send_btn = page.locator("button").filter(has_text="").first

        if send_btn.count() > 0 and send_btn.is_visible():
            send_btn.click()
            log("Send button clicked")
        else:
            # Press Enter
            chat_input.press("Enter")
            log("Pressed Enter to send")

        page.wait_for_timeout(2000)

        # Check for messages
        messages = page.locator(".message, .chat-message, [data-message], .group").all()
        log(f"Message elements found: {len(messages)}")
        results["messages_count"] = len(messages)

        page.screenshot(path=os.path.join(OUTPUT_DIR, "chat_after_send.png"), full_page=True)
    else:
        log("Chat input not found")
        results["chat_input"] = "not_found"
        # Dump body text for debugging
        text = page.inner_text("body")[:500]
        log(f"Body text: {text}")

    return results

def test_responsive_layout(page):
    """Test 4: Responsive at multiple breakpoints"""
    log("=== 4. RESPONSIVE LAYOUT ===")
    breakpoints = [
        ("mobile_s", 375, 667),
        ("mobile_l", 414, 896),
        ("tablet", 768, 1024),
        ("laptop", 1366, 768),
        ("desktop", 1920, 1080),
    ]
    results = {}
    for name, w, h in breakpoints:
        page.set_viewport_size({"width": w, "height": h})
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(300)

        path = os.path.join(OUTPUT_DIR, f"responsive_{name}.png")
        page.screenshot(path=path, full_page=True)

        metrics = page.evaluate("""
            () => ({
                width: window.innerWidth,
                height: window.innerHeight,
                scrollWidth: document.documentElement.scrollWidth,
                hasHScroll: document.documentElement.scrollWidth > window.innerWidth,
            })
        """)
        metrics["screenshot"] = path
        results[name] = metrics
        log(f"{name}: {w}x{h} h-scroll={metrics['hasHScroll']}")
    return results

def main():
    ensure_dir(OUTPUT_DIR)
    log(f"Testing {BASE_URL}")

    all_results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Each test gets fresh page to avoid state pollution
        for test_fn in [test_homepage_screenshots, test_theme_switching, test_chat_flow, test_responsive_layout]:
            page = browser.new_page()
            try:
                result = test_fn(page)
                all_results[test_fn.__name__] = result
            except Exception as e:
                log(f"ERROR in {test_fn.__name__}: {e}")
                all_results[test_fn.__name__] = {"error": str(e)}
                page.screenshot(path=os.path.join(OUTPUT_DIR, f"error_{test_fn.__name__}.png"), full_page=True)
            finally:
                page.close()

        browser.close()

    log("\n" + "="*50)
    log("FINAL SUMMARY")
    log("="*50)
    for section, data in all_results.items():
        log(f"\n{section}:")
        for k, v in data.items():
            log(f"  {k}: {v}")
    log(f"\nAll artifacts: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
