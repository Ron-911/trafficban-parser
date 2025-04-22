# session_manager.py
import random
from playwright.async_api import async_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
]

VIEWPORTS = [
    {"width": 1280, "height": 720},
    {"width": 1920, "height": 1080},
    {"width": 375, "height": 667},  # мобильный
]

async def get_browser_context(proxy=None):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)

    context_args = {
        "user_agent": random.choice(USER_AGENTS),
        "viewport": random.choice(VIEWPORTS),
        "java_script_enabled": True,
    }

    if proxy:
        context_args["proxy"] = {"server": proxy}

    context = await browser.new_context(**context_args)
    return playwright, browser, context
