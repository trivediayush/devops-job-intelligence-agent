import argparse
from .config import load_config
from .db import connect,upsert_jobs
from .sources import collect_all
from .scoring import score_job

def refresh(cfg):
 conn=connect(cfg["app"]["database"]);jobs,errors=collect_all(cfg);changed=upsert_jobs(conn,jobs)
 rows=conn.execute("SELECT * FROM jobs").fetchall()
 for row in rows:
  score,reasons,warnings,matched,years=score_job(dict(row),cfg["profile"])
  conn.execute("UPDATE jobs SET score=?,score_details=?,warnings=?,matched_skills=?,required_years=? WHERE id=?",(score,reasons,warnings,matched,years,row["id"]))
 conn.commit()
 print(f"Fetched {len(jobs)} listings; inserted/updated {changed}; total stored {len(rows)}.")
 for error in errors:print("SOURCE ERROR:",error)
 conn.close()

def main():
 parser=argparse.ArgumentParser(description="Collect and rank public job listings")
 parser.add_argument("--config",default="config.yaml")
 args=parser.parse_args()
 refresh(load_config(args.config))

if __name__=="__main__":main()
