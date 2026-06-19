from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_favorites


async def cmd_favorites(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    jobs = get_favorites(user_id)

    if not jobs:
        await update.message.reply_text(
            '❤ Избранное пусто.\n\nНажимай кнопку «❤ В избранное» под понравившейся вакансией!'
        )
        return

    await update.message.reply_text(
        f'❤ <b>Избранное ({len(jobs)} вакансий):</b>', parse_mode='HTML'
    )
    for job in jobs:
        score = job.get('ai_score', 0)
        text = (
            f'💼 <b>{job["title"]}</b>\n'
            f'🏢 {job["company"]}\n'
            f'💰 {job.get("salary") or "Не указана"}\n'
            f'📡 {job["source"]}\n'
            f'🤖 AI: {score}/100'
        )
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton('Откликнуться →', url=job['url']),
            InlineKeyboardButton('💔 Убрать', callback_data=f'unfav_{job["id"]}'),
        ]])
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode='HTML')
