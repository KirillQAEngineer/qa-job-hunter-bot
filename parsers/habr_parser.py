import logging
import requests
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


def fetch_habr_jobs() -> list[dict]:
    """Используем RSS — публичный, не требует авторизации."""
    rss_url = 'https://career.habr.com/vacancies/rss?q=QA+Engineer&remote=true&sort=date'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml',
    }
    try:
        resp = requests.get(rss_url, headers=headers, timeout=15)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        items = root.findall('.//item')
        logger.info(f'Habr Career RSS: получено {len(items)} вакансий')
    except Exception as e:
        logger.error(f'Habr Career: ошибка: {e}')
        return []

    jobs = []
    for item in items:
        title = item.findtext('title', '').strip()
        url = item.findtext('link', '').strip()
        if title and url:
            jobs.append({
                'title':   title,
                'company': 'Habr Career',
                'salary':  '',
                'url':     url,
                'source':  'Habr Career',
                'remote':  1,
            })
    return jobs
