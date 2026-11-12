import pandas as pd
import streamlit as st
from job_agent.config import load_config
from job_agent.db import connect, list_jobs, save_application

st.set_page_config(page_title="DevOps Job Intelligence", layout="wide")
st.title("DevOps Job Intelligence Agent")
st.caption("Local job discovery and decision support. Scores are heuristics, not hiring predictions.")
try:
    cfg = load_config()
except Exception as exc:
    st.error(str(exc))
    st.stop()

conn = connect(cfg["app"]["database"])
tab_jobs, tab_tracker, tab_help = st.tabs(["Job matches", "Application tracker", "Setup"])
with tab_jobs:
    if st.button("Refresh public job boards", type="primary"):
        with st.spinner("Collecting listings..."):
            from job_agent.cli import refresh
            refresh(cfg)
        st.rerun()
    rows = list_jobs(conn)
    if not rows:
        st.info("No jobs stored yet. Add public board identifiers in config.yaml, then refresh.")
    else:
        df = pd.DataFrame([dict(row) for row in rows])
        c1, c2, c3 = st.columns(3)
        c1.metric("Stored jobs", len(df))
        c2.metric("High priority (70+)", int((df["score"] >= 70).sum()))
        c3.metric("Sources", int(df["source"].nunique()))
        query = st.text_input("Search title, employer, location or skills")
        min_score = st.slider("Minimum match score", 0, 100, 0)
        source_filter = st.multiselect("Sources", sorted(df["source"].dropna().unique()), default=sorted(df["source"].dropna().unique()))
        view = df[(df["score"] >= min_score) & (df["source"].isin(source_filter))]
        if query:
            mask = view[["title", "company", "location", "description", "matched_skills"]].fillna("").astype(str).apply(
                lambda col: col.str.contains(query, case=False, regex=False)).any(axis=1)
            view = view[mask]
        st.dataframe(view[["score", "title", "company", "location", "source", "posted_at", "salary_text", "matched_skills", "required_years", "warnings", "url"]],
                     use_container_width=True, hide_index=True,
                     column_config={"url": st.column_config.LinkColumn("Original posting")})
        st.download_button("Export filtered jobs to CSV", view.drop(columns=["description"], errors="ignore").to_csv(index=False).encode("utf-8"), "devops_jobs.csv", "text/csv")
        st.subheader("Save or update an application")
        options = {f'{r["title"]} — {r["company"]} (ID {r["id"]})': int(r["id"]) for r in rows}
        selected = st.selectbox("Job", list(options))
        status = st.selectbox("Status", ["Saved", "Preparing", "Applied", "Interview", "Offer", "Rejected", "Withdrawn"])
        notes = st.text_area("Notes")
        if st.button("Save tracker entry"):
            save_application(conn, options[selected], status, notes)
            st.success("Tracker entry saved.")
with tab_tracker:
    applications = conn.execute("""SELECT a.status,a.notes,a.applied_at,a.updated_at,j.title,j.company,j.url
    FROM applications a JOIN jobs j ON j.id=a.job_id ORDER BY a.updated_at DESC""").fetchall()
    if applications:
        tracker = pd.DataFrame([dict(row) for row in applications])
        st.dataframe(tracker, use_container_width=True, hide_index=True,
                     column_config={"url": st.column_config.LinkColumn("Posting")})
        st.download_button("Export application tracker", tracker.to_csv(index=False).encode("utf-8"), "application_tracker.csv", "text/csv")
    else:
        st.info("No tracker entries yet. Save a job from the Job matches tab.")
with tab_help:
    st.markdown("""
### Configuration
Edit config.yaml to add employer board identifiers under sources.greenhouse, sources.lever and sources.ashby.
These are board slugs/tokens, not company display names.

### Scoring
The deterministic score prioritises role-title relevance, configured skill overlap, location, infrastructure responsibilities and cautiously extracted experience/salary signals. It is not a probability of selection. Inspect the original posting.

### Local AI (optional)
Enable the Ollama section in config.yaml only after installing Ollama and pulling the configured model. The AI explanation is optional and cannot change numeric scores.

### Privacy and safety
Data is stored in your local SQLite database. No resume or credentials are uploaded. The app never submits applications.
""")
conn.close()
