import csv
import asyncio
import os
from playwright.async_api import async_playwright

country_urls = {
    "Poland": "https://trafficban.com/country.poland.home.151.ru.html",
    # добавьте остальные страны по аналогии
}

async def parse_country(page, country, url):
    print(f"▶️ Visiting {url} for {country}")
    await page.goto(url)
    await asyncio.sleep(2)  # небольшая задержка

    await page.wait_for_selector('tbody.tCo')
    bans = await page.query_selector_all('tbody.tCo tr')
    results = []

    for ban in bans:
        date_el = await ban.query_selector('td:nth-child(2)')
        time_el = await ban.query_selector('td:nth-child(3)')

        if date_el and time_el:
            date = (await date_el.text_content()).strip()
            time_range = (await time_el.text_content()).strip()
            results.append([country, date, time_range])

    print(f"[{country}] Parsed {len(results)} rows")
    return results

async def main():
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
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

        for country, url in country_urls.items():
            country_bans = await parse_country(page, country, url)
            results.extend(country_bans)
            await asyncio.sleep(1)

        await browser.close()

    unique_results = []
    seen = set()

    for row in results:
        row_tuple = tuple(row)
        if row_tuple not in seen:
            seen.add(row_tuple)
            unique_results.append(row)

    print(f"✅ Total unique rows: {len(unique_results)}")

    os.makedirs('data', exist_ok=True)
    with open('data/bans.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Country', 'Date', 'Time Ranges'])
        writer.writerows(unique_results)

if __name__ == '__main__':
    asyncio.run(main())
