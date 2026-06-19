# QA Job Hunter Bot 🤖

Telegram-бот для поиска вакансий QA Engineer. Агрегирует вакансии с hh.ru, Habr Career и Telegram-каналов, оценивает их через AI и присылает только подходящие.

## Быстрый старт

### 1. Клонируй репозиторий

```bash
git clone https://github.com/KirillQAEngineer/qa-job-bot.git
cd qa-job-hunter-bot
```

### 2. Создай файл .env

```bash
cp .env.example .env
# Открой .env и заполни все переменные
```

### 3. Установи зависимости и запусти

```bash
pip install -r requirements.txt
python bot.py
```

При первом запуске Telethon попросит ввести код из Telegram — это нормально, авторизация нужна один раз.

## Деплой на Railway

1. Загрузи код на GitHub (`.env` не загружай — он в `.gitignore`)
2. Зайди на [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Добавь переменные из `.env` в раздел Variables
4. Deploy!

Дальше любые правки: `git add . && git commit -m "правка" && git push` — Railway задеплоит автоматически.

## Настройка Telegram-каналов

Отредактируй список каналов в `config.py`:

```python
TG_CHANNELS = [
    'qa_jobs_ru',        # username канала без @
    'tester_jobs',
    'твой_канал',        # добавь свои каналы
]
```

## Структура проекта

```
qa-job-bot/
├── bot.py              ← точка входа
├── config.py           ← настройки
├── database.py         ← SQLite база данных
├── scheduler.py        ← запуск парсеров каждые 30 минут
├── ai_filter.py        ← AI оценка вакансий через GPT
├── parsers/
│   ├── hh_parser.py    ← hh.ru API
│   ├── habr_parser.py  ← Habr Career API
│   └── tg_parser.py    ← Telegram-каналы
├── handlers/
│   ├── start.py        ← /start, /help, подписка
│   ├── jobs.py         ← просмотр вакансий, отклик
│   ├── favorites.py    ← избранное
│   └── profile.py      ← настройка профиля
├── .env.example        ← шаблон переменных
├── Dockerfile
└── requirements.txt
```
