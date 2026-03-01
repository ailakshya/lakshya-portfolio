import streamlit as st
import os
from datetime import datetime
from automate_jobs import fetch_real_jobs, evaluate_job_match, draft_cold_email, USER_RESUME

st.set_page_config(page_title="AI Job Finder & Outreach Portal", page_icon="🤖", layout="wide")

if "last_export_md" not in st.session_state:
    st.session_state.last_export_md = ""
if "last_match_count" not in st.session_state:
    st.session_state.last_match_count = 0
if "last_filename" not in st.session_state:
    st.session_state.last_filename = ""

st.title("🤖 AI Job Finder & Automated Outreach")
st.markdown("Search for jobs online, evaluate them against your specific profile using OpenAI, and instantly draft 10x cold emails.")

with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Keys
    st.subheader("API Keys")
    openai_key = st.text_input("OpenAI API Key (Required)", type="password", value=os.environ.get("OPENAI_API_KEY", ""))
    
    st.markdown("---")
    
    # Past Searches functionality
    st.subheader("📂 Past Searches")
    os.makedirs("saved_searches", exist_ok=True)
    saved_files = sorted([f for f in os.listdir("saved_searches") if f.endswith(".md")], reverse=True)
    if saved_files:
        for sf in saved_files:
            with open(os.path.join("saved_searches", sf), "r") as f:
                file_content = f.read()
            
            # Create a clean label
            label_time = sf.replace("ai_job_matches_", "").replace(".md", "")
            
            st.download_button(
                label=f"📥 Saved: {label_time}", 
                data=file_content, 
                file_name=sf, 
                mime="text/markdown", 
                key=sf
            )
    else:
        st.info("No past searches run yet.")

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

if st.button("🚀 Start AI Job Hunt", type="primary"):
    if not openai_key or "YOUR" in openai_key:
        st.error("❌ You must provide a valid OpenAI API Key in the sidebar to run the AI evaluator.")
    elif not job_keywords:
        st.error("❌ Please select at least one job keyword preset or enter a custom keyword.")
    else:
        st.markdown("---")
        
        # 1. Fetching
        all_jobs = []
        with st.status(f"Global Scraping LinkedIn & Web for {len(job_keywords)} roles in '{job_location}'...", expanded=False) as status:
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
        
        # Initialize export data
        export_md = f"# AI Job Hunt Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        st.subheader("✨ AI Evaluated Matches")
        
        for i, job in enumerate(jobs):
            # Evaluate using OpenAI
            is_match, reason, contact_email = evaluate_job_match(job)
            
            if is_match:
                match_count += 1
                with st.container():
                    st.markdown(f"### [🔗 {job['title']} @ {job['company']}]({job['url']})")
                    st.success(f"**📬 Contact Email:** [{contact_email}](mailto:{contact_email})")
                    
                    # Display the AI's logic
                    st.info(f"**AI Reasoning:**\n\n{reason}")
                    
                    # Draft the email
                    with st.spinner(f"Drafting highly personalized cold email to {job['company']}..."):
                        email_draft = draft_cold_email(job)
                        
                    # Show the email in a nice copyable format
                    with st.expander("📬 View Drafted Cold Email", expanded=True):
                        st.code(email_draft, language="markdown")
                    
                    st.markdown("---")
                    
                    # Append to export
                    export_md += f"## ✅ MATCH: {job['title']} @ {job['company']}\n"
                    export_md += f"**Apply Link:** [Click Here to Apply]({job['url']})\n"
                    export_md += f"**📬 Contact Email:** {contact_email}\n\n"
                    export_md += f"**AI Reasoning:**\n```json\n{reason}\n```\n\n"
                    export_md += f"### ✉️ Drafted Cold Email:\n\n---\n{email_draft}\n---\n\n"
            
            # Update Progress
            progress_bar.progress((i + 1) / len(jobs))
            
        if match_count == 0:
            st.warning("The AI evaluated all the jobs, but none were a strong enough technical match for your elite profile. Try broadening the search keyword!")
        else:
            st.success(f"Successfully evaluated and drafted {match_count} highly targeted emails!")
            
            # Save the file locally
            os.makedirs("saved_searches", exist_ok=True)
            filename = f"ai_job_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = os.path.join("saved_searches", filename)
            with open(filepath, "w") as f:
                f.write(export_md)
                
            # Save to session state so we can display download button persistently outside the 'if' block
            st.session_state.last_export_md = export_md
            st.session_state.last_match_count = match_count
            st.session_state.last_filename = filename

# =========================
# LATEST RESULTS EXPORT
# =========================
if st.session_state.last_export_md:
    st.markdown("---")
    st.subheader(f"📥 Download Latest Session ({st.session_state.last_match_count} Matches)")
    st.download_button(
        label="Download Markdown Report",
        data=st.session_state.last_export_md,
        file_name=st.session_state.last_filename,
        mime="text/markdown",
        type="primary"
    )
