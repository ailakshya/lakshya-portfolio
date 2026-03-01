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

## 3. Launch the Web Portal

Run the Streamlit app from your terminal:

```bash
streamlit run app.py
```

This will automatically open a sleek web interface in your browser (usually at `http://localhost:8501`).

## 4. Using the Portal

1. **Enter API Keys**: Paste your OpenAI key into the sidebar (it is masked for security).
2. **Edit Profile**: Your M.Tech resume is pre-loaded in the sidebar. You can tweak it on the fly.
3. **Search**: Enter a job title and location in the main panel.
4. **Hit "Start AI Job Hunt"**: 
   - The portal will scrape jobs.
   - You will see a real-time progress bar as GPT-4 evaluates every single job.
   - Highly aligned matches will pop up as rich Markdown cards, complete with the AI's reasoning and a pre-written, highly persuasive outreach email ready to copy and send!
