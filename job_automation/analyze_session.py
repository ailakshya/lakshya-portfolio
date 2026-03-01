"""
analyze_session.py
Parses a saved AI Job Hunt Markdown file and extracts:
  - List of matched companies / job titles
  - Skill frequency chart data (keyword NLP)
  - Salary estimation via OpenAI
Returns structured data consumable by app.py
"""
import re
import os
from collections import Counter

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

def _ai_extract_salary(job_title: str, company: str, job_text: str) -> str:
    """Use OpenAI to estimate the expected salary for a job if not found by regex."""
    try:
        import openai
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        if not openai_key or "YOUR" in openai_key:
            return "AI key not set"
        
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
        return data.get("salary", "Not disclosed")
    except Exception:
        return "Not disclosed"


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

        # Use AI for salary if not found and AI is requested
        if salary == "Not disclosed" and use_ai_for_salary:
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

    # Build salary chart data - parse numeric values where possible
    salary_numeric = {}
    for label, s in salary_data.items():
        # Try to extract first number for approximate sorting
        nums = re.findall(r"[\d,]+", s.replace(",", ""))
        if nums:
            try:
                val = int(nums[0].replace(",", ""))
                # Convert K to actual value
                if "k" in s.lower() and val < 10000:
                    val *= 1000
                salary_numeric[label] = val
            except Exception:
                pass

    return {
        "jobs": jobs,
        "skill_counts": dict(skill_counter.most_common(25)),
        "salary_data": salary_data,
        "salary_numeric": salary_numeric,
        "total_matches": len(jobs)
    }
