# DevOps Job Intelligence Agent

A free, local-first job discovery and ranking application for DevOps, Platform Engineering, AWS/Cloud Operations, Infrastructure Automation and junior SRE roles. Runs on Windows 11 with Python; no paid API key is required.

## Features
- Public Greenhouse, Lever and Ashby posting API collectors.
- Configurable employer board identifiers; no authenticated scraping.
- Local SQLite storage, duplicate-safe upserts and first/last-seen timestamps.
- Explainable deterministic score (0–100), matched skills, warnings and cautious experience extraction.
- INR/LPA salary penalty only when an explicit salary is detectable and below target. Missing salary is flagged, not rejected.
- Streamlit dashboard, search, score/source filters, CSV export and application tracker.
- Optional Ollama local explanation; AI never calculates or changes scores.
- Windows setup/refresh scripts and unit tests.

## Requirements
Windows 10/11, Python 3.11+, Git. 8 GB RAM is sufficient for the core app. Ollama is optional and may be slow on CPU.

## Install (PowerShell)
```powershell
.\scripts\setup.ps1
.\.venv\Scripts\Activate.ps1
```
Manual:
```powershell
py -3 -m venv .venv
..venvScriptsActivate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item config.example.yaml config.yaml
```

## Configure
Edit config.yaml and add public board slugs/tokens:
```yaml
sources:
  greenhouse: [example-board]
  lever: [example-company]
  ashby: [example-board]
```
Identifiers are board slugs, not display names. URL patterns: boards.greenhouse.io/BOARD, jobs.lever.co/SLUG, jobs.ashbyhq.com/BOARD. Verify identifiers yourself. Update profile skills, years_experience, minimum_salary_lpa and preferred_locations with accurate details.

## Run
```powershell
python -m job_agent.cli
streamlit run app.py
```
Open the local URL Streamlit prints (normally http://localhost:8501). Or use .\scripts\refresh.ps1 to refresh only.

## Tests
```powershell
python -m unittest discover -s tests -v
```

## Scoring and limitations
The score is a prioritisation heuristic, not a probability of interview/offer. It considers title relevance, configured skill overlap, location text, infrastructure signals, cautiously extracted experience requirements, explicit INR/LPA salary below target, and user-configured excluded keywords. Descriptions are inconsistent; extraction can miss or misread requirements. Currency conversion is not attempted. Verify seniority, eligibility, work authorisation, location, salary and all requirements on the original employer page. This is not an exhaustive job search; only configured public boards are checked.

## Optional local AI
Install Ollama separately, pull qwen2.5:1.5b (default), and set llm.enabled to true in config.yaml. The helper in job_agent/llm.py generates requirement/gap explanations only. It is not used by the scoring engine. Model download uses disk and CPU/RAM; core app needs no LLM.

## Privacy and responsible use
Only public documented job-board endpoints are used. Respect provider terms, rate limits and employer policies. No login automation, CAPTCHA bypass, proxies, private endpoint discovery, mass messaging or automatic application submission. Resume and credentials are not uploaded. Jobs and tracker notes remain in local SQLite unless you export/share them.

## Project structure
app.py | config.example.yaml | job_agent/ | scripts/ | tests/

MIT License. See LICENSE.
