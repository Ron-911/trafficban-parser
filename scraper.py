import asyncio
import csv
from playwright.async_api import async_playwright
from session_manager import get_stealth_context

OUTPUT_FILE = "data/bans.csv"
FAILED_FILE = "failed_countries.txt"

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
    "United Kingdom": "https://trafficban.com/country.united_kingdom.home.205.ru.html"
}


async def scrape_country(context, country, url):
    rows = []
    try:
        page = await context.new_page()
        await page.goto(url, timeout=60000)
        table = await page.wait_for_selector("table.day", timeout=15000, state="visible")

        if table:
            rows_html = await table.query_selector_all("tbody tr")
            for row in rows_html:
                cells = await row.query_selector_all("td")
                values = [await cell.inner_text() for cell in cells]
                rows.append([country] + values)

        await page.close()
        return rows, None
    except Exception as e:
        print(f"❌ Ошибка при загрузке {country}: {e}")
        return [], country


async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await get_stealth_context(browser)

        tasks = [scrape_country(context, country, url) for country, url in country_links.items()]
        results = await asyncio.gather(*tasks)

        all_rows = []
        failed = []
        for country_rows, fail in results:
            all_rows.extend(country_rows)
            if fail:
                failed.append(fail)

        await browser.close()

        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Country", "Date", "From", "To", "Vehicles", "Description"])
            writer.writerows(all_rows)

        if failed:
            with open(FAILED_FILE, "w", encoding="utf-8") as f:
                for c in failed:
                    f.write(c + "\n")
            print("\n⚠️ Не удалось получить данные для:")
            for c in failed:
                print(f"- {c}")
        else:
            print("✅ Все страны успешно загружены")


if __name__ == "__main__":
    asyncio.run(scrape())
