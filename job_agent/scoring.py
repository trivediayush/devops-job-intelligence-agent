import re

ALIASES = {
 "aws":["aws","amazon web services","ec2","ecr","ecs","eks"], "linux":["linux","ubuntu","rhel"],
 "kubernetes":["kubernetes","k8s"], "docker":["docker","podman","containerization"],
 "terraform":["terraform","iac","infrastructure as code"], "jenkins":["jenkins"],
 "github actions":["github actions"], "gitlab ci":["gitlab ci"], "prometheus":["prometheus"],
 "grafana":["grafana"], "azure":["azure"], "bash":["bash","shell scripting"], "python":["python"],
 "trivy":["trivy"], "sonarqube":["sonarqube","sonar"], "opentelemetry":["opentelemetry","otel"]
}
ROLE=("devops","platform","cloud","site reliability","sre","infrastructure","systems engineer","production engineer")
INFRA=("ci/cd","pipeline","deployment","monitoring","observability","cloud infrastructure","automation","incident","kubernetes","terraform")
def contains(text,term):
 return re.search(r"(?<![a-z0-9])"+re.escape(term.lower())+r"(?![a-z0-9])",text.lower()) is not None
def experience_requirement(description):
 patterns=(r"(\d{1,2})\s*[-–to]+\s*(\d{1,2})\s*\+?\s*years?",r"(\d{1,2})\s*\+\s*years?",r"at least\s+(\d{1,2})\s+years?",r"minimum of\s+(\d{1,2})\s+years?")
 vals=[]
 for pattern in patterns:
  for match in re.finditer(pattern,(description or "").lower()):
   nums=[int(x) for x in match.groups() if x and x.isdigit()]
   if nums:vals.append(max(nums))
 return min(vals) if vals else None
def salary_below_target(salary,minimum):
 if not salary or not minimum:return False
 value=salary.lower().replace(",","")
 if not any(x in value for x in ("lpa","lakh","lakhs","inr","₹")):return False
 nums=[float(x) for x in re.findall(r"\d+(?:\.\d+)?",value)]
 return bool(nums and max(nums)<float(minimum))
def score_job(job,profile):
 title=(job.get("title") or "").lower();desc=(job.get("description") or "").lower()
 location=(job.get("location") or "").lower()
 full=" ".join((title,desc,location,(job.get("company") or "").lower()))
 score=0;reasons=[];warnings=[]
 if any(term in title for term in ROLE):score+=25;reasons.append("Relevant infrastructure/platform title (+25)")
 else:warnings.append("Title is not an obvious DevOps/platform match")
 skills=profile.get("skills",[]);matched=[]
 for skill in skills:
  if any(contains(full,term) for term in ALIASES.get(skill.lower(),[skill.lower()])):matched.append(skill)
 points=min(40,round(40*len(matched)/max(1,len(skills))));score+=points
 reasons.append(f"{len(matched)}/{len(skills)} configured skills matched (+{points})")
 if any(term.lower() in location for term in profile.get("preferred_locations",["India","Remote"])):
  score+=10;reasons.append("Preferred location indicated (+10)")
 else:warnings.append("Location preference needs manual verification")
 points=min(15,sum(term in desc for term in INFRA)*3);score+=points
 if points:reasons.append(f"Infrastructure responsibilities (+{points})")
 years=experience_requirement(desc);user_years=float(profile.get("years_experience",0))
 if years is not None:
  if years>user_years+1:score-=25;warnings.append(f"Experience requirement may exceed profile: about {years} years")
  elif years>user_years:score-=10;warnings.append(f"Experience requirement needs review: about {years} years")
  else:reasons.append(f"Experience requirement appears compatible (about {years} years)")
 else:warnings.append("Experience requirement not confidently extracted; inspect posting")
 if salary_below_target(job.get("salary_text"),profile.get("minimum_salary_lpa")):
  score-=15;warnings.append("Published INR salary appears below target")
 elif not job.get("salary_text"):warnings.append("Salary not disclosed; verify during screening")
 excluded=[word for word in profile.get("exclude_keywords",[]) if word.lower() in full]
 if excluded:score-=35;warnings.append("Excluded keyword found: "+", ".join(excluded))
 return max(0,min(100,score)),"; ".join(reasons),"; ".join(warnings),", ".join(matched),years
