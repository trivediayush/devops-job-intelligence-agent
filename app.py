import streamlit as st
import pandas as pd
from job_agent.db import connect

st.set_page_config(page_title='DevOps Job Intelligence', layout='wide')
st.title('DevOps Job Intelligence Agent')
st.caption('Local-first job discovery. Scores are heuristic decision support, not hiring predictions.')
conn = connect('data/jobs.db')
rows = conn.execute('SELECT * FROM jobs ORDER BY score DESC, first_seen DESC').fetchall()
if not rows:
    st.info('No listings yet. Configure sources in config.yaml, then run: python -m job_agent.cli')
else:
    df = pd.DataFrame([dict(r) for r in rows])
    q = st.text_input('Filter by title, company, or location')
    if q:
        mask = df[['title','company','location']].fillna('').astype(str).apply(lambda c: c.str.contains(q, case=False, regex=False)).any(axis=1)
        df = df[mask]
    st.metric('Matching listings', len(df))
    st.dataframe(df[['score','title','company','location','salary_text','url','score_details']], use_container_width=True, hide_index=True,
                 column_config={'url': st.column_config.LinkColumn('Job posting')})
    st.download_button('Export CSV', df.to_csv(index=False).encode('utf-8'), 'jobs.csv', 'text/csv')
