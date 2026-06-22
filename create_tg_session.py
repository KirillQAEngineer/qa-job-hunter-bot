"""
Запусти этот скрипт ОДИН РАЗ локально для создания Telegram-сессии.
После этого загрузи файл tg_session.session в Railway через переменную окружения.

Запуск:  python create_tg_session.py
"""
import asyncio
from telethon import TelegramClient
from config import TG_API_ID, TG_API_HASH, TG_PHONE


async def main():
    client = TelegramClient('tg_session', TG_API_ID, TG_API_HASH)
    await client.start(phone=TG_PHONE)
    me = await client.get_me()
    print(f'\n✅ Успешно авторизован как: {me.first_name} (@{me.username})')
    print('Файл tg_session.session создан.')
    print('\nТеперь загрузи этот файл на Railway:')
    print('  Railway → твой сервис → Settings → Volumes → добавь /app/tg_session.session')
    await client.disconnect()


asyncio.run(main())
