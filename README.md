# Установка

1. Клонировать репозиторий
2. Установить зависимости: `pip install -r requirements.txt`
3. Создать файл `.env` на основе `.env.example`
4. Запустить: `python app.py`

# Структура проекта

malinka_dashboard/
│
├── app.py                          # Точка входа приложения
├── config.py                       # Конфигурация и настройки
├── requirements.txt                # Зависимости
├── .env.example                    # Пример переменных окружения
├── .gitignore
│
├── src/                            # Исходный код
│   ├── __init__.py
│   ├── database/                   # Работа с базой данных
│   │   ├── __init__.py
│   │   ├── connection.py           # Подключение к БД
│   │   ├── queries.py              # SQL запросы
│   │   └── models.py               # Модели данных
│   │
│   ├── components/                 # Компоненты Dash
│   │   ├── __init__.py
│   │   ├── layout.py               # Основной макет
│   │   ├── callbacks.py            # Все callback'и
│   │   ├── kpi_cards.py            # KPI карточки
│   │   ├── charts.py               # Графики и визуализации
│   │   └── filters.py              # Фильтры и контролы
│   │
│   ├── utils/                      # Вспомогательные функции
│   │   ├── __init__.py
│   │   ├── data_processor.py       # Обработка данных
│   │   ├── calculations.py         # Расчеты метрик
│   │   └── validators.py           # Валидация данных
│   │
│   └── assets/                     # Статические файлы
│       ├── style.css
│       └── custom.js
│
├── tests/                          # Тесты
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_calculations.py
│   └── conftest.py
│
└── docs/                           # Документация
    ├── deployment.md
    ├── api.md
    └── data_schema.md




