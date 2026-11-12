import html
import re
import time
import requests
from bs4 import BeautifulSoup
from .models import Job

class JobSourceError(RuntimeError):
    pass

def clean_html(value):
    if not value:
        return ""
    soup = BeautifulSoup(value, "html.parser")
    return re.sub(r"\s+", " ", html.unescape(soup.get_text(" ", strip=True))).strip()

def make_session(user_agent):
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent, "Accept": "application/json"})
    return session

def request_json(session, url, timeout):
    last_error = None
    for attempt in range(3):
        try:
            response = session.get(url, timeout=timeout)
            if response.status_code == 429 or response.status_code >= 500:
                response.raise_for_status()
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
    raise JobSourceError(f"Could not fetch {url}: {last_error}") from last_error

def fetch_greenhouse(board_token, session=None, timeout=20):
    session = session or make_session("DevOpsJobIntelligenceAgent/1.0")
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
    payload = request_json(session, url, timeout)
    jobs = []
    for item in payload.get("jobs", []):
        jobs.append(Job(
            source="greenhouse", source_id=str(item.get("id", "")),
            title=item.get("title") or "Untitled role", company=board_token,
            location=(item.get("location") or {}).get("name", "Unknown"),
            url=item.get("absolute_url", ""), description=clean_html(item.get("content", "")),
            posted_at=item.get("updated_at")
        ))
    return jobs

def fetch_lever(company_slug, session=None, timeout=20):
    session = session or make_session("DevOpsJobIntelligenceAgent/1.0")
    url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"
    payload = request_json(session, url, timeout)
    jobs = []
    for item in payload if isinstance(payload, list) else []:
        cats = item.get("categories") or {}
        jobs.append(Job(
            source="lever", source_id=str(item.get("id", "")),
            title=item.get("text") or "Untitled role", company=company_slug,
            location=cats.get("location", "Unknown"), url=item.get("hostedUrl", ""),
            description=clean_html(item.get("descriptionPlain") or item.get("description", "")),
            employment_type=cats.get("commitment", "Unknown"),
            posted_at=item.get("createdAt")
        ))
    return jobs

def fetch_ashby(board_name, session=None, timeout=20):
    session = session or make_session("DevOpsJobIntelligenceAgent/1.0")
    url = f"https://api.ashbyhq.com/posting-api/job-board/{board_name}"
    payload = request_json(session, url, timeout)
    jobs = []
    for item in payload.get("jobs", []):
        location = item.get("location") or item.get("locationName") or "Unknown"
        if item.get("isRemote") and "remote" not in location.lower():
            location = f"{location} (Remote)"
        jobs.append(Job(
            source="ashby", source_id=str(item.get("id", "")),
            title=item.get("title") or "Untitled role", company=board_name,
            location=location, url=item.get("jobUrl") or item.get("applyUrl", ""),
            description=clean_html(item.get("descriptionPlain") or item.get("descriptionHtml", "")),
            employment_type=item.get("employmentType", "Unknown"),
            posted_at=item.get("publishedAt")
        ))
    return jobs

def collect_all(cfg):
    timeout = int(cfg["app"].get("request_timeout_seconds", 20))
    session = make_session(cfg["app"].get("user_agent", "DevOpsJobIntelligenceAgent/1.0"))
    collected, errors = [], []
    sources = cfg.get("sources", {})
    collectors = (("greenhouse", fetch_greenhouse), ("lever", fetch_lever), ("ashby", fetch_ashby))
    for source_name, collector in collectors:
        for board in sources.get(source_name, []) or []:
            try:
                collected.extend(collector(board, session=session, timeout=timeout))
            except Exception as exc:
                errors.append(f"{source_name}:{board}: {exc}")
            time.sleep(0.5)
    return collected, errors
