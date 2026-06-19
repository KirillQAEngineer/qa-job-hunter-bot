from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from database import get_user, update_user_field

# Состояния диалога
CHOOSING_FIELD, SETTING_VALUE = range(2)

FIELDS = {
    'position': ('Должность', '💼'),
    'level': ('Уровень', '📊'),
    'skills': ('Навыки', '🛠'),
    'work_format': ('Формат работы', '🏠'),
}


async def cmd_profile(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text('Сначала нажми /start')
        return

    text = (
        '👤 <b>Твой профиль:</b>\n\n'
        f'💼 Должность: {user["position"]}\n'
        f'📊 Уровень: {user["level"]}\n'
        f'🛠 Навыки: {user["skills"]}\n'
        f'🏠 Формат: {user["work_format"]}\n'
        f'🔔 Подписка: {"Включена ✅" if user["subscribed"] else "Выключена 🔕"}\n\n'
        'Нажми кнопку чтобы изменить поле:'
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f'{e} {n}', callback_data=f'profile_{k}')]
        for k, (n, e) in FIELDS.items()
    ])
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode='HTML')


async def profile_field_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    field = query.data.replace('profile_', '')
    ctx.user_data['editing_field'] = field
    name, emoji = FIELDS[field]

    examples = {
        'position': 'например: Senior QA Engineer',
        'level': 'например: Junior, Middle, Senior, Lead',
        'skills': 'например: Selenium, Playwright, API, Mobile, Cypress',
        'work_format': 'например: remote, office, hybrid',
    }

    await query.edit_message_text(
        f'{emoji} <b>Изменить: {name}</b>\n\nВведи новое значение ({examples.get(field, "")}):\n\n/cancel — отмена',
        parse_mode='HTML',
    )
    return SETTING_VALUE


async def profile_set_value(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    field = ctx.user_data.get('editing_field')
    if not field:
        return ConversationHandler.END

    value = update.message.text.strip()
    update_user_field(update.effective_user.id, field, value)
    name, emoji = FIELDS[field]

    await update.message.reply_text(
        f'✅ {emoji} <b>{name}</b> обновлена: {value}\n\nAI теперь будет учитывать это при оценке вакансий.',
        parse_mode='HTML',
    )
    return ConversationHandler.END


async def profile_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Отмена. Профиль не изменён.')
    return ConversationHandler.END


def get_profile_conversation():
    return ConversationHandler(
        entry_points=[],
        states={
            SETTING_VALUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, profile_set_value)
            ],
        },
        fallbacks=[CommandHandler('cancel', profile_cancel)],
        per_message=False,
    )
