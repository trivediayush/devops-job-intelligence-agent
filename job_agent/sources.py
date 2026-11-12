import requests
from .models import Job

TIMEOUT = 20
HEADERS = {'User-Agent': 'DevOpsJobIntelligenceAgent/0.1 (personal job search)'}

def fetch_greenhouse(board_token):
    url = f'https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true'
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json().get('jobs', [])
    out = []
    for item in data:
        out.append(Job('greenhouse', str(item.get('id')), item.get('title',''), board_token,
            (item.get('location') or {}).get('name','Unknown'), item.get('absolute_url',''),
            item.get('content',''), posted_at=item.get('updated_at')))
    return out

def fetch_lever(company_slug):
    url = f'https://api.lever.co/v0/postings/{company_slug}?mode=json'
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    out = []
    for item in response.json():
        cats = item.get('categories') or {}
        out.append(Job('lever', str(item.get('id')), item.get('text',''), company_slug,
            cats.get('location','Unknown'), item.get('hostedUrl',''),
            item.get('descriptionPlain',''), cats.get('commitment','Unknown')))
    return out

# Only use publicly documented endpoints and employer boards you are permitted to access.
