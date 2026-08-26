"""
Unified In-App Study Studio Component
Integrates embedded YouTube video playback, high-yield notes, interactive GATE PYQ solver,
and side-by-side TCS iON Virtual Calculator into a single zero-distraction screen.
"""
import streamlit as st
import math
from database.db import get_all_topics, update_topic_completion, add_error_quarantine
from components.virtual_calc import render_virtual_calc
from config import DOMAINS, ERROR_TAXONOMY


def render_inapp_studio() -> None:
    st.subheader("🎯 In-App GATE Study Studio (Zero Tab-Switching)")
    st.caption("Learn theory, watch lectures, solve embedded GATE PYQs, and use the on-screen calculator in one screen.")

    all_topics = get_all_topics()
    
    # Topic Select Bar
    filter_col1, filter_col2 = st.columns([1.5, 2.5])
    with filter_col1:
        domain_choice = st.selectbox("Select Domain Focus:", options=["All IN & RA Domains"] + DOMAINS)
    with filter_col2:
        if domain_choice != "All IN & RA Domains":
            filtered_topics = [t for t in all_topics if t["domain"] == domain_choice]
        else:
            filtered_topics = all_topics
        
        topic_labels = [f"[{t['id']}] (W{t['week_number']}) {t['topic_name']}" for t in filtered_topics]
        selected_idx = st.selectbox(
            "Choose Active Topic:",
            options=range(len(filtered_topics)),
            format_func=lambda i: topic_labels[i]
        )

    topic = filtered_topics[selected_idx]

    # Topic Status Ribbon
    r_col1, r_col2, r_col3 = st.columns([3, 1, 1])
    with r_col1:
        st.markdown(f"### 📖 [{topic['id']}] {topic['topic_name']}")
        st.caption(f"**Domain:** {topic['domain']} | **Module:** {topic['module_name']} | **Week {topic['week_number']}**")
    with r_col2:
        st.markdown(f"**Weightage:** ~{topic['weightage_approx_marks']} Marks")
    with r_col3:
        is_done = topic["is_completed"] == 1
        toggle_done = st.checkbox("✅ Mark Topic Mastered", value=is_done, key=f"studio_comp_{topic['id']}")
        if toggle_done != is_done:
            update_topic_completion(topic["id"], toggle_done)
            st.rerun()

    st.markdown("---")

    # Split Screen Studio: Left (Video + Notes) vs Right (Interactive PYQ + Calc)
    studio_left, studio_right = st.columns([1.2, 1.1])

    with studio_left:
        st.markdown("#### 📺 Embedded Video Lecture Player")
        video_mode = st.radio("Select Video Stream:", ["🏛️ Tier 1: GATE Theory Lecture", "🧮 Tier 2: Step-by-Step PYQ Solution"], horizontal=True)
        
        if "Theory" in video_mode:
            v_url = topic.get("yt_theory_url", "")
            v_title = topic.get("yt_theory_title", "Theory Lecture")
        else:
            v_url = topic.get("yt_pyq_url", "")
            v_title = topic.get("yt_pyq_title", "PYQ Video Walkthrough")

        st.caption(f"**Playing:** {v_title}")
        if v_url:
            st.video(v_url)
        else:
            st.info("No video URL assigned.")

        # High-Yield Core Theory & Formula Box
        st.markdown("#### 📐 High-Yield Concept & Formula Box")
        if topic.get("key_formula_latex"):
            st.latex(topic["key_formula_latex"])
        st.info(f"**Core Exam Takeaways:** {topic.get('core_summary', '')}")

    with studio_right:
        # Tabbed Interactive Solver & Virtual Calc
        right_tab_pyq, right_tab_calc = st.tabs(["🧮 Interactive GATE PYQ", "🖩 TCS iON Calculator"])

        with right_tab_pyq:
            st.markdown(f"#### 🎯 [{topic['id']}] Official GATE Problem")
            pyq_text = topic.get("pyq_question", "No question text available.")
            st.markdown(f"**Question:**\n\n{pyq_text}")

            q_type = topic.get("pyq_type", "MCQ")
            correct_ans = topic.get("pyq_correct_answer", "").strip()
            explanation = topic.get("pyq_explanation", "")

            user_answer = None
            if q_type == "MCQ":
                opts = topic.get("pyq_options", [])
                if opts:
                    user_answer = st.radio("Select your option:", options=opts, key=f"pyq_mcq_{topic['id']}")
            else:
                user_answer = st.text_input("Enter Numerical Answer (NAT):", placeholder="e.g. 12.5", key=f"pyq_nat_{topic['id']}").strip()

            submit_col, quarantine_col = st.columns([1, 1.2])
            
            with submit_col:
                check_btn = st.button("🚀 Check Answer", type="primary", key=f"btn_check_{topic['id']}", use_container_width=True)

            with quarantine_col:
                quarantine_btn = st.button("⚠️ Quarantine Mistake", key=f"btn_quar_{topic['id']}", use_container_width=True)

            if check_btn:
                if q_type == "MCQ":
                    if user_answer and user_answer == correct_ans:
                        st.success(f"🎉 **Correct Answer!** ({correct_ans})")
                    else:
                        st.error(f"❌ **Incorrect.** Correct answer is: **{correct_ans}**")
                else:
                    try:
                        u_val = float(user_answer)
                        c_val = float(correct_ans)
                        if abs(u_val - c_val) <= 0.05 * abs(c_val) or abs(u_val - c_val) <= 0.1:
                            st.success(f"🎉 **Correct Answer!** (Value: {correct_ans})")
                        else:
                            st.error(f"❌ **Incorrect.** Correct numerical answer is: **{correct_ans}**")
                    except Exception:
                        if user_answer == correct_ans:
                            st.success(f"🎉 **Correct Answer!** ({correct_ans})")
                        else:
                            st.error(f"❌ Correct answer is: **{correct_ans}**")

                with st.expander("📖 View Step-by-Step Mathematical Derivation", expanded=True):
                    st.markdown(f"**Step-by-Step Solution:**\n\n{explanation}")

            if quarantine_btn:
                add_error_quarantine(
                    date_logged=st.session_state.get("checkin_date_str", "2026-08-26"),
                    topic_id=topic["id"],
                    topic_name=topic["topic_name"],
                    error_code="C",
                    question_details=pyq_text,
                    wrong_attempt_notes=f"Solved incorrectly in In-App Studio. Selected: {user_answer}",
                    correct_takeaway=explanation
                )
                st.warning(f"⚠️ Problem for '{topic['topic_name']}' added to your Redo Mistakes Queue!")

        with right_tab_calc:
            render_virtual_calc()
