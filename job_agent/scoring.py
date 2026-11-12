import re

SKILL_ALIASES = {
 'aws': ['aws','amazon web services','ec2','ecr','ecs','eks'],
 'linux': ['linux','ubuntu','rhel'], 'kubernetes': ['kubernetes','k8s'],
 'docker': ['docker','podman','containerization'], 'terraform': ['terraform','iac','infrastructure as code'],
 'jenkins': ['jenkins'], 'github actions': ['github actions'], 'gitlab ci': ['gitlab ci'],
 'prometheus': ['prometheus'], 'grafana': ['grafana'], 'azure': ['azure'],
 'bash': ['bash','shell scripting'], 'python': ['python'], 'trivy': ['trivy'], 'sonarqube': ['sonarqube','sonar']
}

def score_job(job, profile):
    text = ' '.join([job.get('title',''), job.get('description',''), job.get('company',''), job.get('location','')]).lower()
    score, reasons, warnings = 0, [], []
    title = job.get('title','').lower()
    title_terms = ['devops','platform','cloud','site reliability','sre','infrastructure','systems engineer']
    if any(t in title for t in title_terms): score += 25; reasons.append('Relevant role title (+25)')
    else: warnings.append('Title is not an obvious DevOps/platform match')
    skills = profile.get('skills', [])
    matched = []
    for skill in skills:
        aliases = SKILL_ALIASES.get(skill.lower(), [skill.lower()])
        if any(re.search(r'(?<![a-z0-9])'+re.escape(a)+r'(?![a-z0-9])', text) for a in aliases): matched.append(skill)
    skill_points = min(45, round(45 * len(matched) / max(1, len(skills))))
    score += skill_points
    reasons.append(f'{len(matched)}/{len(skills)} profile skills found (+{skill_points})')
    loc = job.get('location','').lower()
    if any(x.lower() in loc for x in profile.get('preferred_locations',['India','Remote'])): score += 10; reasons.append('Preferred location (+10)')
    else: warnings.append('Location preference not confirmed')
    desc = job.get('description','').lower()
    infra_terms = ['ci/cd','pipeline','deployment','monitoring','observability','cloud infrastructure','automation','incident']
    infra_hits = sum(t in desc for t in infra_terms)
    points = min(15, infra_hits * 3); score += points
    if points: reasons.append(f'Infrastructure responsibilities present (+{points})')
    salary = job.get('salary_text') or ''
    minimum = profile.get('minimum_salary_lpa')
    if salary:
        nums = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', salary)]
        if nums and minimum and max(nums) < minimum: score -= 15; warnings.append('Published salary appears below target')
    else: warnings.append('Salary not disclosed; verify during screening')
    return max(0, min(100, score)), '; '.join(reasons), '; '.join(warnings)
