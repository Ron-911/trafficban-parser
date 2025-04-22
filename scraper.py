import asyncio
import csv
import os
from datetime import datetime

from session_manager import get_browser_context

BASE_URL = "https://www.trafficban.com"
COUNTRIES = {
    "Germany": "/germany",
    "France": "/france",
    "Italy": "/italy",
    "Austria": "/austria",
    "Czech Republic": "/czech-republic",
    "Poland": "/poland",
    "Hungary": "/hungary",
    "Slovakia": "/slovakia",
    "Slovenia": "/slovenia",
    "Switzerland": "/switzerland",
    "Spain": "/spain",
    "Portugal": "/portugal",
}

OUTPUT_FILE = "traffic_bans.csv"


async def parse_country(country: str, url: str):
    playwright, browser, context = await get_browser_context()
    page = await context.new_page()
    result = []

    try:
        await page.goto(url, timeout=60000)
        rows = await page.locator("table.table.table-hover tbody tr").all()

        for row in rows:
            columns = await row.locator("td").all_text_contents()
            if len(columns) >= 4:
                result.append({
                    "Country": country,
                    "Date": columns[0].strip(),
                    "Time": columns[1].strip(),
                    "Type of vehicles": columns[2].strip(),
                    "Description": columns[3].strip()
                })
    except Exception as e:
        print(f"Error parsing {country}: {e}")
    finally:
        await context.close()
        await browser.close()
        await playwright.stop()

    return result


async def main():
    all_data = []
    tasks = []

    for country, path in COUNTRIES.items():
        url = BASE_URL + path
        tasks.append(parse_country(country, url))

    results = await asyncio.gather(*tasks)

    for country_data in results:
        if country_data:
            all_data.extend(country_data)

    if all_data:
        keys = all_data[0].keys()
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_data)
        print(f"Saved data to {OUTPUT_FILE}")
    else:
        print("No data extracted.")


if __name__ == "__main__":
    asyncio.run(main())
