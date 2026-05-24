# Async Citilink Laptop Parser

Асинхронный скрапер данных о ноутбуках с сайта Citilink. Проект разработан на стеке **Python + Playwright + BeautifulSoup4** и оптимизирован для обхода динамической загрузки данных (Lazy Loading).

## 🚀 Особенности проекта
- **Асинхронность:** Быстрая и эффективная обработка страниц благодаря `asyncio` и асинхронному API `Playwright`.
- **Эмуляция поведения пользователя:** Реализован плавный скроллинг страниц (`infinite scroll / lazy loading`) для триггера динамической подгрузки карточек товаров через JS.
- **Data Cleansing & Regex:** Извлечение структурированных данных (CPU, RAM, GPU) из сырых текстовых заголовков при помощи регулярных выражений.
- **Дедупликация:** Автоматическая фильтрация рекламных карточек и дубликатов на лету при помощи структуры данных `set`.
- **Режим "Pythonic memory management":** Данные аккуратно агрегируются в RAM и сохраняются в JSON-файл атомарно за один проход ввода-вывода (I/O).

## 🛠 Стек технологий
- Python 3.10+
- Playwright (Chromium)
- BeautifulSoup4
- Регулярные выражения (re)
- Асинхронное логирование (logging)

## 📦 Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone [https://github.com/CrdMan/citilink-async-parser.git](https://github.com/CrdMan/citilink-async-parser.git)
   cd citilink-async-parser
2. Создайте и активируйте виртуальное окружение:
   ```bash
   # Для Linux/macOS
   python3 -m venv venv
   source venv/bin/activate

   # Для Windows
   python -m venv venv
   venv\Scripts\activate
3. Установите зависимости и системные бинарники браузеров для Playwright:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
4. Запустите парсер:
   ```bash
   python parser.py

## 📊 Пример выходных данных (laptops.json)
Результат работы программы сохраняется в корневую папку в виде структурированного JSON-файла:
   ```json
   [
    {
        "title": "Ноутбук Huawei MateBook D 16 RLEF-X 8+512GB Space Grey",
        "price": "54 990",
        "link": "[https://www.citilink.ru/product/noutbuk-huawei-matebook-d-16-rlef-x-8-512gb-space-grey-1948502/](https://www.citilink.ru/product/noutbuk-huawei-matebook-d-16-rlef-x-8-512gb-space-grey-1948502/)",
        "cpu": "Intel Core i5 12450H",
        "ram": "8 ГБ",
        "gpu": "Intel UHD Graphics"
    }
]
