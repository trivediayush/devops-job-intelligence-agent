# DevOps Job Intelligence Agent

A local-first job discovery and ranking tool for DevOps, Platform, Cloud Operations, Infrastructure Automation and junior SRE roles.

## Included in this initial version
- Public Greenhouse and Lever job-board API collectors
- Local SQLite storage with duplicate-safe upserts
- Transparent heuristic scoring (0–100), with reasons and warnings
- Streamlit dashboard, filters and CSV export
- No automatic applications or credential collection

## Requirements
Windows 11 and Python 3.11+.

## Setup (PowerShell)
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item config.example.yaml config.yaml
```

Edit `config.yaml`. Add employer board identifiers under `sources`:
```yaml
sources:
  greenhouse: [example-company]
  lever: [example-company]
```
Use the employer's actual public board identifier, not its display name. Then run:
```powershell
python -m job_agent.cli
streamlit run app.py
```

## Scoring notes
The score is a heuristic for prioritising manual review, not a probability of getting an interview. Salary not disclosed is flagged for verification rather than treated as an automatic rejection. Always inspect the original employer posting for experience requirements, location, salary, work authorisation and eligibility.

## Responsible use
Use publicly documented endpoints and respect source terms, rate limits, robots/access controls and employer policies. This project does not bypass logins, CAPTCHAs or access restrictions, and it does not submit applications automatically.

## Known limitations
- Employer board identifiers must be configured manually.
- The initial version does not yet include Ashby collection, a local LLM explanation layer, automated experience-year extraction, an application tracker interface, scheduling or MCP integration.
- Job data and scoring require human verification; no fit score guarantees suitability or selection.
