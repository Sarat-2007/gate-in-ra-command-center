"""
General Aptitude Weekend Tracker (Strict 2-Hour Quota Enforcement)
"""
import streamlit as st
from datetime import date
from database.db import log_aptitude_session, get_aptitude_sessions, get_all_topics
from engine.analytics import calculate_dashboard_metrics
from config import WEEKEND_APTITUDE_HOURS


def render_aptitude_tracker() -> None:
    st.subheader("🎯 General Aptitude Weekend Tracker (15 Marks Compulsory)")
    st.caption("Enforce a strict 2-hour weekend study block for Quantitative, Analytical, Spatial, and Verbal Aptitude.")

    metrics = calculate_dashboard_metrics()
    current_week = metrics["current_week"]
    sessions = get_aptitude_sessions()

    # Calculate this week's logged aptitude hours
    this_week_sessions = [s for s in sessions if s["week_number"] == current_week]
    hours_this_week = sum(s["hours_logged"] for s in this_week_sessions)
    quota_met = hours_this_week >= WEEKEND_APTITUDE_HOURS

    # Quota Progress Card
    q_col1, q_col2, q_col3 = st.columns([1.5, 1, 1])
    with q_col1:
        st.metric(
            label=f"Week {current_week} Weekend Aptitude Quota",
            value=f"{hours_this_week} / {WEEKEND_APTITUDE_HOURS} hrs",
            delta="🟢 Quota Complete" if quota_met else f"🔴 {round(WEEKEND_APTITUDE_HOURS - hours_this_week, 1)} hrs needed",
            delta_color="normal"
        )
    with q_col2:
        total_attempted = sum(s["pyqs_attempted"] for s in sessions)
        total_correct = sum(s["pyqs_correct"] for s in sessions)
        acc = round((total_correct / total_attempted * 100), 1) if total_attempted > 0 else 0.0
        st.metric("Total GA PYQs Solved", total_attempted, delta=f"{acc}% Accuracy")
    with q_col3:
        st.metric("GA Marks Weightage", "15 Marks", delta="10 Questions (5x1M + 5x2M)")

    st.markdown("---")

    # Session Logging Form
    st.markdown("#### ⏱️ Log Weekend Aptitude Study Block")
    with st.form("aptitude_log_form"):
        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        with col_f1:
            sess_date = st.date_input("Session Date:", value=date.today())
            sess_date_str = sess_date.strftime("%Y-%m-%d")
        with col_f2:
            sess_week = st.number_input("Week Number:", min_value=1, max_value=23, value=current_week)
        with col_f3:
            sess_hours = st.slider("Hours Logged:", min_value=0.5, max_value=4.0, value=2.0, step=0.5)

        col_f4, col_f5, col_f6 = st.columns([1.5, 1, 1])
        with col_f4:
            category = st.selectbox("Aptitude Domain:", options=[
                "Quantitative Aptitude (Arithmetic, Algebra, Geometry)",
                "Analytical Reasoning (Syllogisms, Clocks, Calendars, DI)",
                "Spatial Aptitude (2D Paper Folding, 3D Projections, Cubes)",
                "Verbal Ability (Grammar, Sentence Completion, Reading Comprehension)"
            ])
        with col_f5:
            attempted = st.number_input("PYQs Attempted:", min_value=0, max_value=100, value=15)
        with col_f6:
            correct = st.number_input("PYQs Correct:", min_value=0, max_value=100, value=12)

        notes = st.text_input("Friction Points / Notes:", placeholder="e.g. Practiced 2-mark spatial rotation questions from GATE 2021-2024")

        submit_sess = st.form_submit_button("💾 Save Aptitude Session", type="primary")
        if submit_sess:
            log_aptitude_session(
                session_date=sess_date_str,
                week_number=int(sess_week),
                hours_logged=float(sess_hours),
                topic_category=category,
                pyqs_attempted=int(attempted),
                pyqs_correct=int(correct),
                notes=notes
            )
            st.success(f"Logged {sess_hours}h for {category}!")
            st.rerun()

    st.markdown("---")

    # Aptitude Topic Mastery Checklist
    st.markdown("#### 📚 General Aptitude 12-Module Checklist (A97 to A108)")
    all_topics = get_all_topics()
    ga_topics = [t for t in all_topics if "General Aptitude" in t["domain"]]

    for topic in ga_topics:
        is_done = topic["is_completed"] == 1
        with st.container(border=True):
            t_col1, t_col2, t_col3 = st.columns([3, 1.5, 1])
            with t_col1:
                st.markdown(f"**[{topic['id']}] {topic['topic_name']}**")
                st.caption(f"{topic['core_summary']}")
            with t_col2:
                st.markdown(f"[🎥 Theory Lecture]({topic['yt_theory_url']}) | [🧮 PYQ Video]({topic['yt_pyq_url']})")
            with t_col3:
                status_txt = "✅ Cleared" if is_done else "⏳ Pending"
                st.markdown(f"**{status_txt}**")
