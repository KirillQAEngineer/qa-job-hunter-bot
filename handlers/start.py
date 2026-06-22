from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from database import upsert_user, update_user_field, get_user

MAIN_MENU = ReplyKeyboardMarkup(
    [
        [KeyboardButton('🔍 Вакансии'), KeyboardButton('❤ Избранное')],
        [KeyboardButton('👤 Мой профиль'), KeyboardButton('⚙ Подписка')],
        [KeyboardButton('🔄 Запустить парсинг')],
    ],
    resize_keyboard=True,
)


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    upsert_user(user.id, user.username or '', user.first_name or '')
    await update.message.reply_text(
        f'Привет, {user.first_name}! 👋\n\n'
        '🤖 <b>QA Job Hunter Bot</b> — твой персональный охотник за вакансиями.\n\n'
        '📋 <b>Что я умею:</b>\n'
        '• Каждые 30 минут проверяю hh.ru, Habr Career и Telegram-каналы\n'
        '• Оцениваю каждую вакансию AI и присылаю только подходящие\n'
        '• Позволяю откликнуться прямо из бота\n'
        '• Сохраняю понравившиеся вакансии в избранное\n\n'
        '⚙ Настрой профиль командой /profile, чтобы AI подбирал точнее.\n'
        '🔄 Кнопка <b>«Запустить парсинг»</b> — немедленно ищет новые вакансии.\n\n'
        'Используй меню ниже 👇',
        parse_mode='HTML',
        reply_markup=MAIN_MENU,
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '📖 <b>Команды бота:</b>\n\n'
        '/start — главное меню\n'
        '/jobs — последние вакансии из базы\n'
        '/parse — немедленно запустить парсинг\n'
        '/profile — настроить профиль\n'
        '/favorites — избранные вакансии\n'
        '/subscribe — включить уведомления\n'
        '/unsubscribe — выключить уведомления\n'
        '/help — эта справка',
        parse_mode='HTML',
        reply_markup=MAIN_MENU,
    )


async def cmd_subscribe(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    update_user_field(update.effective_user.id, 'subscribed', 1)
    await update.message.reply_text(
        '✅ Уведомления включены! Буду присылать новые вакансии каждые 30 минут.',
        reply_markup=MAIN_MENU,
    )


async def cmd_unsubscribe(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    update_user_field(update.effective_user.id, 'subscribed', 0)
    await update.message.reply_text(
        '🔕 Уведомления выключены. Включить обратно: /subscribe',
        reply_markup=MAIN_MENU,
    )
