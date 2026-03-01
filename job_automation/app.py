import streamlit as st
import os
import json
from datetime import datetime
from collections import defaultdict
from analyze_session import parse_markdown_session
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
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
if "skills_data" not in st.session_state:
    st.session_state.skills_data = {}

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
    session_name = st.session_state.viewing_past_session['name']
    session_text = st.session_state.viewing_past_session['content']
    
    st.info(f"📂 **Viewing Historical Search:** `{session_name}`")
    
    col_close, col_ai = st.columns([1, 3])
    with col_close:
        if st.button("❌ Close History View"):
            st.session_state.viewing_past_session = None
            st.rerun()
    with col_ai:
        use_ai = st.toggle("🤖 Extract Salaries with AI (uses OpenAI tokens)", value=False)

    # Parse the session file for analytics
    with st.spinner("🔍 Analyzing session..."):
        analytics = parse_markdown_session(session_text, use_ai_for_salary=use_ai)
    jobs_found = analytics["jobs"]
    total = analytics["total_matches"]
    
    st.success(f"🎉 Session `{session_name}` contained **{total} AI-Matched Jobs**")
    
    # Metric summary row
    salaries_found = [v for v in analytics['salary_data'].values() if v not in ('Not disclosed', 'Not specified', 'AI key not set', 'Not specified')]
    met1, met2, met3 = st.columns(3)
    met1.metric("💼 Total Matches", total)
    met2.metric("💰 Jobs with Salary Data", len(salaries_found))
    met3.metric("🛠️ Unique Skills Detected", len(analytics['skill_counts']))
    
    st.markdown("---")
    
    # --- Skill Frequency Chart ---
    skill_data = analytics["skill_counts"]
    if skill_data:
        st.subheader("📊 Skill Demand Frequency")
        sorted_skills = sorted(skill_data.items(), key=lambda x: x[1], reverse=True)
        skill_names = [s[0] for s in sorted_skills]
        skill_counts_vals = [s[1] for s in sorted_skills]
        
        if HAS_PLOTLY:
            fig_skills = go.Figure(go.Bar(
                x=skill_counts_vals, y=skill_names, orientation='h',
                marker=dict(color=skill_counts_vals, colorscale='Viridis', showscale=True,
                           colorbar=dict(title="Count")),
                text=skill_counts_vals, textposition='outside'
            ))
            fig_skills.update_layout(
                title=f"Skills Required Across {total} Matched Jobs",
                xaxis_title="Number of Job Listings",
                yaxis=dict(autorange="reversed"),
                height=max(400, len(skill_names) * 32),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"), margin=dict(l=20, r=20)
            )
            st.plotly_chart(fig_skills, use_container_width=True)
    
    # --- Salary Chart ---
    salary_numeric = analytics.get("salary_numeric", {})
    salary_disp = analytics.get("salary_display", {})
    exchange_rate = analytics.get("exchange_rate", 84.0)
    if salary_numeric:
        st.subheader(f"💰 Expected Salary by Role (INR) — Live Rate: 💵 1 USD = ₹{exchange_rate:.2f}")
        sorted_sal = sorted(salary_numeric.items(), key=lambda x: x[1], reverse=True)
        sal_labels = [k[:45] + "..." if len(k) > 45 else k for k, _ in sorted_sal]
        sal_vals_inr = [v for _, v in sorted_sal]
        sal_display_texts = [salary_disp.get(k, f"₹{v/100000:.1f}L") for k, v in sorted_sal]
        
        if HAS_PLOTLY:
            fig_sal = go.Figure(go.Bar(
                x=sal_vals_inr, y=sal_labels, orientation='h',
                marker=dict(color=sal_vals_inr, colorscale='RdYlGn', showscale=True,
                           colorbar=dict(title="INR/yr")),
                text=sal_display_texts, textposition='outside'
            ))
            fig_sal.update_layout(
                title="🇮🇳 Estimated Annual Salary in Indian Rupees (INR)",
                xaxis_title="Annual Salary (INR)",
                xaxis_tickprefix="₹",
                xaxis_tickformat=",.0f",
                yaxis=dict(autorange="reversed"),
                height=max(400, len(sal_labels) * 32),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"), margin=dict(l=20, r=20)
            )
            st.plotly_chart(fig_sal, use_container_width=True)
    elif use_ai:
        st.info("No parseable salary data found even with AI analysis.")
    else:
        st.info("💡 Salary estimates shown in INR auto-populated from role database. Enable **'Extract Salaries with AI'** for more precise data.")
    
    # --- Job Table ---
    st.subheader("💼 All Matched Jobs")
    salary_disp_map = analytics.get("salary_display", {})
    for j in jobs_found:
        with st.container():
            c1, c2, c3 = st.columns([3, 2, 2])
            c1.markdown(f"**[🔗 {j['title']} @ {j['company']}]({j['url']})**")
            c2.success(f"📬 [{j['email']}](mailto:{j['email']})" if j['email'] else "📬 N/A")
            # Show INR if available, else show raw salary string
            label = f"{j['title']} @ {j['company']}"
            inr_display = salary_disp_map.get(label, j['salary'])
            c3.info(f"💰 {inr_display}")
            if j['skills']:
                st.caption("Skills: " + " ".join([f"`{s}`" for s in j['skills']][:10]))
            st.markdown("---")
    
    # --- Full raw report (collapsible) ---
    with st.expander("📄 View Full Raw Report", expanded=False):
        st.markdown(session_text)
    
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
            # Evaluate using OpenAI (6-tuple: is_match, reason, email, skills, requirements, salary)
            is_match, reason, contact_email, skills, requirements, salary = evaluate_job_match(job)
            
            if is_match:
                match_count += 1
                
                # Accumulate skills data for chart
                for skill in skills:
                    st.session_state.skills_data[skill] = st.session_state.skills_data.get(skill, 0) + 1
                
                with st.container():
                    st.markdown(f"### [🔗 {job['title']} @ {job['company']}]({job['url']})")
                    
                    c1, c2, c3 = st.columns(3)
                    c1.success(f"📬 **Recruiter Email**\n\n[{contact_email}](mailto:{contact_email})")
                    c2.info(f"💰 **Expected Salary**\n\n{salary}")
                    c3.warning(f"🧠 **AI Reasoning**\n\n{reason}")
                    
                    if requirements:
                        with st.expander("📋 Key Requirements", expanded=False):
                            for req in requirements:
                                st.markdown(f"- {req}")
                    
                    if skills:
                        with st.expander("🛠️ Required Skills", expanded=False):
                            st.markdown(" ".join([f"`{s}`" for s in skills]))
                    
                    # Draft the email
                    with st.spinner(f"Drafting cold email to {job['company']}..."):
                        email_draft = draft_cold_email(job)
                        
                    with st.expander("✉️ View Drafted Cold Email", expanded=True):
                        st.code(email_draft, language="markdown")
                    
                    st.markdown("---")
                    
                    # Append to export
                    export_md += f"## ✅ MATCH: {job['title']} @ {job['company']}\n"
                    export_md += f"**Apply Link:** [Click Here to Apply]({job['url']})\n"
                    export_md += f"**📬 Contact Email:** {contact_email}\n"
                    export_md += f"**💰 Expected Salary:** {salary}\n"
                    export_md += f"**🧠 AI Reasoning:** {reason}\n\n"
                    if requirements:
                        export_md += "**📋 Key Requirements:**\n" + "\n".join([f"- {r}" for r in requirements]) + "\n\n"
                    if skills:
                        export_md += "**🛠️ Required Skills:** " + ", ".join(skills) + "\n\n"
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

