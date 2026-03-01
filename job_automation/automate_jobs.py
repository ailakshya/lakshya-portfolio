import os
import requests
import json
from datetime import datetime
import openai # For GPT-4
# import anthropic # Optional: If you prefer Claude 3

# ==========================================
# CONFIGURATION - ADD YOUR API KEYS HERE
# ==========================================
# 1. Get your OpenAI API key: https://platform.openai.com/api-keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")

# No paid API keys required for scraping! We use LinkedIn HTML & Remotive JSON arrays.

# Define the keywords for the roles you want
JOB_KEYWORDS = ["Machine Learning Engineer", "Systems Engineer", "AI Researcher Intern", "Multimodal", "PyTorch"]
LOCATION = "Remote" # Or "San Francisco", "India", etc.

# Define your base resume text here
USER_RESUME = """
Lakshya - AI Researcher and Systems Engineer
Skills: PyTorch, Go, Multimodal Representation Learning, GPU Optimization, RAG, Python, PostgreSQL, NextJS.
Experience:
- Published "Adaptive Gradient Harmonization" to mitigate Modality Dominance in Unified Representation Learning.
- Reduced DFU Image Classification cost via Knowledge Distillation & Network Pruning for efficient edge deployment.
- Built GoBlog CMS handling 10k concurrent requests, architectured a highly concurrent data ingestion system.
- Designed High-Performance AI infrastructure targeting low-level GPU optimizations.
"""
# ==========================================

openai.api_key = OPENAI_API_KEY

def fetch_real_jobs(keyword, location="remote"):
    """
    Scrapes jobs from LinkedIn's public board and the Remotive API globally without API keys.
    """
    jobs = []
    
    # 1. Scrape LinkedIn Public Job Board
    print(f"🔍 Scraping LinkedIn for {keyword}...")
    import urllib.parse
    from bs4 import BeautifulSoup
    
    url = f"https://www.linkedin.com/jobs/search?keywords={urllib.parse.quote(keyword)}&location={urllib.parse.quote(location)}&f_TPR=r86400"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        job_cards = soup.find_all("div", class_="base-search-card__info")
        for card in job_cards:
            title_elem = card.find("h3", class_="base-search-card__title")
            company_elem = card.find("a", class_="hidden-nested-link")
            url_elem = card.parent.find("a", class_="base-card__full-link")
            
            if title_elem and company_elem and url_elem:
                title = title_elem.text.strip()
                company = company_elem.text.strip()
                job_url = url_elem["href"].split("?")[0]
                
                jobs.append({
                    "title": title,
                    "company": company,
                    "url": job_url,
                    "description": f"Role: {title} at {company}. (LinkedIn listing). Candidate must evaluate fit based on standard {keyword} responsibilities."
                })
    except Exception as e:
        print(f"LinkedIn Scrape Error: {e}")

    # 2. Scrape Remotive Free JSON API
    print(f"🔍 Querying Remotive API for {keyword}...")
    try:
        rem_url = f"https://remotive.com/api/remote-jobs?search={urllib.parse.quote(keyword)}"
        rem_res = requests.get(rem_url, timeout=10)
        if rem_res.status_code == 200:
            rem_jobs = rem_res.json().get("jobs", [])
            for r in rem_jobs:
                jobs.append({
                    "title": r.get("title"),
                    "company": r.get("company_name"),
                    "url": r.get("url"),
                    "description": BeautifulSoup(r.get("description", ""), "html.parser").text[:500] + "..." # Truncate HTML
                })
    except Exception as e:
        print(f"Remotive API Error: {e}")

    return jobs

