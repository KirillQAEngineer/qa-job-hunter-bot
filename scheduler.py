import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from parsers.hh_parser import fetch_hh_jobs
from parsers.habr_parser import fetch_habr_jobs
from parsers.tg_parser import fetch_tg_jobs
from ai_filter import score_job
from database import save_job, update_job_score, get_subscribed_users
from config import PARSE_INTERVAL, MIN_AI_SCORE

logger = logging.getLogger(__name__)


def _score_stars(score: int) -> str:
    filled = score // 20
    return '⭐' * filled + '☆' * (5 - filled)


def _format_job_message(job: dict, score: int) -> str:
    return (
        f'🔔 <b>Новая вакансия</b>\n\n'
        f'💼 <b>{job["title"]}</b>\n'
        f'🏢 {job["company"]}\n'
        f'💰 {job.get("salary") or "Не указана"}\n'
        f'📡 {job["source"]}\n'
        f'🤖 AI-оценка: <b>{score}/100</b> {_score_stars(score)}'
    )


async def _send_job(bot, user_id: int, job: dict, score: int):
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton('Откликнуться →', url=job['url']),
        InlineKeyboardButton('❤ В избранное', callback_data=f'fav_{job["id"]}'),
    ]])
    try:
        await bot.send_message(
            chat_id=user_id,
            text=_format_job_message(job, score),
            reply_markup=keyboard,
            parse_mode='HTML',
        )
    except Exception as e:
        logger.warning(f'Не удалось отправить вакансию пользователю {user_id}: {e}')


async def run_parsers(bot):
    logger.info('=== Запуск парсеров ===')

    all_jobs = []
    for fetcher in [fetch_hh_jobs, fetch_habr_jobs, fetch_tg_jobs]:
        try:
            result = fetcher()
            logger.info(f'{fetcher.__name__}: получено {len(result)} вакансий')
            all_jobs.extend(result)
        except Exception as e:
            logger.error(f'Ошибка в парсере {fetcher.__name__}: {e}', exc_info=True)

    logger.info(f'Итого найдено: {len(all_jobs)} вакансий')

    users = get_subscribed_users()
    if not users:
        logger.info('Нет подписчиков для рассылки')
        return

    new_count = 0
    for job in all_jobs:
        job_id = save_job(job)
        if job_id is None:
            continue  # дубликат

        new_count += 1
        job['id'] = job_id

        for user in users:
            score = score_job(job, user)
            update_job_score(job_id, score)
            if score >= MIN_AI_SCORE:
                await _send_job(bot, user['user_id'], job, score)

    logger.info(f'Новых вакансий добавлено: {new_count}')


async def run_parsers_with_status(bot, notify_user_id: int = None):
    """Запуск парсеров с уведомлением пользователя о начале и конце."""
    if notify_user_id:
        try:
            await bot.send_message(
                chat_id=notify_user_id,
                text='🔄 Запускаю парсеры hh.ru, Habr Career и Telegram-каналы...\nЭто займёт ~30 секунд.'
            )
        except Exception:
            pass

    await run_parsers(bot)

    if notify_user_id:
        try:
            await bot.send_message(
                chat_id=notify_user_id,
                text='✅ Парсинг завершён! Нажми <b>🔍 Вакансии</b> чтобы посмотреть результаты.',
                parse_mode='HTML',
            )
        except Exception:
            pass


def start_scheduler(bot):
    scheduler = AsyncIOScheduler()

    # Первый запуск — через 10 секунд после старта (не ждём 30 минут!)
    scheduler.add_job(
        run_parsers,
        trigger='date',
        run_date=datetime.now() + timedelta(seconds=10),
        args=[bot],
        id='parse_jobs_first',
    )

    # Повторяющийся запуск каждые 30 минут
    scheduler.add_job(
        run_parsers,
        trigger='interval',
        seconds=PARSE_INTERVAL,
        args=[bot],
        id='parse_jobs_interval',
        replace_existing=True,
    )

    scheduler.start()
    logger.info(f'Планировщик запущен. Первый парсинг через 10 секунд, затем каждые {PARSE_INTERVAL // 60} минут.')
    return scheduler
