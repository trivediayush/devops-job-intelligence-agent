import pandas as pd
import streamlit as st
from job_agent.config import load_config
from job_agent.db import connect,list_jobs,save_application

st.set_page_config(page_title="DevOps Job Intelligence",layout="wide")
st.title("DevOps Job Intelligence Agent")
st.caption("Local job discovery and decision support. Scores are heuristics, not hiring predictions.")
try:cfg=load_config()
except Exception as exc:st.error(str(exc));st.stop()
conn=connect(cfg["app"]["database"])
jobs_tab,tracker_tab,help_tab=st.tabs(["Job matches","Application tracker","Setup"])
with jobs_tab:
 if st.button("Refresh public job boards",type="primary"):
  from job_agent.cli import refresh
  with st.spinner("Collecting listings..."):refresh(cfg)
  st.rerun()
 rows=list_jobs(conn)
 if not rows:st.info("No jobs stored. Add verified public board identifiers to config.yaml and refresh.")
 else:
  df=pd.DataFrame([dict(r) for r in rows]);a,b,c=st.columns(3)
  a.metric("Stored jobs",len(df));b.metric("High priority (70+)",int((df.score>=70).sum()));c.metric("Sources",int(df.source.nunique()))
  query=st.text_input("Search title, employer, location or skill");minimum=st.slider("Minimum score",0,100,0)
  sources=st.multiselect("Sources",sorted(df.source.unique()),default=sorted(df.source.unique()))
  view=df[(df.score>=minimum)&df.source.isin(sources)]
  if query:
   mask=view[["title","company","location","description","matched_skills"]].fillna("").astype(str).apply(lambda col:col.str.contains(query,case=False,regex=False)).any(axis=1)
   view=view[mask]
  st.dataframe(view[["score","title","company","location","source","posted_at","salary_text","matched_skills","required_years","warnings","url"]],use_container_width=True,hide_index=True,column_config={"url":st.column_config.LinkColumn("Original posting")})
  st.download_button("Export filtered jobs CSV",view.drop(columns=["description"],errors="ignore").to_csv(index=False).encode(),"devops_jobs.csv","text/csv")
  choices={f'{r["title"]} — {r["company"]} [ID {r["id"]}]':int(r["id"]) for r in rows}
  st.subheader("Save/update application")
  selected=st.selectbox("Job",list(choices));status=st.selectbox("Status",["Saved","Preparing","Applied","Interview","Offer","Rejected","Withdrawn"]);notes=st.text_area("Notes")
  if st.button("Save tracker entry"):save_application(conn,choices[selected],status,notes);st.success("Tracker entry saved.")
  if cfg.get("llm",{}).get("enabled",False):
   st.subheader("Optional local AI explanation")
   if st.button("Explain selected job requirements and gaps"):
    jobrow=conn.execute("SELECT * FROM jobs WHERE id=?",(choices[selected],)).fetchone()
    try:
     from job_agent.llm import explain_with_ollama
     with st.spinner("Asking local Ollama model..."):
      answer=explain_with_ollama(dict(jobrow),cfg["profile"],cfg["llm"]["model"],cfg["llm"]["base_url"])
     st.markdown(answer)
    except Exception as exc:st.error(f"Local model unavailable: {exc}")
with tracker_tab:
 records=conn.execute("SELECT a.status,a.notes,a.applied_at,a.updated_at,j.title,j.company,j.url FROM applications a JOIN jobs j ON j.id=a.job_id ORDER BY a.updated_at DESC").fetchall()
 if records:
  tracker=pd.DataFrame([dict(r) for r in records])
  st.dataframe(tracker,use_container_width=True,hide_index=True,column_config={"url":st.column_config.LinkColumn("Posting")})
  st.download_button("Export tracker CSV",tracker.to_csv(index=False).encode(),"application_tracker.csv","text/csv")
 else:st.info("No tracker entries yet. Save a job from Job matches.")
with help_tab:
 st.markdown("""
### Configure sources
Edit config.yaml and add verified public board slugs under sources.greenhouse, sources.lever and sources.ashby. Update profile skills and experience accurately.

### Scoring
Scores are deterministic prioritisation heuristics, not interview probabilities. Experience extraction is approximate. Inspect original postings for salary, eligibility, seniority, work authorisation and location.

### Optional Ollama
Install Ollama separately, pull the configured model and set llm.enabled to true. The local model explains job requirements and potential gaps; it never changes numeric scores.

### Privacy
Data is stored in local SQLite. No resume or credentials are uploaded. The app never submits applications.
""")
conn.close()
