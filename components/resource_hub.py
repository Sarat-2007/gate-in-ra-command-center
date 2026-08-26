"""
Multi-Tier GATE Exam Resource Hub with Embedded Video Playback
"""
import streamlit as st
from database.db import get_all_topics, update_topic_completion
from config import DOMAINS


def render_resource_hub() -> None:
    st.subheader("🎓 100% GATE Exam Resource Hub & Lecture Player")
    st.caption("Access verified GATE theory lectures, step-by-step PYQ solution videos, and formulas for all 108 micro-topics.")

    all_topics = get_all_topics()

    # Filters
    col_domain, col_week, col_search = st.columns([1.5, 1, 1.5])
    with col_domain:
        selected_domain = st.selectbox("Filter by Domain:", options=["All Domains"] + DOMAINS)
    with col_week:
        week_options = ["All Weeks"] + [f"Week {w}" for w in range(1, 24)]
        selected_week = st.selectbox("Filter by Week:", options=week_options)
    with col_search:
        search_query = st.text_input("Search Topics / Formulas:", placeholder="e.g. Strain Gauge, Nyquist, Mohr...").strip().lower()

    # Filter logic
    filtered_topics = all_topics
    if selected_domain != "All Domains":
        filtered_topics = [t for t in filtered_topics if t["domain"] == selected_domain]
    if selected_week != "All Weeks":
        w_num = int(selected_week.split()[1])
        filtered_topics = [t for t in filtered_topics if t["week_number"] == w_num]
    if search_query:
        filtered_topics = [
            t for t in filtered_topics
            if (search_query in t["topic_name"].lower() or
                search_query in t["module_name"].lower() or
                search_query in t["id"].lower() or
                search_query in t.get("core_summary", "").lower())
        ]

    st.write(f"Showing **{len(filtered_topics)}** of {len(all_topics)} micro-topics.")

    if not filtered_topics:
        st.warning("No micro-topics matched your search filters.")
        return

    # Select active topic to display full details & player
    topic_labels = [f"[{t['id']}] (W{t['week_number']}) {t['topic_name']}" for t in filtered_topics]
    selected_topic_idx = st.selectbox("Select Active Topic to Study:", options=range(len(filtered_topics)), format_func=lambda i: topic_labels[i])

    active_topic = filtered_topics[selected_topic_idx]

    st.markdown("---")

    # Topic Header Card
    header_col1, header_col2, header_col3 = st.columns([3, 1, 1])
    with header_col1:
        st.markdown(f"### 📖 [{active_topic['id']}] {active_topic['topic_name']}")
        st.caption(f"**Domain:** {active_topic['domain']} | **Module:** {active_topic['module_name']} | **Week {active_topic['week_number']}**")
    with header_col2:
        st.markdown(f"**GATE Weightage:** ~{active_topic['weightage_approx_marks']} Marks")
        priority_color = "red" if active_topic['priority'] == 'Core' else "blue"
        st.markdown(f"**Priority:** :{priority_color}[{active_topic['priority']}]")
    with header_col3:
        is_comp = active_topic['is_completed'] == 1
        toggle_comp = st.checkbox("✅ Mark Completed", value=is_comp, key=f"comp_{active_topic['id']}")
        if toggle_comp != is_comp:
            update_topic_completion(active_topic['id'], toggle_comp)
            st.rerun()

    # Core Summary & Key Formula Banner
    st.info(f"**Core Concepts & Exam Focus:** {active_topic.get('core_summary', '')}")

    if active_topic.get("key_formula_latex"):
        st.markdown("#### 📐 Key Governing Formula:")
        st.latex(active_topic["key_formula_latex"])

    st.markdown("---")

    # Multi-Tier Video & Practice Links
    tab_theory, tab_pyq, tab_overflow = st.tabs([
        "🏛️ Tier 1: GATE Theory Lecture",
        "🧮 Tier 2: Step-by-Step PYQ Video",
        "🎯 Tier 3: GATE Overflow Interactive PYQs"
    ])

    with tab_theory:
        st.markdown(f"#### 🎥 {active_topic.get('yt_theory_title', 'GATE Theory Lecture')}")
        theory_url = active_topic.get("yt_theory_url", "")
        if theory_url:
            st.video(theory_url)
            st.markdown(f"[🔗 Open Video Lecture on YouTube in New Tab]({theory_url})")
        else:
            st.info("No video URL provided.")

    with tab_pyq:
        st.markdown(f"#### 🎥 {active_topic.get('yt_pyq_title', 'GATE PYQ Solving Video')}")
        pyq_url = active_topic.get("yt_pyq_url", "")
        if pyq_url:
            st.video(pyq_url)
            st.markdown(f"[🔗 Open PYQ Walkthrough on YouTube in New Tab]({pyq_url})")
        else:
            st.info("No PYQ video URL provided.")

    with tab_overflow:
        st.markdown("#### 🎯 Interactive Previous Year Questions (GATE Overflow)")
        st.write("Solve categorized 1-mark and 2-mark GATE questions from actual past papers with community-verified solutions and discussion threads.")
        overflow_url = active_topic.get("pyq_practice_url", "https://gateoverflow.in/")
        st.link_button("🚀 Open GATE Overflow Question Bank for this Subject", overflow_url, type="primary")
