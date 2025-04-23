import asyncio
import csv
import os
from playwright.async_api import async_playwright
from session_manager import get_stealth_context

OUTPUT_FILE = "data/bans.csv"
FAILED_FILE = "data/failed_countries.txt"

country_links = {  # Ваш список ссылок }

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await get_stealth_context(browser)
        page = await context.new_page()

        existing_rows = set()
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header
                existing_rows = {tuple(row) for row in reader}

        new_rows = set()
        failed_countries = set()

        for country_name, url in country_links.items():
            await page.goto(url, timeout=60000)

            tables = await page.query_selector_all("table.ui.celled.center.aligned.unstackable.table.seven.column.day")

            has_data = False
            for table in tables:
                trs = await table.query_selector_all("tbody tr")
                for tr in trs:
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

        await browser.close()

        if new_rows:
            write_header = not os.path.exists(OUTPUT_FILE) or os.path.getsize(OUTPUT_FILE) == 0
            with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(["Country", "Date", "Time Ranges"])
                writer.writerows(new_rows)

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
