"""
analyze_session.py
Parses a saved AI Job Hunt Markdown file and extracts:
  - List of matched companies / job titles
  - Skill frequency chart data (keyword NLP)
  - Salary estimation with live USD->INR conversion
Returns structured data consumable by app.py
"""
import re
import os
from collections import Counter
import urllib.request
import json as _json

_USD_TO_INR_CACHE = {"rate": None}

def get_usd_to_inr() -> float:
    """Fetch live USD to INR exchange rate. Falls back to 84.0 if offline."""
    if _USD_TO_INR_CACHE["rate"] is not None:
        return _USD_TO_INR_CACHE["rate"]
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = _json.loads(resp.read())
        rate = data["rates"]["INR"]
        _USD_TO_INR_CACHE["rate"] = rate
        return rate
    except Exception:
        _USD_TO_INR_CACHE["rate"] = 84.0  # Reasonable offline fallback
        return 84.0

def usd_to_inr_str(usd_val: int) -> str:
    """Convert a USD int to a formatted INR string in lakhs."""
    rate = get_usd_to_inr()
    inr = usd_val * rate
    lakhs = inr / 100000
    return f"₹{lakhs:.1f}L"


# Common tech skills to look for in the text
SKILL_KEYWORDS = [
    "PyTorch", "TensorFlow", "Python", "Go", "Golang", "CUDA",
    "C++", "JavaScript", "TypeScript", "Rust", "Java", "Kubernetes",
    "Docker", "AWS", "GCP", "Azure", "PostgreSQL", "MongoDB",
    "SQL", "Machine Learning", "Deep Learning", "NLP", "LLM",
    "RAG", "Transformer", "BERT", "GPT", "Diffusion", "RL",
    "Computer Vision", "Multimodal", "Knowledge Distillation",
    "Model Pruning", "MLOps", "Spark", "Hadoop", "Redis", "Kafka",
    "FastAPI", "Flask", "Django", "React", "NextJS", "HuggingFace",
    "OpenCV", "scikit-learn", "JAX", "XLA", "ONNX", "TensorRT",
    "vLLM", "LoRA", "PEFT", "Triton", "NCCL", "RLHF", "Fine-tuning",
    "Data Engineering", "System Design", "Distributed Systems"
]

SALARY_PATTERN = re.compile(
    r"\$[\d,]+ ?[-–—] ?\$[\d,]+[kKmM]?|"
    r"[\$£€][\d,.]+[kKmM]? ?[-–—] ?[\$£€][\d,.]+[kKmM]?|"
    r"[\d,.]+[kKlL] ?[-–—] ?[\d,.]+[kKlL] ?(?:LPA|USD|INR|EUR)?",
    re.IGNORECASE
)

# Role-based salary lookup (median USD annual, source: levels.fyi / glassdoor 2024)
ROLE_SALARY_TABLE = {
    "machine learning engineer":        (150000, 220000),
    "ml engineer":                       (150000, 220000),
    "machine learning systems engineer": (160000, 230000),
    "ai research scientist":             (165000, 250000),
    "ai researcher":                     (150000, 240000),
    "research scientist":                (130000, 220000),
    "research engineer":                 (140000, 210000),
    "applied scientist":                 (130000, 200000),
    "deep learning engineer":            (145000, 215000),
    "nlp engineer":                      (140000, 210000),
    "computer vision engineer":          (140000, 210000),
    "computer vision researcher":        (145000, 220000),
    "multimodal ai engineer":            (155000, 230000),
    "large language model engineer":     (160000, 240000),
    "llm engineer":                      (155000, 235000),
    "gpu performance engineer":          (165000, 250000),
    "gpu engineer":                      (160000, 240000),
    "mlops engineer":                    (130000, 195000),
    "data scientist":                    (110000, 175000),
    "data engineer":                     (120000, 185000),
    "data infrastructure engineer":      (135000, 200000),
    "backend engineer":                  (125000, 195000),
    "backend software engineer":         (125000, 195000),
    "software engineer":                 (120000, 190000),
    "senior software engineer":          (160000, 240000),
    "staff engineer":                    (200000, 300000),
    "principal engineer":                (220000, 350000),
    "robotics software engineer":        (140000, 210000),
    "ai hardware architect":             (180000, 270000),
    "ai research intern":                (50000,  90000),
    "research intern":                   (45000,  80000),
}

def _lookup_salary(title: str) -> str:
    """Return a salary range string from the lookup table based on job title."""
    title_lower = title.lower().strip()
    # Direct match first
    if title_lower in ROLE_SALARY_TABLE:
        lo, hi = ROLE_SALARY_TABLE[title_lower]
        return f"~${lo:,} - ${hi:,} / yr (est.)"
    # Partial match
    for role, (lo, hi) in ROLE_SALARY_TABLE.items():
        if role in title_lower or title_lower in role:
            return f"~${lo:,} - ${hi:,} / yr (est.)"
    # Keyword fallback
    if any(k in title_lower for k in ["senior", "staff", "lead", "principal"]):
        return "~$180,000 - $280,000 / yr (est.)"
    if any(k in title_lower for k in ["intern", "junior"]):
        return "~$60,000 - $100,000 / yr (est.)"
    if any(k in title_lower for k in ["ml", "ai", "machine learning", "deep learning"]):
        return "~$140,000 - $210,000 / yr (est.)"
    return "Not disclosed"


