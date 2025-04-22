# 🚛 Traffic Ban Parser & Dashboard

![GitHub last commit](https://img.shields.io/github/last-commit/Ron-911/trafficban-parser)
![GitHub repo size](https://img.shields.io/github/repo-size/Ron-911/trafficban-parser)
![GitHub issues](https://img.shields.io/github/issues/Ron-911/trafficban-parser)
![MIT license](https://img.shields.io/badge/license-MIT-blue.svg)

Автоматический парсинг ограничений движения грузовиков в европейских странах с визуализацией в Streamlit и обновлением через GitHub Actions.

---

## 🔍 Описание

Этот проект:

- собирает данные с [trafficban.com](https://trafficban.com) по 40+ странам;
- сохраняет информацию о запретах движения в CSV-таблицу;
- отображает данные в Streamlit-интерфейсе;
- обновляет данные автоматически каждый день.

---

## 📊 Демо (Render)

👉 https://your-subdomain.onrender.com  
*(замени на актуальную ссылку после деплоя)*

---

## 📁 Структура проекта

```
📁 trafficban-parser/
├── app.py                  # Streamlit интерфейс
├── scraper.py              # Основной скрипт для парсинга
├── data/bans.csv           # CSV-файл (создаётся автоматически)
├── requirements.txt        # Зависимости Python
├── render.yaml             # Деплой на Render
└── .streamlit/config.toml  # Конфиг для Streamlit
```

---

## ⚙️ Запуск локально

```bash
git clone https://github.com/Ron-911/trafficban-parser.git
cd trafficban-parser

pip install -r requirements.txt
playwright install

python scraper.py
streamlit run app.py
```

---

## ☁️ Деплой на Render

1. Создай Web Service на [render.com](https://render.com)
2. Укажи команды:
   - **Build command**:
     ```bash
     pip install -r requirements.txt && playwright install
     ```
   - **Start command**:
     ```bash
     streamlit run app.py
     ```
3. Добавь `.streamlit/config.toml`:
   ```toml
   [server]
   port = 10000
   enableCORS = false
   enableXsrfProtection = false
   address = "0.0.0.0"
   headless = true
   ```

---

## 🤖 Автоматизация (GitHub Actions)

- Ежедневный запуск парсера в 06:00 (UTC)
- Сохранение и пуш `bans.csv` при изменениях
- Обновление веб-интерфейса на основе свежих данных

---

## 💡 Возможности

- ✅ Парсинг 40+ стран
- ✅ Асинхронность + прокси
- ✅ Streamlit-интерфейс
- ✅ Маскировка под обычный браузер
- ✅ Автообновление данных
- ✅ Защита от сбоев и логирование

---

## 👤 Автор

Создано Романом @ [github.com/Ron-911](https://github.com/Ron-911)  
С поддержкой ChatGPT

---

## 📄 Лицензия

Проект распространяется по лицензии MIT.

---

## 🌐 English Version (Summary)

This project:

- Scrapes traffic restrictions for trucks from [trafficban.com]
- Supports 40+ countries
- Saves data to CSV (`Country`, `Date`, `Time Ranges`)
- Updates daily via GitHub Actions
- Displays data in a simple Streamlit interface
- Deployable to [Render](https://render.com)

---

> Enjoy it, and feel free to contribute! 🚛📊
