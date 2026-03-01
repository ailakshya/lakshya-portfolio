# 🚀 Job Search Automation System

This is a custom Python agent designed to find AI internships and ML System roles across the globe, evaluate them against your specific M.Tech resume using LLMs, and draft highly technical cold emails for you to send to recruiters.

## 1. Setup

First, navigate to the automation directory and install the required Python libraries.

```bash
cd "/Users/lakshya/M.Tech sem 2 reserch paper/portfolio_website/job_automation"
pip install -r requirements.txt
```

## 2. API Keys

For this tool to read job descriptions and actually write emails, it requires an **OpenAI API Key**.
If you want it to scrape live jobs from the internet instead of using mock data, you can optionally get an **Adzuna API key** (free).

Open `automate_jobs.py` in your code editor and paste your keys at the top of the file:

```python
OPENAI_API_KEY = "sk-proj-YOUR-KEY-HERE"

# Optional: For scraping the live web
ADZUNA_APP_ID = "YOUR-ID"
ADZUNA_APP_KEY = "YOUR-KEY"
```

*Note: The script currently defaults to searching for "Machine Learning Systems Engineer" and "AI Research Intern" but you can change the `JOB_KEYWORDS` array inside the script to whatever you want.*

## 3. Run the Automation

Run the script from your terminal:

```bash
python automate_jobs.py
```

## 4. The Output

Once finished, the script will generate a brand new Markdown file called `job_matches_report.md` in the same directory.

If you open `job_matches_report.md`, you will see:
1. Every job that strictly matches your Multimodal & PyTorch background.
2. The direct link to apply.
3. A pre-written, highly persuasive cold email tailored specifically to the company's job description, proving why your Adaptive Gradient Harmonization research makes you a perfect fit. All you have to do is copy, paste, and send!
