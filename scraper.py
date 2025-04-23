import asyncio
import csv
from datetime import datetime
from playwright.async_api import async_playwright
from session_manager import get_stealth_context

OUTPUT_FILE = "data/bans.csv"
FAILED_FILE = "data/failed_countries.txt"

async def get_country_links(page):
    await page.goto("https://www.trafficban.com/", timeout=60000)
    await page.wait_for_selector("div#rightColumn .menu .item")
    country_elements = await page.query_selector_all("div#rightColumn .menu .item")

    country_links = {}
    for el in country_elements:
        href = await el.get_attribute("href")
        text = await el.inner_text()
        if href and text:
            url = f"https://www.trafficban.com/{href}"
            country_name = text.split("|")[-1].strip()
            country_links[country_name] = url
    return country_links

async def scrape():
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

                table = await page.query_selector("table.table")
                html_content = await table.inner_html()
                if "No data" in html_content or not html_content.strip():
                    failed_countries.append(country_name)
                    await page.close()
                    continue

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
