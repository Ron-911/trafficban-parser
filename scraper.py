import csv
import asyncio
import os
import random
from playwright.async_api import async_playwright

country_urls = {
    "Poland": "https://trafficban.com/country.poland.home.151.ru.html",
    "Germany": "https://trafficban.com/country.germany.home.135.ru.html",
    "France": "https://trafficban.com/country.france.home.56.ru.html"
    # Добавь другие страны при необходимости
}

# Прокси список (HTTP формат: ip:port)
proxies = [
    "http://user:pass@proxy1.example.com:8080",
    "http://user:pass@proxy2.example.com:8080",
    # Добавь свои рабочие прокси
]

async def parse_country(playwright, country, url):
    proxy = random.choice(proxies) if proxies else None
    launch_args = {"headless": True}
    if proxy:
        launch_args["proxy"] = {"server": proxy}

    browser = await playwright.chromium.launch(**launch_args)
    context = await browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0.0.0 Safari/537.36"
        ),
        locale="ru-RU",
        viewport={"width": 1280, "height": 800},
        device_scale_factor=1
    )

    await context.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    });
    """)
    page = await context.new_page()
    print(f"▶️ Visiting {url} for {country}")
    await page.goto(url)
    await asyncio.sleep(2)

    results = []
    try:
        await page.wait_for_selector('tbody.tCo', timeout=5000)
        bans = await page.query_selector_all('tbody.tCo tr')

        for ban in bans:
            date_el = await ban.query_selector('td:nth-child(2)')
            time_el = await ban.query_selector('td:nth-child(3)')

            if date_el and time_el:
                date = (await date_el.text_content()).strip()
                time_range = (await time_el.text_content()).strip()
                results.append([country, date, time_range])
    except:
        print(f"⚠️ [{country}] No data found")

    await browser.close()
    return results

async def main():
    results = []
    os.makedirs('data', exist_ok=True)

    async with async_playwright() as p:
        tasks = [
            parse_country(p, country, url)
            for country, url in country_urls.items()
        ]
        all_results = await asyncio.gather(*tasks)
        for result in all_results:
            results.extend(result)

    seen = set()
    unique_results = []
    for row in results:
        row_tuple = tuple(row)
        if row_tuple not in seen:
            seen.add(row_tuple)
            unique_results.append(row)

    print(f"✅ Total unique rows: {len(unique_results)}")

    with open('data/bans.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Country', 'Date', 'Time Ranges'])
        writer.writerows(unique_results)

if __name__ == '__main__':
    asyncio.run(main())
