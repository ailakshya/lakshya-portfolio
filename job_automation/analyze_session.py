"""
analyze_session.py
Parses a saved AI Job Hunt Markdown file and extracts:
  - List of matched companies / job titles
  - Skill frequency chart data (keyword NLP)
  - Salary mentions
  - Email contacts
Returns structured data consumable by app.py
"""
import re
from collections import Counter

# Common tech skills to look for in the reasoning / email text
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
    "VLLM", "vLLM", "LoRA", "PEFT", "Triton", "NCCL"
]

SALARY_PATTERN = re.compile(
    r"\$[\d,]+ ?[-–—] ?\$[\d,]+|"
    r"[\$£€][\d,.]+[kKmM]? ?[-–—] ?[\$£€][\d,.]+[kKmM]?|"
    r"[\d,.]+[kKlL]? ?[-–—] ?[\d,.]+[kKlL]? ?(?:LPA|USD|INR|EUR)?",
    re.IGNORECASE
)

def parse_markdown_session(md_text: str) -> dict:
    """
    Parse a saved markdown session and return structured analytics.
    """
    # Split into job blocks
    blocks = re.split(r"## ✅ MATCH:", md_text)
    blocks = [b for b in blocks if b.strip()]

    jobs = []
    skill_counter = Counter()
    salaries = []
    emails = []

    for block in blocks:
        # Title & Company
        title_line = block.strip().split("\n")[0]
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
        if email:
            emails.append(email)

        # AI Reasoning / email text (entire block text for skill matching)
        full_text = block.lower()

        # Skill extraction
        matched_skills = []
        for skill in SKILL_KEYWORDS:
            if skill.lower() in full_text:
                skill_counter[skill] += 1
                matched_skills.append(skill)

        # Salary extraction
        salary_matches = SALARY_PATTERN.findall(block)
        salary = salary_matches[0] if salary_matches else "Not specified"
        if salary != "Not specified":
            salaries.append(salary)

        jobs.append({
            "title": title,
            "company": company,
            "url": apply_url,
            "email": email,
            "skills": matched_skills,
            "salary": salary
        })

    return {
        "jobs": jobs,
        "skill_counts": dict(skill_counter.most_common(20)),
        "salaries": salaries,
        "emails": emails,
        "total_matches": len(jobs)
    }