# =========================
# SKILLS ANALYTICS CHART
# =========================
if st.session_state.skills_data:
    st.markdown("---")
    st.subheader("📊 In-Demand Skills Analytics (Current Session)")
    
    # Sort by frequency descending
    sorted_skills = sorted(st.session_state.skills_data.items(), key=lambda x: x[1], reverse=True)
    skill_names = [s[0] for s in sorted_skills]
    skill_counts = [s[1] for s in sorted_skills]
    
    if HAS_PLOTLY:
        fig = go.Figure(go.Bar(
            x=skill_counts,
            y=skill_names,
            orientation='h',
            marker=dict(
                color=skill_counts,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Frequency")
            ),
            text=skill_counts,
            textposition='outside'
        ))
        fig.update_layout(
            title="Most Required Skills Across Matched Jobs",
            xaxis_title="Number of Jobs Requiring Skill",
            yaxis_title="Skill",
            yaxis=dict(autorange="reversed"),
            height=max(400, len(skill_names) * 35),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Install plotly for the chart: `pip install plotly`")
        st.table({"Skill": skill_names, "Frequency": skill_counts})

    # Missing skills gap analysis
    your_skills = {"PyTorch", "Go", "Python", "PostgreSQL", "LLM", "RAG", "CUDA",
                   "Multimodal", "Machine Learning", "Deep Learning", "Computer Vision"}
    missing = [s for s in skill_names if s not in your_skills]
    if missing:
        st.warning(f"**📈 Skills Gap:** The following are in-demand skills you may want to highlight more: **{', '.join(missing[:8])}**")
    
    st.markdown("*Chart is reset each new search session.*")
