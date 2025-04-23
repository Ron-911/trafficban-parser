from playwright.async_api import Browser, BrowserContext
import random

def generate_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Mobile/15E148 Safari/604.1",
    ]
    return random.choice(user_agents)

async def get_stealth_context(browser: Browser) -> BrowserContext:
    context = await browser.new_context(
        user_agent=generate_random_user_agent(),
        locale="en-US",
        viewport={"width": 1280, "height": 800},
    )

    # Удаляем следы автоматизации
    await context.add_init_script(
        """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"""
    )

    return context
