import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import re

BASE_URL = "https://www.citilink.ru/catalog/noutbuki/"
NUM_PAGES = 20
SCROLL_STEP = 1000
SCROLL_TIMEOUT_MS = 400
PAGE_TIMEOUT_MS = 30000
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def extract_specs_from_title(title: str):
    """Извлекает процессор, ОЗУ и видеокарту из текстового названия ноутбука.

    Args:
        title: Полное название товара из каталога.

    Returns:
        Словарь со структурированными характеристиками.
    """

    ram_match = re.search(r"(\d+\s*(?:ГБ|GB))", title, re.IGNORECASE)
    ram = ram_match.group(1) if ram_match else None

    cpu_match = re.search(r"((?:Intel|AMD)[^,]+)", title, re.IGNORECASE)
    cpu = cpu_match.group(1).strip() if cpu_match else None

    gpu_match = re.search(
        r"([^,]*(?:GeForce|Radeon|UHD Graphics|Iris Xe|Graphics)[^,]+)",
        title,
        re.IGNORECASE,
    )
    gpu = gpu_match.group(1).strip() if gpu_match else None

    if not gpu and cpu and "Intel" in title and "Graphics" in title:
        gpu = "Intel UHD Graphics"

    return {"ram": ram, "cpu": cpu, "gpu": gpu}

def parse_html_to_laptops(html: str):
    """Парсит HTML страницу каталога и возвращает список ноутбуков с характеристиками."""

    soup = BeautifulSoup(html, "html.parser")
    laptops_data = []

    cards = soup.find_all(
        "div", attrs={"data-meta-name": "SnippetProductVerticalLayout"}
    )

    for card in cards:
        title_element = card.find(
            "a", attrs={"data-meta-name": "Snippet__title"}
        )
        price_element = card.find(
            "span", attrs={"data-meta-name": "Snippet__price"}
        )

        if title_element:
            full_title = title_element.text.strip()
            link = f"https://www.citilink.ru{title_element.get('href', '')}"
            price = price_element.text.strip() if price_element else "Нет в наличии"

            specs = extract_specs_from_title(full_title)

            laptop_entry = {
                "title": full_title,
                "price": price,
                "link": link,
                "cpu": specs["cpu"] or "Не определен",
                "ram": specs["ram"] or "Не определена",
                "gpu": specs["gpu"] or "Не определена",
            }
            laptops_data.append(laptop_entry)

    return laptops_data

async def scroll_to_bottom(page):
    """Плавно прокручивает страницу до самого низа для активации Lazy Loading.
    
    Двигается небольшими шагами, чтобы спровоцировать триггеры загрузки JS.
    """
    current_scroll_position = 0
    
    while True:
        total_height = await page.evaluate("document.body.scrollHeight")
        
        current_scroll_position += SCROLL_STEP
        await page.evaluate(f"window.scrollTo(0, {current_scroll_position});")
        
        await page.wait_for_timeout(SCROLL_TIMEOUT_MS)
        
        if current_scroll_position >= total_height:
            new_total_height = await page.evaluate("document.body.scrollHeight")
            if new_total_height == total_height:
                break

async def get_page_html(page, url: str):
    """Загружает страницу, прокручивает её до конца для загрузки всех товаров и возвращает HTML."""
    logger.info("Переход по адресу: %s", url)
    
    await page.goto(url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
    
    logger.info("Выполняется эмуляция прокрутки страницы для загрузки всех товаров...")
    await scroll_to_bottom(page)
    
    try:
        await page.wait_for_selector('[data-meta-name="SnippetProductVerticalLayout"]', timeout=PAGE_TIMEOUT_MS)
    except Exception:
        logger.warning("Элементы каталога не появились после скроллинга.")
        
    return await page.content()


def save_results_to_json(data: list[dict[str, Any]], filename: str = "laptops.json"):
    """Сохраняет собранные данные в файл JSON (Pythonic Way — запись за один раз).

    Args:
        data: Список словарей с данными.
        filename: Имя итогового файла.
    """

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    logger.info("Данные успешно сохранены в файл %s. Всего товаров: %d", filename, len(data))


async def main():
    all_laptops: list[dict[str, Any]] = []
    
    seen_urls = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
        )
        page = await context.new_page()

        try:
            for page_num in range(1, NUM_PAGES + 1):  
                logger.info("--- Парсинг страницы %d ---", page_num)
                url = f"{BASE_URL}?p={page_num}"
                
                try:
                    html = await get_page_html(page, url)
                    page_laptops = parse_html_to_laptops(html)
                    
                    if page_laptops:
                        unique_count_on_page = 0
                        for laptop in page_laptops:
                            laptop_url = laptop.get("link")
                            
                            if laptop_url and laptop_url not in seen_urls:
                                seen_urls.add(laptop_url)
                                all_laptops.append(laptop)
                                unique_count_on_page += 1
                                
                        logger.info(
                            "Страница %d: Спарсено карточек: %d, из них уникальных: %d", 
                            page_num, len(page_laptops), unique_count_on_page
                        )
                
                except Exception as page_ex:
                    logger.error("Ошибка при обработке страницы %d: %s", page_num, page_ex)
                
                await asyncio.sleep(2)

            if all_laptops:
                save_results_to_json(all_laptops)
                logger.info("Успех! Всего сохранено УНИКАЛЬНЫХ ноутбуков: %d", len(all_laptops))
                logger.info("Отрезано дубликатов/рекламы: %d", len(seen_urls) - len(all_laptops))

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())