import asyncio
import csv
import os
from playwright.async_api import async_playwright
from session_manager import get_stealth_context

OUTPUT_FILE = "data/bans.csv"
FAILED_FILE = "data/failed_countries.txt"

country_links = {
    "Albania": "https://trafficban.com/country.albania.home.2.ru.html",
    "Austria": "https://trafficban.com/country.austria.home.14.ru.html",
    "Belarus": "https://trafficban.com/country.belarus.home.25.ru.html",
    "Belgium": "https://trafficban.com/country.belgium.home.20.ru.html",
    "Bosnia and Herzegovina": "https://trafficban.com/country.bosnia_and_herzegovina.home.27.ru.html",
    "Bulgaria": "https://trafficban.com/country.bulgaria.home.32.ru.html",
    "Croatia": "https://trafficban.com/country.croatia.home.37.ru.html",
    "Czech Republic": "https://trafficban.com/country.czech_republic.home.41.ru.html",
    "Denmark": "https://trafficban.com/country.denmark.home.42.ru.html",
    "Estonia": "https://trafficban.com/country.estonia.home.50.ru.html",
    "Finland": "https://trafficban.com/country.finland.home.55.ru.html",
    "France": "https://trafficban.com/country.france.home.56.ru.html",
    "Germany": "https://trafficban.com/country.germany.home.135.ru.html",
    "Greece": "https://trafficban.com/country.greece.home.61.ru.html",
    "Hungary": "https://trafficban.com/country.hungary.home.212.ru.html",
    "Ireland": "https://trafficban.com/country.ireland.home.81.ru.html",
    "Italy": "https://trafficban.com/country.italy.home.213.ru.html",
    "Kazakhstan": "https://trafficban.com/country.kazakhstan.home.95.ru.html",
    "Latvia": "https://trafficban.com/country.latvia.home.110.ru.html",
    "Liechtenstein": "https://trafficban.com/country.liechtenstein.home.219.ru.html",
    "Lithuania": "https://trafficban.com/country.lithuania.home.108.ru.html",
    "Luxembourg": "https://trafficban.com/country.luxembourg.home.109.ru.html",
    "Macedonia": "https://trafficban.com/country.macedonia.home.111.ru.html",
    "Moldova": "https://trafficban.com/country.moldova.home.126.ru.html",
    "Montenegro": "https://trafficban.com/country.montenegro.home.40.ru.html",
    "Netherlands": "https://trafficban.com/country.netherlands.home.76.ru.html",
    "Norway": "https://trafficban.com/country.norway.home.140.ru.html",
    "Poland": "https://trafficban.com/country.poland.home.151.ru.html",
    "Portugal": "https://trafficban.com/country.portugal.home.153.ru.html",
    "Romania": "https://trafficban.com/country.romania.home.157.ru.html",
    "Russia": "https://trafficban.com/country.russia.home.52.ru.html",
    "Serbia": "https://trafficban.com/country.serbia.home.168.ru.html",
    "Slovakia": "https://trafficban.com/country.slovakia.home.172.ru.html",
    "Slovenia": "https://trafficban.com/country.slovenia.home.173.ru.html",
    "Spain": "https://trafficban.com/country.spain.home.75.ru.html",
    "Sweden": "https://trafficban.com/country.sweden.home.182.ru.html",
    "Switzerland": "https://trafficban.com/country.switzerland.home.181.ru.html",
    "Turkey": "https://trafficban.com/country.turkey.home.193.ru.html",
    "Ukraine": "https://trafficban.com/country.ukraine.home.198.ru.html",
    "United Kingdom": "https://trafficban.com/country.united_kingdom.home.205.ru.html",
}

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await get_stealth_context(browser)
        page = await context.new_page()

        existing_rows = set()
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)
                existing_rows = {tuple(row) for row in reader}

        new_rows = set()
        failed_countries = set()

        for country_name, url in country_links.items():
            try:
                await page.goto(url, timeout=60000)
                rows = await page.query_selector_all("table.ui.table tbody.tCo tr")
                has_data = False

                   for tr in rows:
                        tds = await tr.query_selector_all("td")
                        if len(tds) >= 3:
                            date = (await tds[1].inner_text()).strip()
                            time_range = (await tds[2].inner_text()).strip()
                            row = (country_name, date, time_range)
                                if row not in existing_rows:
                                    new_rows.add(row)
                                    has_data = True

                if not has_data:
                    failed_countries.add(country_name)

            except Exception as e:
                print(f"❌ Ошибка при загрузке {country_name}: {e}")
                failed_countries.add(country_name)

        await browser.close()

        if new_rows:
            write_header = not os.path.exists(OUTPUT_FILE) or os.path.getsize(OUTPUT_FILE) == 0
            with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(["Country", "Date", "Time Ranges"])
                writer.writerows(sorted(new_rows))

        if failed_countries:
            existing_failed = set()
            if os.path.exists(FAILED_FILE):
                with open(FAILED_FILE, "r", encoding="utf-8") as f:
                    existing_failed = {line.strip() for line in f}

            all_failed = existing_failed | failed_countries
            with open(FAILED_FILE, "w", encoding="utf-8") as f:
                for country in sorted(all_failed):
                    f.write(f"{country}\n")

if __name__ == "__main__":
    asyncio.run(scrape())
