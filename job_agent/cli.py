import argparse
from .db import connect, upsert_jobs
from .sources import fetch_greenhouse, fetch_lever
from .scoring import score_job
import yaml

def main():
    parser = argparse.ArgumentParser(description='Collect and rank public job listings')
    parser.add_argument('--config', default='config.yaml')
    args = parser.parse_args()
    with open(args.config, encoding='utf-8') as f: cfg = yaml.safe_load(f)
    conn = connect(cfg['app']['database'])
    jobs = []
    for token in cfg.get('sources', {}).get('greenhouse', []):
        try: jobs.extend(fetch_greenhouse(token))
        except Exception as exc: print(f'Greenhouse {token}: {exc}')
    for slug in cfg.get('sources', {}).get('lever', []):
        try: jobs.extend(fetch_lever(slug))
        except Exception as exc: print(f'Lever {slug}: {exc}')
    upsert_jobs(conn, jobs)
    profile = cfg.get('profile', {})
    for row in conn.execute('SELECT * FROM jobs').fetchall():
        score, reasons, warnings = score_job(dict(row), profile)
        conn.execute('UPDATE jobs SET score=?, score_details=? WHERE id=?', (score, reasons + (' | ' + warnings if warnings else ''), row['id']))
    conn.commit()
    print(f'Collected {len(jobs)} listings; database: {cfg["app"]["database"]}')

if __name__ == '__main__': main()
