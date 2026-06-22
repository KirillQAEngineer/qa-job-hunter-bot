import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters,
)

from config import BOT_TOKEN
from database import init_db
from scheduler import start_scheduler, run_parsers_with_status

from handlers.start import cmd_start, cmd_help, cmd_subscribe, cmd_unsubscribe, MAIN_MENU
from handlers.jobs import cmd_jobs, handle_favorite_callback
from handlers.favorites import cmd_favorites
from handlers.profile import cmd_profile, profile_field_callback, profile_set_value

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def cmd_parse(update: Update, ctx):
    """Ручной запуск парсинга прямо из бота."""
    user_id = update.effective_user.id
    await run_parsers_with_status(ctx.bot, notify_user_id=user_id)


def main():
    if not BOT_TOKEN:
        raise ValueError('BOT_TOKEN не задан! Проверь файл .env')

    init_db()
    logger.info('База данных инициализирована')

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # --- Команды ---
    app.add_handler(CommandHandler('start', cmd_start))
    app.add_handler(CommandHandler('help', cmd_help))
    app.add_handler(CommandHandler('jobs', cmd_jobs))
    app.add_handler(CommandHandler('favorites', cmd_favorites))
    app.add_handler(CommandHandler('profile', cmd_profile))
    app.add_handler(CommandHandler('subscribe', cmd_subscribe))
    app.add_handler(CommandHandler('unsubscribe', cmd_unsubscribe))
    app.add_handler(CommandHandler('parse', cmd_parse))

    # --- Кнопки меню (текстовые) ---
    app.add_handler(MessageHandler(filters.Regex('🔍 Вакансии'), cmd_jobs))
    app.add_handler(MessageHandler(filters.Regex('❤ Избранное'), cmd_favorites))
    app.add_handler(MessageHandler(filters.Regex('👤 Мой профиль'), cmd_profile))
    app.add_handler(MessageHandler(filters.Regex('⚙ Подписка'), cmd_subscribe))
    app.add_handler(MessageHandler(filters.Regex('🔄 Запустить парсинг'), cmd_parse))

    # --- Inline-кнопки ---
    app.add_handler(CallbackQueryHandler(handle_favorite_callback, pattern='^(fav|unfav)_'))
    app.add_handler(CallbackQueryHandler(profile_field_callback, pattern='^profile_'))

    # --- Ввод значений профиля ---
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.Regex('^(🔍|❤|👤|⚙|🔄)'),
        profile_set_value,
    ))

    # --- Планировщик (первый запуск через 10 сек, затем каждые 30 мин) ---
    start_scheduler(app.bot)

    logger.info('Бот запущен и готов к работе!')
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
