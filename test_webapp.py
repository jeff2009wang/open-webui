#!/usr/bin/env python3
"""
Blue Archive Open WebUI - Comprehensive Web Test
Covers: homepage screenshots, theme switching, chat flow, responsive layout
"""
import os
import time
from playwright.sync_api import sync_playwright, expect

BASE_URL = "http://localhost:5174"
OUTPUT_DIR = "/root/open-webui/test_output"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def log(msg):
    print(f"[TEST] {msg}")

def test_homepage_screenshots(page, viewport_name, width, height):
    """Test 1: Homepage screenshot at given resolution"""
    log(f"=== Homepage Screenshot: {viewport_name} ({width}x{height}) ===")
    page.set_viewport_size({"width": width, "height": height})
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    # Wait a bit for any JS animations
    page.wait_for_timeout(500)

    # Take full page screenshot
    screenshot_path = os.path.join(OUTPUT_DIR, f"homepage_{viewport_name}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    log(f"Saved: {screenshot_path}")

    # Check data-theme attribute
    theme = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
    log(f"Current theme: {theme}")

    # Check CSS variables exist
    has_ba_bg = page.evaluate("""
        () => {
            const style = getComputedStyle(document.documentElement);
            return style.getPropertyValue('--ba-bg-primary').trim() !== '';
        }
    """)
    log(f"Blue Archive CSS vars present: {has_ba_bg}")
    return {"theme": theme, "has_css_vars": has_ba_bg}

def test_theme_switching(page):
    """Test 2: Theme switching light <-> dark"""
    log("=== Theme Switching Test ===")
    page.set_viewport_size({"width": 1366, "height": 768})
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    # Check initial theme
    initial_theme = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
    log(f"Initial theme: {initial_theme}")

    # Try to find theme toggle button (usually in header/sidebar)
    # First, let's inspect what buttons are available
    buttons = page.locator("button").all()
    log(f"Found {len(buttons)} buttons on page")

    # Look for theme-related buttons by aria-label or title
    theme_btn = page.locator("[aria-label*='theme' i], [title*='theme' i], [aria-label*='Theme' i]").first
    if theme_btn.count() == 0:
        # Try common theme toggle selectors
        theme_btn = page.locator("button:has(.lucide-sun), button:has(.lucide-moon), .theme-toggle").first

    if theme_btn.count() > 0:
        log("Found theme toggle button, clicking...")
        theme_btn.click()
        page.wait_for_timeout(300)
        new_theme = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
        log(f"After toggle theme: {new_theme}")

        # Toggle back
        theme_btn.click()
        page.wait_for_timeout(300)
        final_theme = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
        log(f"After second toggle: {final_theme}")
        return {"initial": initial_theme, "toggled": new_theme, "restored": final_theme}
    else:
        log("No theme toggle button found via common selectors")
        # Try via localStorage manipulation as fallback
        page.evaluate("() => localStorage.setItem('theme', 'dark')")
        page.reload()
        page.wait_for_load_state("networkidle")
        dark_theme = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
        log(f"After localStorage 'dark': {dark_theme}")

        page.evaluate("() => localStorage.setItem('theme', 'light')")
        page.reload()
        page.wait_for_load_state("networkidle")
        light_theme = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
        log(f"After localStorage 'light': {light_theme}")
        return {"initial": initial_theme, "localstorage_dark": dark_theme, "localstorage_light": light_theme}

def test_chat_flow(page):
    """Test 3: Register -> Login -> Create Chat -> Send Message"""
    log("=== Chat Flow Test ===")
    page.set_viewport_size({"width": 1366, "height": 768})
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    results = {}

    # Check if we're already logged in or need to register
    # Look for login/register links or chat interface
    page_content = page.content()

    # Try to find "Sign up" or "Register" button/link
    signup_locators = [
        page.locator("text=Sign up").first,
        page.locator("text=Register").first,
        page.locator("text=Create account").first,
        page.locator("a[href*='register']").first,
        page.locator("a[href*='signup']").first,
    ]

    signup_found = False
    for loc in signup_locators:
        if loc.count() > 0 and loc.is_visible():
            log(f"Found signup element: {loc.inner_text()}")
            loc.click()
            page.wait_for_load_state("networkidle")
            signup_found = True
            break

    if not signup_found:
        # Check if we're already on a page with auth forms
        if page.locator("input[name='email'], input[name='username']").count() > 0:
            log("Auth form already visible")
            signup_found = True
        else:
            log("No signup link found, might need different approach")
            # Take screenshot to see current state
            page.screenshot(path=os.path.join(OUTPUT_DIR, "pre_auth_state.png"), full_page=True)

    if signup_found:
        # Fill registration form
        try:
            # Wait for form to appear
            page.wait_for_selector("input[type='email'], input[name='email'], input[name='username']", timeout=5000)

            # Determine form fields
            email_input = page.locator("input[type='email']").first
            if email_input.count() == 0:
                email_input = page.locator("input[name='email']").first
            if email_input.count() == 0:
                email_input = page.locator("input[name='username']").first

            password_input = page.locator("input[type='password']").first
            name_input = page.locator("input[name='name']").first

            if email_input.count() > 0 and password_input.count() > 0:
                test_email = "testuser_webapp@example.com"
                test_password = "TestPass123!"
                test_name = "TestUser"

                email_input.fill(test_email)
                password_input.fill(test_password)

                if name_input.count() > 0:
                    name_input.fill(test_name)

                # Look for confirm password
                confirm_password = page.locator("input[name='password_confirm']").first
                if confirm_password.count() > 0:
                    confirm_password.fill(test_password)

                # Submit form
                submit_btn = page.locator("button[type='submit']").first
                if submit_btn.count() > 0:
                    log("Submitting registration form...")
                    submit_btn.click()
                    page.wait_for_load_state("networkidle")
                    page.wait_for_timeout(1000)

                    # Check result - look for chat interface or error
                    if page.locator("textarea, .chat-input, [contenteditable]").count() > 0:
                        log("Registration successful, chat interface detected")
                        results["registration"] = "success"
                    elif page.locator("text=already exists").count() > 0 or page.locator("text=already taken").count() > 0:
                        log("User already exists, trying login...")
                        results["registration"] = "user_exists"
                        # Try login instead
                        test_login(page, test_email, test_password)
                    else:
                        log("Registration result unclear")
                        page.screenshot(path=os.path.join(OUTPUT_DIR, "post_register.png"), full_page=True)
                        results["registration"] = "unclear"
                else:
                    log("No submit button found")
                    results["registration"] = "no_submit_btn"
            else:
                log("Required form fields not found")
                results["registration"] = "missing_fields"
        except Exception as e:
            log(f"Registration error: {e}")
            results["registration"] = f"error: {e}"
            page.screenshot(path=os.path.join(OUTPUT_DIR, "register_error.png"), full_page=True)
    else:
        results["registration"] = "skipped"

    # If we're logged in, try sending a message
    chat_input = page.locator("textarea").first
    if chat_input.count() == 0:
        chat_input = page.locator("[contenteditable='true']").first

    if chat_input.count() > 0 and chat_input.is_visible():
        log("Chat input found, attempting to send message...")
        chat_input.fill("Hello, this is a test message from automated testing!")
        page.wait_for_timeout(200)

        # Find send button
        send_btn = page.locator("button:has-text('Send'), button[type='submit']").first
        if send_btn.count() > 0 and send_btn.is_visible():
            send_btn.click()
            page.wait_for_timeout(2000)  # Wait for response

            # Check for message bubbles
            messages = page.locator(".message, .chat-message, [data-message]").all()
            log(f"Found {len(messages)} messages")
            results["messages_sent"] = len(messages)
            page.screenshot(path=os.path.join(OUTPUT_DIR, "chat_with_messages.png"), full_page=True)
        else:
            # Try pressing Enter
            chat_input.press("Enter")
            page.wait_for_timeout(2000)
            results["messages_sent"] = "enter_pressed"
    else:
        log("Chat input not found")
        results["chat_input"] = "not_found"

    return results

def test_login(page, email, password):
    """Helper: Login with credentials"""
    log(f"Attempting login for {email}...")
    # Navigate to login if not already there
    login_links = page.locator("text=Log in, text=Login, text=Sign in").all()
    for link in login_links:
        if link.is_visible():
            link.click()
            page.wait_for_load_state("networkidle")
            break

    email_input = page.locator("input[type='email'], input[name='email'], input[name='username']").first
    password_input = page.locator("input[type='password']").first

    if email_input.count() > 0 and password_input.count() > 0:
        email_input.fill(email)
        password_input.fill(password)
        submit = page.locator("button[type='submit']").first
        if submit.count() > 0:
            submit.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)
            log("Login submitted")

