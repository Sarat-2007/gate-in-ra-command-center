"""
Attendance & Check-In Form with AI Action Plan Generation
"""
import streamlit as st
from datetime import date
from database.db import (
    log_daily_checkin,
    get_all_topics,
    get_checkin_by_date,
    add_error_quarantine
)
from engine.ai_planner import generate_next_day_action_plan
from config import ERROR_TAXONOMY, DAILY_STUDY_CAP_HOURS


def render_attendance_form() -> None:
    st.subheader("📋 Daily Check-In & Action Plan Engine")
    st.caption("Capture your study window, log topic clearances, classify mistakes, and generate tomorrow's schedule.")

    all_topics = get_all_topics()
    uncompleted_topics = [t for t in all_topics if not t["is_completed"]]
    
    col_date, col_time = st.columns([1, 2])
    with col_date:
        checkin_date = st.date_input("Check-In Date", value=date.today())
        checkin_date_str = checkin_date.strftime("%Y-%m-%d")

    # Check if there is existing check-in data for this date
    existing_checkin = get_checkin_by_date(checkin_date_str)
    default_hours = existing_checkin["hours_logged"] if existing_checkin else 1.5
    default_roadblocks = existing_checkin["roadblocks_text"] if existing_checkin else ""
    default_errors = existing_checkin["error_codes"] if existing_checkin else []

    with col_time:
        hours_logged = st.slider(
            "Daily Study Time Logged (Hours)",
            min_value=0.25,
            max_value=float(DAILY_STUDY_CAP_HOURS),
            value=float(default_hours),
            step=0.25,
            help="GATE prep operates on focused, high-intensity daily windows (up to 2.0 hours)."
        )

    st.markdown("---")

    # Syllabus Topic Clearance Multi-Select
    st.markdown("#### 🎯 Syllabus Topics Cleared Today")
    topic_options = {f"[{t['id']}] {t['topic_name']} ({t['domain']})": t["id"] for t in all_topics}
    
    default_selected = []
    if existing_checkin and existing_checkin.get("completed_topics"):
        for label, tid in topic_options.items():
            if tid in existing_checkin["completed_topics"]:
                default_selected.append(label)

    selected_topic_labels = st.multiselect(
        "Select Topics Completed during this study window:",
        options=list(topic_options.keys()),
        default=default_selected,
        placeholder="Search and select micro-topics..."
    )
    completed_topic_ids = [topic_options[lbl] for lbl in selected_topic_labels]

    st.markdown("---")

    # Standardized Error Logging
    st.markdown("#### ⚠️ Diagnostic Error Logging (C, F, A, I, T, S Taxonomy)")
    st.caption("Classify any practice mistakes made during today's solving session to target tomorrow's recall drill.")

    error_cols = st.columns(6)
    selected_error_codes = []

    for idx, (code, meta) in enumerate(ERROR_TAXONOMY.items()):
        with error_cols[idx]:
            is_checked = st.checkbox(
                f"{meta['icon']} **[{code}]** {meta['name']}",
                value=(code in default_errors),
                help=meta["description"]
            )
            if is_checked:
                selected_error_codes.append(code)

    # Roadblocks and Free-text notes
    st.markdown("---")
    roadblocks = st.text_area(
        "📝 Roadblocks, Problem Friction, or Key Takeaways:",
        value=default_roadblocks,
        placeholder="e.g. Struggled with Nyquist contour enclosing -1+j0 or got confused in sign convention for Mohr's circle...",
        height=90
    )

    # Optional Quarantining of Specific Wrong Problem
    with st.expander("➕ Quarantine a Specific Mistake to 'Redo Mistakes Queue'", expanded=False):
        q_topic = st.selectbox("Related Topic for Mistake:", options=[t["topic_name"] for t in all_topics])
        q_code = st.selectbox("Mistake Code:", options=list(ERROR_TAXONOMY.keys()), format_func=lambda c: f"[{c}] {ERROR_TAXONOMY[c]['name']}")
        q_details = st.text_input("Question Summary / Year / Marks:", placeholder="e.g. GATE 2021 IN 2-Mark Question on Piezoelectric charge amplifier")
        q_wrong = st.text_input("What went wrong?:", placeholder="e.g. Substituted dynamic frequency in static formula, forgot low-frequency cutoff")
        q_correct = st.text_input("Correct Approach / Formula to remember:", placeholder="e.g. Vo = -(d * F) / Cf, cutoff frequency w_L = 1 / (Rf * Cf)")
        if st.button("Add to Error Quarantine Queue"):
            if q_details:
                matched_topic = next((t for t in all_topics if t["topic_name"] == q_topic), None)
                tid = matched_topic["id"] if matched_topic else "GEN_01"
                add_error_quarantine(
                    date_logged=checkin_date_str,
                    topic_id=tid,
                    topic_name=q_topic,
                    error_code=q_code,
                    question_details=q_details,
                    wrong_attempt_notes=q_wrong,
                    correct_takeaway=q_correct
                )
                st.success(f"Quarantined mistake for '{q_topic}' added to queue!")
            else:
                st.warning("Please provide question details.")

    # Action Buttons
    st.markdown("---")
    btn_col1, btn_col2 = st.columns([1, 2])

    with btn_col1:
        if st.button("💾 Save Check-In Record", type="primary", use_container_width=True):
            log_daily_checkin(
                checkin_date=checkin_date_str,
                hours_logged=hours_logged,
                completed_topics=completed_topic_ids,
                error_codes=selected_error_codes,
                roadblocks_text=roadblocks
            )
            st.success(f"Check-in for {checkin_date_str} successfully saved! ({hours_logged}h logged)")

    with btn_col2:
        generate_btn = st.button("🤖 Generate Tomorrow's Action Plan (Recall + Theory + PYQs)", use_container_width=True)

    # If plan exists or is generated
    plan_to_display = None
    if generate_btn:
        with st.spinner("Generating tailored GATE action plan with state injection..."):
            api_key = st.session_state.get("gemini_api_key", None)
            generated_plan = generate_next_day_action_plan(
                study_window_hours=hours_logged,
                recent_errors=selected_error_codes,
                roadblocks=roadblocks,
                api_key_override=api_key
            )
            # Save generated plan to database
            log_daily_checkin(
                checkin_date=checkin_date_str,
                hours_logged=hours_logged,
                completed_topics=completed_topic_ids,
                error_codes=selected_error_codes,
                roadblocks_text=roadblocks,
                ai_generated_plan=generated_plan
            )
            plan_to_display = generated_plan
    elif existing_checkin and existing_checkin.get("ai_generated_plan"):
        plan_to_display = existing_checkin["ai_generated_plan"]

    if plan_to_display:
        st.markdown("---")
        st.markdown("### 📋 Tomorrow's Tailored Action Plan")
        st.markdown(plan_to_display)
