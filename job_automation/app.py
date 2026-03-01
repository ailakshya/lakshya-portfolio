import streamlit as st
import os
from automate_jobs import fetch_real_jobs, evaluate_job_match, draft_cold_email, USER_RESUME

st.set_page_config(page_title="AI Job Finder & Outreach Portal", page_icon="🤖", layout="wide")

st.title("🤖 AI Job Finder & Automated Outreach")
st.markdown("Search for jobs online, evaluate them against your specific profile using OpenAI, and instantly draft 10x cold emails.")

# =========================
# SIDEBAR: CONFIGURATION
# =========================
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Keys
    st.subheader("API Keys")
    openai_key = st.text_input("OpenAI API Key (Required)", type="password", value=os.environ.get("OPENAI_API_KEY", ""))
    adzuna_id = st.text_input("Adzuna App ID (Optional)", type="password", value=os.environ.get("ADZUNA_APP_ID", ""))
    adzuna_key = st.text_input("Adzuna App Key (Optional)", type="password", value=os.environ.get("ADZUNA_APP_KEY", ""))
    
    st.markdown("---")
    
    # Resume editing
    st.subheader("📄 Your Profile / Resume")
    resume_text = st.text_area("Edit Profile to feed to AI:", value=USER_RESUME, height=300)

# =========================
# MAIN AREA: SEARCH ACTIONS
# =========================
st.subheader("🔍 Search Parameters")
col1, col2 = st.columns(2)
with col1:
    presets = [
        "Machine Learning Systems Engineer",
        "AI Research Intern",
        "GPU Performance Engineer",
        "Data Infrastructure Engineer",
        "Backend Engineer - Go",
        "Computer Vision Researcher",
        "Multimodal AI Engineer",
        "Deep Learning Engineer",
        "NLP Engineer",
        "MLOps Engineer",
        "Large Language Model (LLM) Engineer",
        "Applied Scientist",
        "Robotics Software Engineer",
        "AI Hardware Architect"
    ]
    selected_presets = st.multiselect("Select Job Keyword(s) Presets", presets, default=["Machine Learning Systems Engineer"])
    custom_keyword = st.text_input("Add Custom Keyword (Optional)", value="")
    
    # Combine selected presets and any custom keyword
    job_keywords = selected_presets
    if custom_keyword.strip():
        job_keywords.append(custom_keyword.strip())
with col2:
    job_location = st.text_input("Location", value="Remote")

# Inject keys back into env vars for the backend logic
os.environ["OPENAI_API_KEY"] = openai_key
os.environ["ADZUNA_APP_ID"] = adzuna_id
os.environ["ADZUNA_APP_KEY"] = adzuna_key

if st.button("🚀 Start AI Job Hunt", type="primary"):
    if not openai_key or "YOUR" in openai_key:
        st.error("❌ You must provide a valid OpenAI API Key in the sidebar to run the AI evaluator.")
    elif not job_keywords:
        st.error("❌ Please select at least one job keyword preset or enter a custom keyword.")
    else:
        st.markdown("---")
        
        # 1. Fetching
        all_jobs = []
        with st.status(f"Searching Adzuna for {len(job_keywords)} keywords in '{job_location}'...", expanded=False) as status:
            for keyword in job_keywords:
                st.write(f"Fetching '{keyword}' jobs...")
                all_jobs.extend(fetch_real_jobs(keyword, job_location))
            
            # Deduplicate by URL
            seen_urls = set()
            jobs = []
            for j in all_jobs:
                if j["url"] not in seen_urls:
                    jobs.append(j)
                    seen_urls.add(j["url"])
                    
            status.update(label=f"Found {len(jobs)} unique potential jobs across {len(job_keywords)} keywords. Now filtering with AI...", state="complete")
        
        if not jobs:
            st.warning("No jobs found with those keywords.")
            st.stop()
            
        # 2. Filtering & Emailing
        match_count = 0
        progress_bar = st.progress(0)
        
        st.subheader("✨ AI Evaluated Matches")
        
        for i, job in enumerate(jobs):
            # Evaluate using OpenAI
            is_match, reason = evaluate_job_match(job)
            
            if is_match:
                match_count += 1
                with st.container():
                    st.markdown(f"### [🔗 {job['title']} @ {job['company']}]({job['url']})")
                    
                    # Display the AI's logic
                    st.info(f"**AI Reasoning:**\n\n{reason}")
                    
                    # Draft the email
                    with st.spinner(f"Drafting highly personalized cold email to {job['company']}..."):
                        email_draft = draft_cold_email(job)
                        
                    # Show the email in a nice copyable format
                    with st.expander("📬 View Drafted Cold Email", expanded=True):
                        st.code(email_draft, language="markdown")
                    
                    st.markdown("---")
            
            # Update Progress
            progress_bar.progress((i + 1) / len(jobs))
            
        if match_count == 0:
            st.warning("The AI evaluated all the jobs, but none were a strong enough technical match for your elite profile. Try broadening the search keyword!")
        else:
            st.success(f"Successfully evaluated and drafted {match_count} highly targeted emails!")
