import logging
import requests

logger = logging.getLogger(__name__)
HH_API = 'https://api.hh.ru/vacancies'
HEADERS = {'User-Agent': 'QAJobBot/1.0 (job search bot)'}


def fetch_hh_jobs() -> list[dict]:
    params = {
        'text': 'QA Engineer OR тестировщик OR автоматизатор',
        'schedule': 'remote',
        'per_page': 50,
        'order_by': 'publication_time',
        'search_field': 'name',
        'only_with_salary': 'false',
    }
    try:
        resp = requests.get(HH_API, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        items = resp.json().get('items', [])
    except Exception as e:
        logger.error(f'hh.ru: ошибка запроса: {e}')
        return []

    jobs = []
    for item in items:
        salary = _parse_salary(item.get('salary'))
        jobs.append({
            'title':   item['name'],
            'company': item.get('employer', {}).get('name', ''),
            'salary':  salary,
            'url':     item['alternate_url'],
            'source':  'hh.ru',
            'remote':  1,
        })
    logger.info(f'hh.ru: найдено {len(jobs)} вакансий')
    return jobs


def _parse_salary(salary_obj) -> str:
    if not salary_obj:
        return ''
    from_val = salary_obj.get('from')
    to_val = salary_obj.get('to')
    currency = salary_obj.get('currency', '')
    parts = []
    if from_val:
        parts.append(f'от {int(from_val):,}')
    if to_val:
        parts.append(f'до {int(to_val):,}')
    return ' '.join(parts) + f' {currency}' if parts else ''