def _ai_extract_salary(job_title: str, company: str, job_text: str) -> str:
    """Use OpenAI to estimate the expected salary for a job if not found by regex or lookup."""
    try:
        import openai
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        if not openai_key or "YOUR" in openai_key:
            return _lookup_salary(job_title)
        
        openai.api_key = openai_key
        prompt = f"""Based on this job posting information, estimate the expected salary range.
Job Title: {job_title}
Company: {company}
Context from the posting:
{job_text[:800]}

Return ONLY a JSON object like this:
{{"salary": "$120,000 - $180,000", "currency": "USD", "basis": "annual"}}

If you genuinely cannot estimate from any of the context, return:
{{"salary": "Not disclosed", "currency": "USD", "basis": "annual"}}
"""
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        result = response.choices[0].message.content.strip()
        clean = result.strip("`").replace("json", "").strip()
        import json
        data = json.loads(clean)
        return data.get("salary", _lookup_salary(job_title))
    except Exception:
        return _lookup_salary(job_title)



def parse_markdown_session(md_text: str, use_ai_for_salary: bool = False) -> dict:
    """
    Parse a saved markdown session and return structured analytics.
    
    Args:
        md_text: The full markdown text of the saved session
        use_ai_for_salary: If True, calls OpenAI to estimate salary where not found by regex
    """
    # Split into job blocks
    blocks = re.split(r"## ✅ MATCH:", md_text)
    blocks = [b for b in blocks if b.strip()]

    jobs = []
    skill_counter = Counter()
    salary_data = {}  # {job_label: salary_str}

    for block in blocks:
        lines = block.strip().split("\n")
        title_line = lines[0].strip()
        # e.g. "Machine Learning Engineer @ Google"
        title, _, company = title_line.partition(" @ ")
        title = title.strip()
        company = company.strip()

        # Apply link
        apply_match = re.search(r"\[Click Here to Apply\]\((.+?)\)", block)
        apply_url = apply_match.group(1) if apply_match else "#"

        # Contact email
        email_match = re.search(r"\*\*📬 Contact Email:\*\* ([^\s\n]+)", block)
        email = email_match.group(1) if email_match else ""

        # Try to find salary in the text first (regex)
        salary = "Not disclosed"
        # Check new format (💰 Expected Salary field)
        salary_field = re.search(r"\*\*💰 Expected Salary:\*\* (.+)", block)
        if salary_field:
            salary = salary_field.group(1).strip()
        else:
            # Try general regex
            salary_matches = SALARY_PATTERN.findall(block)
            if salary_matches:
                salary = salary_matches[0]

        # Skill extraction from full block text
        full_text = block.lower()
        matched_skills = []
        for skill in SKILL_KEYWORDS:
            if skill.lower() in full_text:
                skill_counter[skill] += 1
                matched_skills.append(skill)

        # Auto-apply lookup salary if still not found (works offline, no tokens)
        if salary in ("Not disclosed",):
            salary = _lookup_salary(title)

        # Use AI for salary if still not found and AI is requested
        if salary in ("Not disclosed",) and use_ai_for_salary:
            salary = _ai_extract_salary(title, company, block)

        job_label = f"{title} @ {company}"
        salary_data[job_label] = salary

        jobs.append({
            "title": title,
            "company": company,
            "url": apply_url,
            "email": email,
            "skills": matched_skills,
            "salary": salary
        })

    # Build salary chart data in INR - parse USD numeric values and convert
    exchange_rate = get_usd_to_inr()
    salary_numeric_inr = {}
    salary_display = {}  # INR formatted strings for display
    for label, s in salary_data.items():
        nums = re.findall(r"[\d]+", s.replace(",", ""))
        if nums:
            try:
                val_usd = int(nums[0])
                # Convert K notation (e.g. 150k)
                if "k" in s.lower() and val_usd < 10000:
                    val_usd *= 1000
                val_inr = int(val_usd * exchange_rate)
                salary_numeric_inr[label] = val_inr
                salary_display[label] = f"₹{val_inr/100000:.1f}L/yr  (~${val_usd:,})"
            except Exception:
                pass

    return {
        "jobs": jobs,
        "skill_counts": dict(skill_counter.most_common(25)),
        "salary_data": salary_data,
        "salary_numeric": salary_numeric_inr,   # INR values for chart
        "salary_display": salary_display,        # Formatted INR strings
        "exchange_rate": exchange_rate,
        "total_matches": len(jobs)
    }
