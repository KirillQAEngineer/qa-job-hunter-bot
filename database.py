import sqlite3
from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            username    TEXT,
            first_name  TEXT,
            position    TEXT DEFAULT 'QA Engineer',
            level       TEXT DEFAULT 'Senior',
            work_format TEXT DEFAULT 'remote',
            skills      TEXT DEFAULT 'Selenium,Playwright,API,Mobile',
            subscribed  INTEGER DEFAULT 1,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS jobs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT,
            company     TEXT,
            salary      TEXT,
            source      TEXT,
            url         TEXT UNIQUE,
            description TEXT,
            remote      INTEGER DEFAULT 1,
            ai_score    INTEGER DEFAULT 0,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS favorites (
            user_id    INTEGER,
            job_id     INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, job_id)
        );
    ''')
    conn.commit()
    conn.close()


def upsert_user(user_id, username, first_name):
    conn = get_conn()
    conn.execute(
        'INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
        (user_id, username, first_name)
    )
    conn.commit()
    conn.close()


def get_user(user_id):
    conn = get_conn()
    row = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_field(user_id, field, value):
    conn = get_conn()
    conn.execute(f'UPDATE users SET {field} = ? WHERE user_id = ?', (value, user_id))
    conn.commit()
    conn.close()


def get_subscribed_users():
    conn = get_conn()
    rows = conn.execute('SELECT * FROM users WHERE subscribed = 1').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_job(job: dict) -> int | None:
    """Сохраняет вакансию, возвращает id если новая, None если дубликат."""
    conn = get_conn()
    try:
        c = conn.execute(
            'INSERT OR IGNORE INTO jobs (title, company, salary, source, url, remote) VALUES (?,?,?,?,?,?)',
            (job['title'], job['company'], job.get('salary', ''), job['source'], job['url'], job.get('remote', 1))
        )
        conn.commit()
        job_id = c.lastrowid if c.rowcount > 0 else None
    except Exception as e:
        print(f'Ошибка сохранения вакансии: {e}')
        job_id = None
    finally:
        conn.close()
    return job_id


def update_job_score(job_id: int, score: int):
    conn = get_conn()
    conn.execute('UPDATE jobs SET ai_score = ? WHERE id = ?', (score, job_id))
    conn.commit()
    conn.close()


def get_recent_jobs(limit=10):
    conn = get_conn()
    rows = conn.execute(
        'SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?', (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_job_by_id(job_id):
    conn = get_conn()
    row = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_favorite(user_id, job_id):
    conn = get_conn()
    conn.execute('INSERT OR IGNORE INTO favorites (user_id, job_id) VALUES (?,?)', (user_id, job_id))
    conn.commit()
    conn.close()


def remove_favorite(user_id, job_id):
    conn = get_conn()
    conn.execute('DELETE FROM favorites WHERE user_id=? AND job_id=?', (user_id, job_id))
    conn.commit()
    conn.close()


def get_favorites(user_id):
    conn = get_conn()
    rows = conn.execute(
        '''SELECT j.* FROM jobs j
           JOIN favorites f ON j.id = f.job_id
           WHERE f.user_id = ?
           ORDER BY f.created_at DESC''',
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def is_favorite(user_id, job_id):
    conn = get_conn()
    row = conn.execute(
        'SELECT 1 FROM favorites WHERE user_id=? AND job_id=?', (user_id, job_id)
    ).fetchone()
    conn.close()
    return row is not None