def evaluate_job_match(job):
    """
    Uses OpenAI GPT-3.5 to determine if the job aligns with your M.Tech profile.
    """
    openai_key = os.environ.get("OPENAI_API_KEY", OPENAI_API_KEY)
    if openai_key and "YOUR" not in openai_key:
        openai.api_key = openai_key
        
    print(f"🧠 Evaluating Match: {job['title']} at {job['company']}")
    
    prompt = f"""
    You are an expert technical recruiter for elite AI labs (like OpenAI, DeepMind, Anthropic).
    Analyze this Job Description and extract structured details. The candidate is highly specialized in Multimodal ML and High-Performance Systems (Go/PyTorch).
    
    Return ONLY a valid JSON object with these exact keys:
    {{
      "is_match": true,
      "match_reason": "Brief 1-sentence explanation.",
      "contact_email": "found_or_guessed_email@company.com",
      "skills_required": ["PyTorch", "Go", "CUDA"],
      "key_requirements": ["3+ years ML experience", "PhD preferred"],
      "expected_salary": "$150,000 - $200,000"
    }}
    
    Rules:
    - skills_required: list of up to 8 specific technical skills mentioned in the job description.
    - key_requirements: list of up to 5 concise requirements (experience, degree, etc.).
    - expected_salary: exact salary range from job description, or "Not specified" if missing.
    - contact_email: extract from job text, or guess based on company name (e.g. careers@company.com).
    - is_match: true if this is a strong fit for the candidate.

    Job Title: {job['title']}
    Company: {job['company']}
    Job Description: {job['description']}

    Candidate Resume:
    {USER_RESUME}
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        result = response.choices[0].message.content
        try:
            import json
            # Strip markdown code fences if present
            clean = result.strip().strip("```json").strip("```").strip()
            data = json.loads(clean)
            is_match = data.get("is_match", False)
            reason = data.get("match_reason", "")
            contact_email = data.get("contact_email", f"careers@{job['company'].lower().replace(' ', '')}.com")
            skills = data.get("skills_required", [])
            requirements = data.get("key_requirements", [])
            salary = data.get("expected_salary", "Not specified")
            return is_match, reason, contact_email, skills, requirements, salary
        except Exception:
            is_match = "true" in result.lower()
            return is_match, result, f"careers@{job['company'].lower().replace(' ', '')}.com", [], [], "Not specified"
    except Exception as e:
        print(f"❌ OpenAI API Error during evaluation. Check your API Key.")
        return False, str(e), "", [], [], "Not specified"

def draft_cold_email(job):
    """
    Uses GPT-4o (or 4) to draft a highly personalized, aggressive cold email to the hiring manager.
    """
    openai_key = os.environ.get("OPENAI_API_KEY", OPENAI_API_KEY)
    if openai_key and "YOUR" not in openai_key:
        openai.api_key = openai_key
        
    prompt = f"""
    Write a concise, compelling cold email (max 120 words) to the hiring recruiter at {job['company']} for the {job['title']} role.
    Do NOT use fluff or generic corporate speak. Be direct, technical, and confident.
    Explicitly connect a SPECIFIC skill from the candidate's resume (e.g., Adaptive Gradient Harmonization, Go concurrency, PyTorch GPU optimization) to the specific needs in the job description.
    Tone: Elite 10x engineer/researcher.
    End with a call to action asking them to check the portfolio at https://ailakshya.in

    Job Description: {job['description']}

    Candidate Resume:
    {USER_RESUME}
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o", # Use gpt-4 if you don't have access to 4o
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Could not generate email. Is your API key correct?"

def main():
    if "YOUR_OPENAI_API_KEY" in OPENAI_API_KEY:
        print("⚠️  CRITICAL: You must set your OPENAI_API_KEY in the script or environment variables to generate emails!")
        return

    all_jobs = []
    # Fetch jobs for a couple of keywords
    for keyword in ["Machine Learning Systems", "AI Research Intern"]:
        all_jobs.extend(fetch_real_jobs(keyword, LOCATION))
        
    # Deduplicate
    seen_urls = set()
    unique_jobs = []
    for job in all_jobs:
        if job["url"] not in seen_urls:
            unique_jobs.append(job)
            seen_urls.add(job["url"])

    report_lines = [f"# Lakshya's Automated Job Matches - {datetime.now().strftime('%Y-%m-%d')}\n"]
    report_lines.append("> Auto-generated using OpenAI GPT-4 filtering and Adzuna scraping.\n\n")
    
    match_count = 0
    for job in unique_jobs:
        is_match, reason, contact_email = evaluate_job_match(job)
        if is_match:
            match_count += 1
            report_lines.append(f"## ✅ MATCH: {job['title']} @ {job['company']}")
            report_lines.append(f"**Apply Link:** [Click Here to Apply]({job['url']})")
            report_lines.append(f"**📬 Contact Email:** {contact_email}")
            report_lines.append(f"\n**AI Reasoning:**\n```json\n{reason}\n```\n")
            
            print(f"✍️ Drafting email for {job['company']}...")
            email = draft_cold_email(job)
            report_lines.append(f"### ✉️ Drafted Cold Email To Send:\n\n---\n{email}\n---\n\n")
            
    if match_count == 0:
        report_lines.append("\n*No highly-aligned jobs found today. Try broadening the search keywords.*")
            
    # Save the report
    with open("job_matches_report.md", "w") as f:
        f.writelines(report_lines)
    
    print(f"\n✅ Done! Found {match_count} strong matches. Open 'job_matches_report.md' to see your drafted emails.")

if __name__ == "__main__":
    main()
