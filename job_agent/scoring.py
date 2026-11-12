import re

ALIASES = {
    "aws": ["aws", "amazon web services", "ec2", "ecr", "ecs", "eks"],
    "linux": ["linux", "ubuntu", "rhel"], "kubernetes": ["kubernetes", "k8s"],
    "docker": ["docker", "podman", "containerization"], "terraform": ["terraform", "iac", "infrastructure as code"],
    "jenkins": ["jenkins"], "github actions": ["github actions"], "gitlab ci": ["gitlab ci"],
    "prometheus": ["prometheus"], "grafana": ["grafana"], "azure": ["azure"],
    "bash": ["bash", "shell scripting"], "python": ["python"], "trivy": ["trivy"],
    "sonarqube": ["sonarqube", "sonar"], "opentelemetry": ["opentelemetry", "otel"]
}
ROLE_TERMS = ("devops", "platform", "cloud", "site reliability", "sre", "infrastructure", "systems engineer", "production engineer")
INFRA_TERMS = ("ci/cd", "pipeline", "deployment", "monitoring", "observability", "cloud infrastructure", "automation", "incident", "kubernetes", "terraform")

def _contains(text, term):
    return re.search(r"(?<![a-z0-9])" + re.escape(term.lower()) + r"(?![a-z0-9])", text.lower()) is not None

def experience_requirement(description):
    text = description.lower()
    patterns = [
        r"(\d{1,2})\s*[-–to]+\s*(\d{1,2})\s*\+?\s*years?",
        r"(\d{1,2})\s*\+\s*years?",
        r"at least\s+(\d{1,2})\s+years?",
        r"minimum of\s+(\d{1,2})\s+years?"
    ]
    found = []
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            nums = [int(x) for x in match.groups() if x and x.isdigit()]
            if nums:
                found.append(max(nums))
    return min(found) if found else None

def salary_below_target(salary_text, minimum_lpa):
    if not salary_text or not minimum_lpa:
        return False
    text = salary_text.lower().replace(",", "")
    if not any(token in text for token in ("lpa", "lakhs", "lakh", "inr", "₹")):
        return False
    values = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", text)]
    return bool(values and max(values) < float(minimum_lpa))

def score_job(job, profile):
    title = (job.get("title") or "").lower()
    description = (job.get("description") or "").lower()
    location = (job.get("location") or "").lower()
    company = (job.get("company") or "").lower()
    full_text = " ".join((title, description, location, company))
    score, reasons, warnings = 0, [], []

    if any(term in title for term in ROLE_TERMS):
        score += 25
        reasons.append("Relevant infrastructure/platform title (+25)")
    else:
        warnings.append("Title is not an obvious DevOps/platform match")

    skills = profile.get("skills", [])
    matched = []
    for skill in skills:
        terms = ALIASES.get(skill.lower(), [skill.lower()])
        if any(_contains(full_text, term) for term in terms):
            matched.append(skill)
    skill_points = min(40, round(40 * len(matched) / max(1, len(skills))))
    score += skill_points
    reasons.append(f"{len(matched)}/{len(skills)} configured skills matched (+{skill_points})")

    if any(term.lower() in location for term in profile.get("preferred_locations", ["India", "Remote"])):
        score += 10
        reasons.append("Preferred location indicated (+10)")
    else:
        warnings.append("Location preference needs manual verification")

    infra_hits = sum(term in description for term in INFRA_TERMS)
    infra_points = min(15, infra_hits * 3)
    score += infra_points
    if infra_points:
        reasons.append(f"Infrastructure responsibilities found (+{infra_points})")

    required_years = experience_requirement(description)
    user_years = float(profile.get("years_experience", 0))
    if required_years is not None:
        if required_years > user_years + 1:
            score -= 25
            warnings.append(f"Experience requirement may exceed profile: about {required_years} years")
        elif required_years > user_years:
            score -= 10
            warnings.append(f"Experience requirement needs review: about {required_years} years")
        else:
            reasons.append(f"Experience requirement appears compatible (about {required_years} years)")
    else:
        warnings.append("Experience requirement not confidently extracted; inspect posting")

    if salary_below_target(job.get("salary_text"), profile.get("minimum_salary_lpa")):
        score -= 15
        warnings.append("Published INR salary appears below configured target")
    elif not job.get("salary_text"):
        warnings.append("Salary not disclosed; verify during screening")

    excluded = [x for x in profile.get("exclude_keywords", []) if x.lower() in full_text]
    if excluded:
        score -= 35
        warnings.append("Excluded keyword found: " + ", ".join(excluded))

    return max(0, min(100, score)), "; ".join(reasons), "; ".join(warnings), ", ".join(matched), required_years
