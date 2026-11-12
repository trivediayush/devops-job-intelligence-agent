import requests

def explain_with_ollama(job, profile, model="qwen2.5:1.5b", base_url="http://localhost:11434"):
    """Optional explanation only. This function never calculates or changes the numeric score."""
    prompt = (
        "You are a cautious job-description analyst. Use only the supplied facts. "
        "Do not invent experience, salary, company facts, or qualifications. "
        "Return concise bullets: relevant requirements, likely gaps, questions to verify. "
        "State when information is missing.\n\n"
        f"Candidate profile: {profile}\n\nJob title: {job.get('title')}\n"
        f"Description: {(job.get('description') or '')[:9000]}"
    )
    response = requests.post(
        base_url.rstrip("/") + "/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=120
    )
    response.raise_for_status()
    return response.json().get("response", "").strip()
