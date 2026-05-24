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
