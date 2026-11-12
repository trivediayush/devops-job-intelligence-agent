import sqlite3
from pathlib import Path
from .models import Job

SCHEMA = '''
CREATE TABLE IF NOT EXISTS jobs (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 source TEXT NOT NULL, source_id TEXT NOT NULL, title TEXT NOT NULL,
 company TEXT NOT NULL, location TEXT, url TEXT, description TEXT,
 employment_type TEXT, posted_at TEXT, salary_text TEXT,
 score INTEGER DEFAULT 0, score_details TEXT DEFAULT '',
 first_seen TEXT DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(source, source_id)
);
CREATE TABLE IF NOT EXISTS applications (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 job_id INTEGER NOT NULL REFERENCES jobs(id), status TEXT NOT NULL DEFAULT 'Saved',
 notes TEXT DEFAULT '', applied_at TEXT, updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
'''

def connect(db_path='data/jobs.db'):
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn

def upsert_jobs(conn, jobs):
    count = 0
    for j in jobs:
        cur = conn.execute('''INSERT INTO jobs
        (source,source_id,title,company,location,url,description,employment_type,posted_at,salary_text)
        VALUES (?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(source,source_id) DO UPDATE SET title=excluded.title,
        company=excluded.company,location=excluded.location,url=excluded.url,
        description=excluded.description,employment_type=excluded.employment_type,
        posted_at=excluded.posted_at,salary_text=excluded.salary_text''',
        (j.source,j.source_id,j.title,j.company,j.location,j.url,j.description,
         j.employment_type,j.posted_at,j.salary_text))
        count += cur.rowcount > 0
    conn.commit()
    return count

def list_jobs(conn):
    return conn.execute('SELECT * FROM jobs ORDER BY score DESC, first_seen DESC').fetchall()
