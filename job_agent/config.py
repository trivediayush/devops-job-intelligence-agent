from pathlib import Path
import yaml

DEFAULT_CONFIG = {
    "app": {"database": "data/jobs.db", "request_timeout_seconds": 20, "user_agent": "DevOpsJobIntelligenceAgent/1.0 (personal research)"},
    "sources": {"greenhouse": [], "lever": [], "ashby": []},
    "profile": {
        "target_titles": ["DevOps Engineer", "Platform Engineer", "Cloud Engineer", "Site Reliability Engineer", "Infrastructure Engineer"],
        "skills": ["AWS", "Linux", "Kubernetes", "Docker", "Terraform", "Jenkins", "GitHub Actions", "GitLab CI", "Prometheus", "Grafana", "Azure", "Bash", "Python", "Trivy", "SonarQube", "OpenTelemetry"],
        "preferred_locations": ["India", "Remote"],
        "minimum_salary_lpa": 6,
        "years_experience": 1,
        "exclude_keywords": ["unpaid internship"]
    },
    "llm": {"enabled": False, "provider": "ollama", "model": "qwen2.5:1.5b", "base_url": "http://localhost:11434"}
}

def load_config(path="config.yaml"):
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"{config_path} not found. Copy config.example.yaml to config.yaml and edit it.")
    with config_path.open(encoding="utf-8") as handle:
        cfg = yaml.safe_load(handle) or {}
    for section in ("app", "sources", "profile", "llm"):
        cfg.setdefault(section, {})
    for key, value in DEFAULT_CONFIG.items():
        for subkey, default in value.items():
            cfg[ key ].setdefault(subkey, default)
    return cfg
