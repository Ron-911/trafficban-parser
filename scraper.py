import csv
import asyncio
from playwright.async_api import async_playwright

country_urls = {
    "Poland": "https://trafficban.com/country.poland.home.151.ru.html",
    # добавьте остальные страны по аналогии
}

async def parse_country(page, country, url):
    await page.goto(url)
    await page.wait_for_selector('tbody.tCo')
    bans = await page.query_selector_all('tbody.tCo tr')
    results = []

    for ban in bans:
        date = await ban.query_selector_eval('td:nth-child(2)', 'el => el.textContent.trim()')
        time_range = await ban.query_selector_eval('td:nth-child(3)', 'el => el.textContent.trim()')
        results.append([country, date, time_range])

    return results

async def main():
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        for country, url in country_urls.items():
            country_bans = await parse_country(page, country, url)
            results.extend(country_bans)

        await browser.close()

    unique_results = []
    seen = set()

    for row in results:
        row_tuple = tuple(row)
        if row_tuple not in seen:
            seen.add(row_tuple)
            unique_results.append(row)

    os.makedirs('data', exist_ok=True)
    with open('data/bans.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Country', 'Date', 'Time Ranges'])
        writer.writerows(unique_results)

if __name__ == '__main__':
    asyncio.run(main())