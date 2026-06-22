import logging
import random
import requests

logger = logging.getLogger(__name__)
HH_API = 'https://api.hh.ru/vacancies'

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
]


def fetch_hh_jobs() -> list[dict]:
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'application/json',
        'HH-User-Agent': 'QAJobHunterBot/1.0 (qa.job.hunter.bot@gmail.com)',
    }
    params = {
        'text': 'QA Engineer OR тестировщик OR QA automation',
        'schedule': 'remote',
        'per_page': 50,
        'order_by': 'publication_time',
    }
    try:
        resp = requests.get(HH_API, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        items = data.get('items', [])
        logger.info(f'hh.ru: найдено {data.get("found", "?")} вакансий, получено {len(items)}')
    except Exception as e:
        logger.error(f'hh.ru: ошибка: {e}')
        return []

    jobs = []
    for item in items:
        jobs.append({
            'title':   item['name'],
            'company': item.get('employer', {}).get('name', ''),
            'salary':  _parse_salary(item.get('salary')),
            'url':     item['alternate_url'],
            'source':  'hh.ru',
            'remote':  1,
        })
    return jobs


def _parse_salary(s) -> str:
    if not s:
        return ''
    parts = []
    if s.get('from'): parts.append(f'от {int(s["from"]):,}')
    if s.get('to'):   parts.append(f'до {int(s["to"]):,}')
    return (' '.join(parts) + f' {s.get("currency", "")}').strip() if parts else ''
