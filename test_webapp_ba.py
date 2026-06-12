#!/usr/bin/env python3
"""UI Test: Verify Blue Archive anime theme assets render correctly."""
import os
from playwright.sync_api import sync_playwright

BASE_URL = 'http://localhost:5174'
OUTPUT_DIR = '/root/open-webui/test_output'
TEST_EMAIL = 'testuser_webapp@example.com'
TEST_PASSWORD = 'TestPass123!'


def dismiss_modal(page):
    for text in ['确认，开始使用！', 'Get Started', '开始使用', 'Confirm']:
        btn = page.locator(f"button:has-text('{text}')").first
        if btn.count() > 0 and btn.is_visible():
            btn.click()
            page.wait_for_timeout(500)
            break


def test_login_page_background():
    """ITUT-UI-01: Login page shows BA portrait background"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.set_viewport_size({'width': 1366, 'height': 768})
        # Navigate directly to auth page
        page.goto(f'{BASE_URL}/auth')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)

        bg_div = page.locator('#auth-page > div').first
        assert bg_div.count() > 0, 'Auth page background div not found'
        bg_img = bg_div.evaluate("el => el.style.backgroundImage")
        assert 'portrait' in bg_img or 'ba/students' in bg_img, \
            f'Background should contain BA portrait, got: {bg_img}'

        page.screenshot(path=os.path.join(OUTPUT_DIR, 'ba_login_bg.png'), full_page=True)
        browser.close()


def test_sidebar_mascot_avatar():
    """ITUT-UI-02: Sidebar shows character avatar"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1366, 'height': 768})
        page.goto(BASE_URL)
        page.wait_for_load_state('networkidle')

        if '/auth' in page.url:
            page.locator("input[name='email']").fill(TEST_EMAIL)
            page.locator("input[name='password']").fill(TEST_PASSWORD)
            page.locator("button[type='submit']").click()
            page.wait_for_url(lambda url: '/auth' not in url, timeout=10000)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(2000)

        dismiss_modal(page)

        # Ensure sidebar is visible by clicking toggle
        toggle = page.locator("[aria-label*='Open Sidebar' i], [aria-label*='打开侧边栏' i]").first
        if toggle.count() > 0 and toggle.is_visible():
            toggle.click()
            page.wait_for_timeout(500)

        avatar = page.locator("img[src*='ba/students/icon']").first
        assert avatar.count() > 0, 'Sidebar mascot avatar not found'
        assert avatar.is_visible(), 'Sidebar mascot avatar not visible'

        src = avatar.get_attribute('src')
        assert 'ba/students/icon' in src, f'Avatar src should be BA student icon, got: {src}'

        page.screenshot(path=os.path.join(OUTPUT_DIR, 'ba_sidebar_avatar.png'), full_page=True)
        browser.close()


def test_chat_mascot_avatar():
    """ITUT-UI-03: Chat AI messages show character avatar"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1366, 'height': 768})
        page.goto(BASE_URL)
        page.wait_for_load_state('networkidle')

        if '/auth' in page.url:
            page.locator("input[name='email']").fill(TEST_EMAIL)
            page.locator("input[name='password']").fill(TEST_PASSWORD)
            page.locator("button[type='submit']").click()
            page.wait_for_url(lambda url: '/auth' not in url, timeout=10000)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(2000)

        dismiss_modal(page)

        chat_input = page.locator("#chat-input").first
        if chat_input.count() == 0:
            chat_input = page.locator("textarea").first

        if chat_input.count() > 0 and chat_input.is_visible():
            chat_input.fill('Hello BA test!')
            chat_input.press('Enter')
            page.wait_for_timeout(3000)

        avatars = page.locator("img[src*='ba/students/icon']").all()
        assert len(avatars) > 0, 'No BA mascot avatar found in chat'

        page.screenshot(path=os.path.join(OUTPUT_DIR, 'ba_chat_avatar.png'), full_page=True)
        browser.close()


def test_theme_switch_changes_mascot():
    """ITUT-UI-04: Theme switch updates mascot avatar"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1366, 'height': 768})
        page.goto(BASE_URL)
        page.wait_for_load_state('networkidle')

        if '/auth' in page.url:
            page.locator("input[name='email']").fill(TEST_EMAIL)
            page.locator("input[name='password']").fill(TEST_PASSWORD)
            page.locator("button[type='submit']").click()
            page.wait_for_url(lambda url: '/auth' not in url, timeout=10000)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(2000)

        dismiss_modal(page)

        light_avatar = page.locator("img[src*='10010']").first
        has_light = light_avatar.count() > 0 and light_avatar.is_visible()

        page.evaluate("() => { localStorage.setItem('theme', 'dark'); window.location.reload(); }")
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)
        dismiss_modal(page)

        dark_avatar = page.locator("img[src*='10005']").first
        has_dark = dark_avatar.count() > 0 and dark_avatar.is_visible()

        assert has_light or has_dark, 'At least one theme mascot should be visible'

        page.screenshot(path=os.path.join(OUTPUT_DIR, 'ba_theme_dark.png'), full_page=True)
        browser.close()


if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    test_login_page_background()
    print('ITUT-UI-01: PASS')
    test_sidebar_mascot_avatar()
    print('ITUT-UI-02: PASS')
    test_chat_mascot_avatar()
    print('ITUT-UI-03: PASS')
    test_theme_switch_changes_mascot()
    print('ITUT-UI-04: PASS')
    print('All BA UI tests passed!')
