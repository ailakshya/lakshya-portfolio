import streamlit as st
import os
import json
from datetime import datetime
from automate_jobs import fetch_real_jobs, evaluate_job_match, draft_cold_email, USER_RESUME

STATE_FILE = "job_run_state.json"

st.set_page_config(page_title="AI Job Finder & Outreach Portal", page_icon="🤖", layout="wide")

if "last_export_md" not in st.session_state:
    st.session_state.last_export_md = ""
if "last_match_count" not in st.session_state:
    st.session_state.last_match_count = 0
if "last_filename" not in st.session_state:
    st.session_state.last_filename = ""
if "viewing_past_session" not in st.session_state:
    st.session_state.viewing_past_session = None

st.title("🤖 AI Job Finder & Automated Outreach")
st.markdown("Search for jobs online, evaluate them against your specific profile using OpenAI, and instantly draft 10x cold emails.")

with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Keys
    st.subheader("API Keys")
    openai_key = st.text_input("OpenAI API Key (Required)", type="password", value=os.environ.get("OPENAI_API_KEY", ""))
    
    st.markdown("---")
    
    # Resume editing
    st.subheader("📄 Your Profile / Resume")
    resume_text = st.text_area("Edit Profile to feed to AI:", value=USER_RESUME, height=300)

# =========================
# STATE RECOVERY UTILITIES
# =========================
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return None

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def clear_state():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)

run_state = load_state()

# =========================
# RESUME BANNER
# =========================
if run_state and run_state.get("status") == "processing":
    total = len(run_state["jobs"])
    current = run_state["current_index"]
    st.warning(f"⚠️ **Interrupted Job Hunt Detected:** You have an incomplete AI evaluation paused at {current} / {total} jobs.")
    
    colA, colB = st.columns([1, 4])
    with colA:
        if st.button("▶️ Resume Job Hunt", type="primary"):
            st.session_state.resume_run = True
    with colB:
        if st.button("❌ Cancel & Discard"):
            clear_state()
            st.rerun()
    st.markdown("---")
else:
    st.session_state.resume_run = False

# =========================
# LATEST RESULTS EXPORT & HISTORY VIEW (AT TOP)
# =========================
if st.session_state.last_export_md and not st.session_state.viewing_past_session:
    st.success(f"🎉 Latest Job Hunt Complete! ({st.session_state.last_match_count} Matches Found)")
    st.download_button(
        label="📥 Download Latest Session (Markdown)",
        data=st.session_state.last_export_md,
        file_name=st.session_state.last_filename,
        mime="text/markdown",
        type="primary"
    )
    st.markdown("---")

if st.session_state.viewing_past_session:
    st.info(f"📂 **Viewing Historical Search:** {st.session_state.viewing_past_session['name']}")
    if st.button("❌ Close History View"):
        st.session_state.viewing_past_session = None
        st.rerun()
    
    with st.container():
        st.markdown(st.session_state.viewing_past_session['content'])
    st.markdown("---")

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

start_new_run = st.button("🚀 Start AI Job Hunt", type="primary")

if start_new_run or st.session_state.get("resume_run", False):
    if not openai_key or "YOUR" in openai_key:
        st.error("❌ You must provide a valid OpenAI API Key in the sidebar to run the AI evaluator.")
    elif not job_keywords and not st.session_state.get("resume_run"):
        st.error("❌ Please select at least one job keyword preset or enter a custom keyword.")
    else:
        st.markdown("---")
        
        # If starting fresh
        if start_new_run:
            clear_state()
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
                
            # Initialize state
            run_state = {
                "status": "processing",
                "jobs": jobs,
                "current_index": 0,
                "match_count": 0,
                "export_md": f"# AI Job Hunt Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            }
            save_state(run_state)
            
        # 2. Filtering & Emailing Phase
        jobs = run_state["jobs"]
        start_idx = run_state["current_index"]
        match_count = run_state["match_count"]
        export_md = run_state["export_md"]
        
        progress_bar = st.progress(start_idx / len(jobs) if len(jobs) > 0 else 0)
        
        st.subheader(f"✨ AI Evaluated Matches (Resuming from {start_idx}/{len(jobs)})" if st.session_state.get("resume_run") else "✨ AI Evaluated Matches")
        
        # Render previous matches from the markdown export string (so they don't disappear on resume)
        if start_idx > 0 and "## ✅ MATCH:" in export_md:
            with st.expander("👀 View Matches Found Before Disconnection", expanded=False):
                st.markdown(export_md)
                
        # Stop button container
        stop_btn_col1, stop_btn_col2 = st.columns([1, 4])
        stop_clicked = stop_btn_col1.button("🛑 Stop Search & Finalize", key="stop_search_btn")
        
        if stop_clicked:
            st.session_state.stop_search = True
        else:
            st.session_state.stop_search = False

        for i in range(start_idx, len(jobs)):
            if st.session_state.get("stop_search", False):
                st.warning("🛑 Job Hunt Stopped Early by User.")
                break
                
            job = jobs[i]
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
            
            # Save checkpoint state after every loop iteration
            run_state["current_index"] = i + 1
            run_state["match_count"] = match_count
            run_state["export_md"] = export_md
            save_state(run_state)
            
            # Update Progress
            progress_bar.progress((i + 1) / len(jobs))
            
        # Run Complete! Clear checkpoint state
        run_state["status"] = "completed"
        save_state(run_state)
        clear_state()
        st.session_state.resume_run = False
        
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
# RENDER PAST SEARCHES (At end to capture new saves immediately)
# =========================
with st.sidebar:
    st.markdown("---")
    st.subheader("📂 Past Searches")
    os.makedirs("saved_searches", exist_ok=True)
    saved_files = sorted([f for f in os.listdir("saved_searches") if f.endswith(".md")], reverse=True)
    if saved_files:
        for sf in saved_files:
            with open(os.path.join("saved_searches", sf), "r") as f:
                file_content = f.read()
            
            label_time = sf.replace("ai_job_matches_", "").replace(".md", "")
            
            st.markdown(f"**{label_time}**")
            colA, colB = st.columns([1, 1])
            with colA:
                if st.button("👁️ View", key=f"view_{sf}"):
                    st.session_state.viewing_past_session = {
                        "name": label_time,
                        "content": file_content
                    }
                    st.rerun()
            with colB:
                st.download_button(
                    label="📥 D/L", 
                    data=file_content, 
                    file_name=sf, 
                    mime="text/markdown", 
                    key=f"dl_{sf}"
                )
            st.markdown("---")
    else:
        st.info("No past searches run yet.")
