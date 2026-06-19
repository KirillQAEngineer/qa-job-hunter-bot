import logging
import re
from telethon.sync import TelegramClient
from config import TG_API_ID, TG_API_HASH, TG_PHONE, TG_CHANNELS

logger = logging.getLogger(__name__)

QA_KEYWORDS = [
    'qa', 'qа', 'тестировщик', 'tester', 'quality assurance',
    'автоматизатор', 'automation', 'playwright', 'selenium', 'appium',
]


def fetch_tg_jobs() -> list[dict]:
    if not TG_API_ID or not TG_API_HASH:
        logger.warning('Telegram API не настроен, пропускаем парсинг каналов')
        return []

    jobs = []
    try:
        with TelegramClient('tg_session', TG_API_ID, TG_API_HASH) as client:
            client.start(phone=TG_PHONE)
            for channel in TG_CHANNELS:
                channel_jobs = _parse_channel(client, channel)
                jobs.extend(channel_jobs)
    except Exception as e:
        logger.error(f'Telegram парсер: {e}')

    logger.info(f'Telegram: найдено {len(jobs)} вакансий')
    return jobs


def _parse_channel(client, channel: str) -> list[dict]:
    jobs = []
    try:
        messages = client.get_messages(channel, limit=30)
        for msg in messages:
            if not msg.text:
                continue
            text_lower = msg.text.lower()
            if not any(kw in text_lower for kw in QA_KEYWORDS):
                continue

            # Берём первую строку как заголовок
            title = msg.text.strip().split('\n')[0][:120]

            # Ищем ссылку в тексте
            url_match = re.search(r'https?://\S+', msg.text)
            url = url_match.group() if url_match else f'https://t.me/{channel}/{msg.id}'

            # Пробуем найти зарплату в тексте
            salary_match = re.search(
                r'(\d[\d\s]*\d)\s*(руб|rub|₽|\$|usd|eur|€)', msg.text, re.IGNORECASE
            )
            salary = salary_match.group() if salary_match else ''

            jobs.append({
                'title':   title,
                'company': f'@{channel}',
                'salary':  salary,
                'url':     url,
                'source':  f'Telegram @{channel}',
                'remote':  1,
            })
    except Exception as e:
        logger.error(f'Ошибка парсинга канала @{channel}: {e}')
    return jobs
