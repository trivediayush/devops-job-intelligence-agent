from dataclasses import dataclass
from typing import Optional

@dataclass
class Job:
    source: str
    source_id: str
    title: str
    company: str
    location: str = "Unknown"
    url: str = ""
    description: str = ""
    employment_type: str = "Unknown"
    posted_at: Optional[str] = None
    salary_text: Optional[str] = None

