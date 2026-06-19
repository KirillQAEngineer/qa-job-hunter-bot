import logging
from openai import OpenAI
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)


def score_job(job: dict, user_profile: dict) -> int:
    """
    Оценивает соответствие вакансии профилю пользователя.
    Возвращает число от 0 до 100.
    """
    prompt = f"""Ты помогаешь специалисту найти работу. Оцени насколько вакансия подходит кандидату.

Профиль кандидата:
- Должность: {user_profile.get('position', 'QA Engineer')}
- Уровень: {user_profile.get('level', 'Senior')}
- Навыки: {user_profile.get('skills', 'Selenium, Playwright, API, Mobile')}
- Формат работы: {user_profile.get('work_format', 'remote')}

Вакансия:
- Название: {job.get('title', '')}
- Компания: {job.get('company', '')}
- Зарплата: {job.get('salary') or 'не указана'}
- Источник: {job.get('source', '')}

Ответь ТОЛЬКО числом от 0 до 100. Без пояснений, без текста, только число."""

    try:
        resp = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=5,
            temperature=0,
        )
        raw = resp.choices[0].message.content.strip()
        score = int(''.join(filter(str.isdigit, raw))[:3])
        return min(max(score, 0), 100)
    except Exception as e:
        logger.warning(f'AI оценка недоступна: {e}')
        return 50  # Дефолт если OpenAI недоступен
