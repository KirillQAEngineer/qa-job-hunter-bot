import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')           # Токен от @BotFather
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') # Ключ OpenAI для AI-фильтра
TG_API_ID = int(os.getenv('TG_API_ID', '0'))
TG_API_HASH = os.getenv('TG_API_HASH')
TG_PHONE = os.getenv('TG_PHONE')

# Telegram-каналы для парсинга (добавь свои username каналов без @)
TG_CHANNELS = [
    'qa_jobs_ru',
    'tester_jobs',
    'qa_automation_jobs',
]

# Интервал парсинга — 30 минут
PARSE_INTERVAL = 1800

DB_PATH = 'jobs.db'

# Минимальный AI-скор для отправки пользователю (0-100)
MIN_AI_SCORE = 60
