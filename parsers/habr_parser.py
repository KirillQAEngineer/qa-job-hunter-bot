import logging
import requests

logger = logging.getLogger(__name__)
HABR_API = 'https://career.habr.com/api/v1/vacancies'


def fetch_habr_jobs() -> list[dict]:
    params = {
        'q': 'QA Engineer',
        'remote': 'true',
        'per_page': 30,
        'order': 'date',
    }
    try:
        resp = requests.get(HABR_API, params=params, timeout=15)
        resp.raise_for_status()
        items = resp.json().get('list', [])
    except Exception as e:
        logger.error(f'Habr Career: ошибка запроса: {e}')
        return []

    jobs = []
    for item in items:
        job_id = item.get('id', '')
        jobs.append({
            'title':   item.get('title', ''),
            'company': item.get('company', {}).get('title', ''),
            'salary':  item.get('salaryQualifier', ''),
            'url':     f'https://career.habr.com/vacancies/{job_id}',
            'source':  'Habr Career',
            'remote':  1,
        })
    logger.info(f'Habr Career: найдено {len(jobs)} вакансий')
    return jobs
