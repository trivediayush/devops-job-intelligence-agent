import sqlite3
from pathlib import Path
SCHEMA="""
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS jobs(id INTEGER PRIMARY KEY AUTOINCREMENT,source TEXT NOT NULL,source_id TEXT NOT NULL,title TEXT NOT NULL,company TEXT NOT NULL,location TEXT,url TEXT,description TEXT,employment_type TEXT,posted_at TEXT,salary_text TEXT,score INTEGER DEFAULT 0,score_details TEXT DEFAULT '',warnings TEXT DEFAULT '',matched_skills TEXT DEFAULT '',required_years REAL,first_seen TEXT DEFAULT CURRENT_TIMESTAMP,last_seen TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(source,source_id));
CREATE TABLE IF NOT EXISTS applications(id INTEGER PRIMARY KEY AUTOINCREMENT,job_id INTEGER NOT NULL UNIQUE REFERENCES jobs(id) ON DELETE CASCADE,status TEXT NOT NULL DEFAULT 'Saved',notes TEXT DEFAULT '',applied_at TEXT,updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
"""
def connect(db_path="data/jobs.db"):
    p=Path(db_path);p.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(p);c.row_factory=sqlite3.Row;c.execute("PRAGMA foreign_keys=ON");c.executescript(SCHEMA)
    existing={r[1] for r in c.execute("PRAGMA table_info(jobs)")}
    for name,kind in {"warnings":"TEXT DEFAULT ''","matched_skills":"TEXT DEFAULT ''","required_years":"REAL","last_seen":"TEXT"}.items():
        if name not in existing:c.execute(f"ALTER TABLE jobs ADD COLUMN {name} {kind}")
    c.commit();return c
def upsert_jobs(conn,jobs):
    count=0
    for j in jobs:
        vals=(j.source,j.source_id,j.title,j.company,j.location,j.url,j.description,j.employment_type,j.posted_at,j.salary_text)
        cur=conn.execute("""INSERT INTO jobs(source,source_id,title,company,location,url,description,employment_type,posted_at,salary_text) VALUES(?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(source,source_id) DO UPDATE SET title=excluded.title,company=excluded.company,location=excluded.location,url=excluded.url,description=excluded.description,employment_type=excluded.employment_type,posted_at=excluded.posted_at,salary_text=excluded.salary_text,last_seen=CURRENT_TIMESTAMP""",vals)
        count+=max(cur.rowcount,0)
    conn.commit();return count
def list_jobs(conn):return conn.execute("SELECT * FROM jobs ORDER BY score DESC,first_seen DESC").fetchall()
def save_application(conn,job_id,status="Saved",notes=""):
    conn.execute("""INSERT INTO applications(job_id,status,notes,applied_at) VALUES(?,?,?,CASE WHEN ?='Applied' THEN CURRENT_TIMESTAMP ELSE NULL END)
    ON CONFLICT(job_id) DO UPDATE SET status=excluded.status,notes=excluded.notes,applied_at=CASE WHEN excluded.status='Applied' THEN COALESCE(applications.applied_at,CURRENT_TIMESTAMP) ELSE applications.applied_at END,updated_at=CURRENT_TIMESTAMP""",(job_id,status,notes,status));conn.commit()
