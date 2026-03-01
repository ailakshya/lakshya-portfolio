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

# 2. To get real job postings, get a free API key from Adzuna (https://developer.adzuna.com/) or SerpApi
ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID", "YOUR_APP_ID_HERE")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY", "YOUR_APP_KEY_HERE")

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
    Fetches real job listings using the Adzuna API. 
    If keys are missing, falls back to a mock list.
    """
    if "YOUR_APP" in ADZUNA_APP_ID:
        print("⚠️ Adzuna API keys not set. Falling back to mock data for demonstration.")
        return [
            {
                "title": "Machine Learning Systems Engineer",
                "company": "Anthropic",
                "url": "https://anthropic.com/careers",
                "description": "Build high-concurrency data ingestion pipelines to feed our frontier RLHF models. Experience with Go, Python, and PyTorch is required. Strong focus on AI Safety and systems performance."
            },
            {
                "title": "AI Research Intern (Vision Language Models)",
                "company": "Upstage AI",
                "url": "https://upstage.ai",
                "description": "Looking for interns to push the boundary of Multimodal LLMs. Must understand modality imbalance and gradient issues in training large vision networks."
            },
            {
                "title": "Senior Frontend Developer",
                "company": "RandomTech Inc.",
                "url": "https://example.com/job",
                "description": "Looking for 5+ years of React experience to build our web dashboard."
            }
        ]

    # Real API Call to Adzuna
    print(f"🔍 Fetching {keyword} jobs from Adzuna API...")
    url = f"https://api.adzuna.com/v1/api/jobs/us/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 10,
        "what": keyword,
        "where": location
    }
    
    response = requests.get(url, params=params)
    jobs = []
    if response.status_code == 200:
        results = response.json().get("results", [])
        for r in results:
            jobs.append({
                "title": r.get("title"),
                "company": r.get("company", {}).get("display_name"),
                "url": r.get("redirect_url"),
                "description": r.get("description")
            })
    return jobs

def evaluate_job_match(job):
    """
    Uses OpenAI GPT-3.5 to determine if the job aligns with your M.Tech profile.
    """
    print(f"🧠 Evaluating Match: {job['title']} at {job['company']}")
    
    prompt = f"""
    You are an expert technical recruiter for elite AI labs (like OpenAI, DeepMind, Anthropic).
    Analyze this Job Description against the Candidate's Resume. This candidate is highly specialized in Multimodal ML and High-Performance Systems (Go/PyTorch).
    
    Return ONLY a JSON response in this exact format:
    {{"is_match": true/false, "match_reason": "Brief 1-sentence explanation why it is or isn't a fit."}}

    Job Title: {job['title']}
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
        # Simple JSON extraction
        is_match = "true" in result.lower()
        return is_match, result
    except Exception as e:
        print(f"❌ OpenAI API Error during evaluation. Check your API Key.")
        return False, str(e)

def draft_cold_email(job):
    """
    Uses GPT-4o (or 4) to draft a highly personalized, aggressive cold email to the hiring manager.
    """
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
        is_match, reason = evaluate_job_match(job)
        if is_match:
            match_count += 1
            report_lines.append(f"## ✅ MATCH: {job['title']} @ {job['company']}")
            report_lines.append(f"**Apply Link:** [Click Here to Apply]({job['url']})")
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
