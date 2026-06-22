import asyncio
from telethon import TelegramClient
from config import TG_API_ID, TG_API_HASH, TG_PHONE

async def main():
    client = TelegramClient('tg_session', TG_API_ID, TG_API_HASH)
    await client.start(phone=TG_PHONE)
    me = await client.get_me()
    print(f'\n✅ Успешно авторизован как: {me.first_name} (@{me.username})')
    print('Файл tg_session.session создан!')
    await client.disconnect()

asyncio.run(main())
