"""
GATE IN & RA Master Preparation Command Center (23-Week Cycle)
Main Streamlit Application Entry Point
Strictly tailored for Instrumentation Engineering (IN) & Robotics & Automation (RA)
"""
import streamlit as st
import os
from datetime import date, datetime
from database.db import init_db, get_setting, set_setting
from components.morning_recap import render_morning_recap
from components.inapp_studio import render_inapp_studio
from components.attendance_form import render_attendance_form
from components.dashboard_view import render_dashboard_view
from components.formula_vault import render_formula_vault
from components.aptitude_tracker import render_aptitude_tracker
from components.virtual_calc import render_virtual_calc
from components.pomodoro_timer import render_pomodoro_timer
from components.error_quarantine import render_error_quarantine
from config import PAPERS, TOTAL_WEEKS

# Page Configuration
st.set_page_config(
    page_title="GATE IN & RA Master Command Center",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize SQLite Database & Auto-Seed
init_db()

# Custom CSS for Modern Clean Exam UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 1.2rem;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# Sidebar: Settings & Quick Controls
# =============================================================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/6/69/IIT_Madras_Logo.svg/240px-IIT_Madras_Logo.svg.png", width=70)
    st.title("GATE Command Center")
    st.caption("23-Week Prep for IN (Instrumentation) & RA (Robotics)")

    st.markdown("---")

    # Paper Track Selection (IN vs RA vs Dual)
    saved_paper = get_setting("target_paper", "IN")
    paper_options = list(PAPERS.keys())
    selected_paper_code = st.selectbox(
        "🎯 Active Paper Focus:",
        options=paper_options,
        index=paper_options.index(saved_paper) if saved_paper in paper_options else 0,
        format_func=lambda code: PAPERS[code]
    )
    if selected_paper_code != saved_paper:
        set_setting("target_paper", selected_paper_code)
        st.rerun()

    # Timeline Start Date
    saved_start_date = get_setting("start_date", date.today().strftime("%Y-%m-%d"))
    try:
        current_start = datetime.strptime(saved_start_date, "%Y-%m-%d").date()
    except Exception:
        current_start = date.today()

    new_start_date = st.date_input("🗓️ 23-Week Cycle Start Date:", value=current_start)
    if new_start_date.strftime("%Y-%m-%d") != saved_start_date:
        set_setting("start_date", new_start_date.strftime("%Y-%m-%d"))
        st.rerun()

    st.markdown("---")

    # Optional Gemini API Key Input
    st.markdown("#### 🤖 Gemini API Key")
    api_key_input = st.text_input(
        "API Key (Optional):",
        value=st.session_state.get("gemini_api_key", os.environ.get("GEMINI_API_KEY", "")),
        type="password",
        help="Provide your Google Gemini API key to power custom AI schedules. If left blank, the app runs seamlessly on its built-in rule engine."
    )
    if api_key_input:
        st.session_state["gemini_api_key"] = api_key_input

    st.markdown("---")
    st.markdown("### 📌 Diagnostic Error Taxonomy")
    st.markdown("""
    - **[C]** Conceptual Principle Gap
    - **[F]** Formula Recall Decay
    - **[A]** Strategy / Method Deficit
    - **[I]** Reading / Boundary Slip
    - **[T]** Time Pressure Panic
    - **[S]** Virtual Calc / Arithmetic Error
    """)

# =============================================================================
# Main Header
# =============================================================================
st.markdown('<div class="main-header">🎯 GATE IN & RA Master Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">23-Week Self-Contained Prep for <b>{PAPERS[selected_paper_code]}</b> | Engineering Math • Sensors & Transducers • Circuits • Signals & Control • Robot Kinematics & Vision • General Aptitude</div>', unsafe_allow_html=True)

# =============================================================================
# Primary Navigation Tabs
# =============================================================================
tabs = st.tabs([
    "🌅 5-Min Morning Recap",
    "🎯 In-App Study Studio",
    "📋 Daily Check-In & AI Schedule",
    "🧠 Formula Vault",
    "🎯 Weekend Aptitude",
    "🖩 Calculator & Timer",
    "🔄 Redo Mistakes Queue",
    "📊 Analytics & Pacing"
])

with tabs[0]:
    render_morning_recap()

with tabs[1]:
    render_inapp_studio()

with tabs[2]:
    render_attendance_form()

with tabs[3]:
    render_formula_vault()

with tabs[4]:
    render_aptitude_tracker()

with tabs[5]:
    st.markdown("### 🖩 Official GATE Testing Tools: Virtual Calculator & Sprint Timer")
    calc_tab, timer_tab = st.tabs(["🖩 TCS iON Virtual Calculator", "⏱️ 3-Phase Pomodoro Study Timer"])
    with calc_tab:
        render_virtual_calc()
    with timer_tab:
        render_pomodoro_timer()

with tabs[6]:
    render_error_quarantine()

with tabs[7]:
    render_dashboard_view()
