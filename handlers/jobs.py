from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_recent_jobs, add_favorite, remove_favorite, is_favorite, get_job_by_id


def _score_stars(score: int) -> str:
    filled = score // 20
    return '⭐' * filled + '☆' * (5 - filled)


def _job_text(job: dict) -> str:
    score = job.get('ai_score', 0)
    return (
        f'💼 <b>{job["title"]}</b>\n'
        f'🏢 {job["company"]}\n'
        f'💰 {job.get("salary") or "Не указана"}\n'
        f'📡 {job["source"]}\n'
        f'🤖 AI-оценка: <b>{score}/100</b> {_score_stars(score)}'
    )


def _job_keyboard(job: dict, user_id: int) -> InlineKeyboardMarkup:
    fav = is_favorite(user_id, job['id'])
    fav_label = '💔 Убрать из избранного' if fav else '❤ В избранное'
    fav_data = f'unfav_{job["id"]}' if fav else f'fav_{job["id"]}'
    return InlineKeyboardMarkup([[
        InlineKeyboardButton('Откликнуться →', url=job['url']),
        InlineKeyboardButton(fav_label, callback_data=fav_data),
    ]])


async def cmd_jobs(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    jobs = get_recent_jobs(limit=10)
    if not jobs:
        await update.message.reply_text(
            '😔 Пока нет вакансий. Парсеры работают каждые 30 минут — скоро появятся!'
        )
        return

    await update.message.reply_text(f'📋 <b>Последние {len(jobs)} вакансий:</b>', parse_mode='HTML')
    user_id = update.effective_user.id
    for job in jobs:
        await update.message.reply_text(
            _job_text(job),
            reply_markup=_job_keyboard(job, user_id),
            parse_mode='HTML',
        )


async def handle_favorite_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data  # fav_123 или unfav_123

    action, job_id_str = data.split('_', 1)
    job_id = int(job_id_str)
    job = get_job_by_id(job_id)
    if not job:
        await query.answer('Вакансия не найдена', show_alert=True)
        return

    if action == 'fav':
        add_favorite(user_id, job_id)
        await query.answer('Добавлено в избранное! ❤', show_alert=True)
    else:
        remove_favorite(user_id, job_id)
        await query.answer('Убрано из избранного', show_alert=True)

    # Обновляем кнопку
    try:
        await query.edit_message_reply_markup(reply_markup=_job_keyboard(job, user_id))
    except Exception:
        pass