def test_responsive_layout(page):
    """Test 4: Responsive layout at multiple breakpoints"""
    log("=== Responsive Layout Test ===")
    breakpoints = [
        ("mobile_small", 375, 667),
        ("mobile_large", 414, 896),
        ("tablet", 768, 1024),
        ("laptop", 1366, 768),
        ("desktop", 1920, 1080),
    ]

    results = {}
    for name, w, h in breakpoints:
        log(f"Testing {name}: {w}x{h}")
        page.set_viewport_size({"width": w, "height": h})
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(300)

        # Screenshot
        path = os.path.join(OUTPUT_DIR, f"responsive_{name}.png")
        page.screenshot(path=path, full_page=True)
        log(f"Saved: {path}")

        # Gather layout metrics
        metrics = page.evaluate("""
            () => {
                return {
                    width: window.innerWidth,
                    height: window.innerHeight,
                    scrollWidth: document.documentElement.scrollWidth,
                    scrollHeight: document.documentElement.scrollHeight,
                    hasHorizontalScroll: document.documentElement.scrollWidth > window.innerWidth,
                    bodyChildren: document.body.children.length,
                };
            }
        """)
        metrics["screenshot"] = path
        results[name] = metrics
        log(f"Metrics: {metrics}")

    return results

def main():
    ensure_dir(OUTPUT_DIR)
    log(f"Output directory: {OUTPUT_DIR}")
    log(f"Testing URL: {BASE_URL}")

    all_results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Test 1: Homepage screenshots at standard desktop
        page = browser.new_page()
        result = test_homepage_screenshots(page, "desktop", 1920, 1080)
        all_results["homepage_desktop"] = result
        page.close()

        # Test 2: Theme switching
        page = browser.new_page()
        result = test_theme_switching(page)
        all_results["theme_switching"] = result
        page.close()

        # Test 3: Chat flow (register/login/message)
        page = browser.new_page()
        result = test_chat_flow(page)
        all_results["chat_flow"] = result
        page.close()

        # Test 4: Responsive layout
        page = browser.new_page()
        result = test_responsive_layout(page)
        all_results["responsive_layout"] = result
        page.close()

        browser.close()

    # Summary
    log("=" * 50)
    log("TEST SUMMARY")
    log("=" * 50)
    for section, data in all_results.items():
        log(f"\n{section}:")
        if isinstance(data, dict):
            for k, v in data.items():
                log(f"  {k}: {v}")
        else:
            log(f"  {data}")

    log(f"\nAll screenshots saved to: {OUTPUT_DIR}")
    return all_results

if __name__ == "__main__":
    main()
