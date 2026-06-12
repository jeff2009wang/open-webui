#!/usr/bin/env python3
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5174"
TEST_EMAIL = "testuser_webapp@example.com"
TEST_PASSWORD = "TestPass123!"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1366, "height": 768})

    failed_requests = []
    def handle_route(route, request):
        route.continue_()

    def handle_response(response):
        if not response.url.startswith(BASE_URL) and not response.url.startswith("http://localhost:8080"):
            return
        content_type = response.headers.get('content-type', '')
        if response.status >= 400 or 'text/html' in content_type:
            failed_requests.append({
                'url': response.url,
                'status': response.status,
                'content_type': content_type[:50],
            })

    page.on("response", handle_response)

    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    if "/auth" in page.url:
        page.locator("input[name='email']").fill(TEST_EMAIL)
        page.locator("input[name='password']").fill(TEST_PASSWORD)
        page.locator("button[type='submit']").click()
        page.wait_for_url(lambda url: "/auth" not in url, timeout=10000)
        page.wait_for_load_state("networkidle")

    page.wait_for_timeout(5000)

    print("=== FAILED/OFF RESPONSES ===")
    for req in failed_requests:
        print(f"  {req['status']} {req['content_type']} {req['url'][:100]}")

    browser.close()
