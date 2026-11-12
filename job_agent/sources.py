import html, re, time
import requests
from bs4 import BeautifulSoup
from .models import Job

class JobSourceError(RuntimeError): pass

def clean_html(value):
 if not value:return ""
 text=html.unescape(BeautifulSoup(value,"html.parser").get_text(" ",strip=True))
 return re.sub(r"\s+"," ",text).strip()

def make_session(user_agent):
 session=requests.Session()
 session.headers.update({"User-Agent":user_agent,"Accept":"application/json"})
 return session

def request_json(session,url,timeout):
 error=None
 for attempt in range(3):
  try:
   response=session.get(url,timeout=timeout);response.raise_for_status();return response.json()
  except (requests.RequestException,ValueError) as exc:
   error=exc
   if attempt<2:time.sleep(1.5*(attempt+1))
 raise JobSourceError(f"Unable to fetch {url}: {error}") from error

def fetch_greenhouse(board,session=None,timeout=20):
 s=session or make_session("DevOpsJobIntelligenceAgent/1.0")
 data=request_json(s,f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true",timeout)
 return [Job("greenhouse",str(x.get("id","")),x.get("title") or "Untitled role",board,(x.get("location") or {}).get("name","Unknown"),x.get("absolute_url",""),clean_html(x.get("content","")),posted_at=x.get("updated_at")) for x in data.get("jobs",[])]

def fetch_lever(slug,session=None,timeout=20):
 s=session or make_session("DevOpsJobIntelligenceAgent/1.0")
 data=request_json(s,f"https://api.lever.co/v0/postings/{slug}?mode=json",timeout);jobs=[]
 for x in data if isinstance(data,list) else []:
  cats=x.get("categories") or {}
  jobs.append(Job("lever",str(x.get("id","")),x.get("text") or "Untitled role",slug,cats.get("location","Unknown"),x.get("hostedUrl",""),clean_html(x.get("descriptionPlain") or x.get("description","")),cats.get("commitment","Unknown"),x.get("createdAt")))
 return jobs

def fetch_ashby(board,session=None,timeout=20):
 s=session or make_session("DevOpsJobIntelligenceAgent/1.0")
 data=request_json(s,f"https://api.ashbyhq.com/posting-api/job-board/{board}",timeout);jobs=[]
 for x in data.get("jobs",[]):
  location=x.get("location") or x.get("locationName") or "Unknown"
  if x.get("isRemote") and "remote" not in location.lower():location+=" (Remote)"
  jobs.append(Job("ashby",str(x.get("id","")),x.get("title") or "Untitled role",board,location,x.get("jobUrl") or x.get("applyUrl",""),clean_html(x.get("descriptionPlain") or x.get("descriptionHtml","")),x.get("employmentType","Unknown"),x.get("publishedAt")))
 return jobs

def collect_all(cfg):
 timeout=int(cfg["app"].get("request_timeout_seconds",20))
 session=make_session(cfg["app"].get("user_agent","DevOpsJobIntelligenceAgent/1.0"))
 jobs=[];errors=[]
 for name,collector in (("greenhouse",fetch_greenhouse),("lever",fetch_lever),("ashby",fetch_ashby)):
  for board in cfg["sources"].get(name,[]) or []:
   try:jobs.extend(collector(board,session,timeout))
   except Exception as exc:errors.append(f"{name}/{board}: {exc}")
   time.sleep(.5)
 return jobs,errors
