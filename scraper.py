import asyncio
import csv
from datetime import datetime
from playwright.async_api import async_playwright
from session_manager import get_stealth_context
import os

OUTPUT_FILE = "data/bans.csv"
FAILED_FILE = "data/failed_countries.txt"

async def get_country_links(page):
    await page.goto("https://www.trafficban.com/", timeout=60000)
    await page.wait_for_selector("#rightColumn .menu a.item")
    links = await page.query_selector_all("#rightColumn .menu a.item")
    country_links = {}
    for link in links:
        href = await link.get_attribute("href")
        name = await link.inner_text()
        if href and name:
            country_links[name.strip()] = f"https://www.trafficban.com/{href}"
    return country_links

async def scrape():
    os.makedirs("data", exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            context = await get_stealth_context(browser)
        except Exception as e:
            print(f"❌ Не удалось создать stealth context: {e}")
            await browser.close()
            return

        page = await context.new_page()
        country_links = await get_country_links(page)
        await page.close()

        rows = []
        failed_countries = []

        for country_name, url in country_links.items():
            try:
                page = await context.new_page()
                await page.goto(url, timeout=60000)
                await page.wait_for_selector("table.table", timeout=10000)

                tables = await page.query_selector_all("table.table")
                if not tables:
                    failed_countries.append(country_name)
                    await page.close()
                    continue

                table = tables[0]
                rows_html = await table.query_selector_all("tbody tr")
                for row in rows_html:
                    cells = await row.query_selector_all("td")
                    values = [await cell.inner_text() for cell in cells]
                    rows.append([country_name] + values)

                await page.close()
            except Exception as e:
                print(f"❌ Ошибка при загрузке {country_name}: {e}")
                failed_countries.append(country_name)

        await browser.close()

        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Country", "Date", "From", "To", "Vehicles", "Description"])
            writer.writerows(rows)

        with open(FAILED_FILE, "w", encoding="utf-8") as f:
            for c in failed_countries:
                f.write(c + "\n")

        if failed_countries:
            print("\n⚠️ Не удалось получить данные для следующих стран:")
            for c in failed_countries:
                print(f"- {c}")
        else:
            print("✅ Все страны успешно загружены")

if __name__ == "__main__":
    asyncio.run(scrape())