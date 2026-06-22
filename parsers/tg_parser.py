import logging
import re
from telethon import TelegramClient
from config import TG_API_ID, TG_API_HASH, TG_CHANNELS

logger = logging.getLogger(__name__)

QA_KEYWORDS = [
    'qa', 'qа', 'тестировщик', 'tester', 'quality assurance',
    'автоматизатор', 'automation', 'playwright', 'selenium', 'appium',
]

_client: TelegramClient | None = None


async def _get_client() -> TelegramClient:
    global _client
    if _client is None:
        # Используем файл сессии tg_session.session — он уже авторизован
        _client = TelegramClient('tg_session', TG_API_ID, TG_API_HASH)
    if not _client.is_connected():
        await _client.connect()
    return _client


async def fetch_tg_jobs() -> list[dict]:
    if not TG_API_ID or not TG_API_HASH:
        logger.warning('Telegram API не настроен')
        return []

    jobs = []
    try:
        client = await _get_client()
        for channel in TG_CHANNELS:
            channel_jobs = await _parse_channel(client, channel)
            jobs.extend(channel_jobs)
    except Exception as e:
        logger.error(f'Telegram парсер: {e}', exc_info=True)

    logger.info(f'Telegram: найдено {len(jobs)} вакансий')
    return jobs


async def _parse_channel(client: TelegramClient, channel: str) -> list[dict]:
    jobs = []
    try:
        async for msg in client.iter_messages(channel, limit=30):
            if not msg.text:
                continue
            if not any(kw in msg.text.lower() for kw in QA_KEYWORDS):
                continue

            title = msg.text.strip().split('\n')[0][:120]
            url_match = re.search(r'https?://\S+', msg.text)
            url = url_match.group().rstrip('.,)') if url_match else f'https://t.me/{channel}/{msg.id}'
            salary_match = re.search(
                r'(\d[\d\s]*\d)\s*(руб|rub|₽|\$|usd|eur|€|тыс)', msg.text, re.IGNORECASE
            )
            jobs.append({
                'title':   title,
                'company': f'@{channel}',
                'salary':  salary_match.group() if salary_match else '',
                'url':     url,
                'source':  f'Telegram @{channel}',
                'remote':  1,
            })
    except Exception as e:
        logger.error(f'Ошибка парсинга @{channel}: {e}')
    return jobs
