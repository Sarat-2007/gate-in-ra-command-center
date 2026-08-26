"""
Error Quarantine & Redo Mistakes Queue Component
"""
import streamlit as st
from datetime import date
from database.db import get_quarantined_errors, update_error_mastery, add_error_quarantine, get_all_topics
from config import ERROR_TAXONOMY


def render_error_quarantine() -> None:
    st.subheader("🔄 Redo Mistakes Quarantine Queue")
    st.caption("Quarantine every problem you solve incorrectly. Re-attempt and master each question before exam day.")

    all_topics = get_all_topics()
    active_tab, mastered_tab, add_tab = st.tabs([
        "⚠️ Active Quarantined Mistakes",
        "✅ Mastered & Resolved Problems",
        "➕ Quarantine New Mistake"
    ])

    with active_tab:
        active_errors = get_quarantined_errors(only_active=True)
        if not active_errors:
            st.success("🎉 No active quarantined errors! Your mistake queue is clean.")
        else:
            q_col_txt, q_col_dl = st.columns([2, 1])
            with q_col_txt:
                st.write(f"**{len(active_errors)}** problems currently quarantined:")
            with q_col_dl:
                error_md = "# 🔄 GATE Quarantined Mistakes Log & Root-Cause Diary\n\n"
                for err in active_errors:
                    error_md += f"## [{err['error_code']}] {err['topic_name']} (Logged: {err['date_logged']})\n"
                    error_md += f"**Problem:** {err['question_details']}\n\n"
                    error_md += f"**❌ Mistake:** {err['wrong_attempt_notes']}\n\n"
                    error_md += f"**💡 Correct Method & Concept:** {err['correct_takeaway']}\n\n---\n\n"

                st.download_button(
                    label="📥 Export Mistake Diary (.md)",
                    data=error_md,
                    file_name="gate_mistake_diary.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            for err in active_errors:
                code_meta = ERROR_TAXONOMY.get(err["error_code"], {"name": "Error", "icon": "⚠️", "color": "#EF4444"})
                with st.container(border=True):
                    head1, head2 = st.columns([3, 1])
                    with head1:
                        st.markdown(f"#### {code_meta['icon']} [{err['error_code']}] {err['topic_name']}")
                        st.caption(f"Logged on: {err['date_logged']} | Total Attempts: {err['attempts_count']}")
                    with head2:
                        if st.button("✅ Mark Mastered", key=f"mast_{err['id']}", type="primary", use_container_width=True):
                            update_error_mastery(err["id"], is_mastered=True)
                            st.success(f"Problem on '{err['topic_name']}' marked as Mastered!")
                            st.rerun()

                    st.markdown(f"**Question / Context:** {err['question_details']}")
                    
                    col_wrong, col_correct = st.columns(2)
                    with col_wrong:
                        st.error(f"**❌ Original Mistake:**\n\n{err['wrong_attempt_notes']}")
                    with col_correct:
                        st.success(f"**💡 Key Takeaway & Correct Method:**\n\n{err['correct_takeaway']}")

    with mastered_tab:
        mastered_errors = [e for e in get_quarantined_errors(only_active=False) if e["is_mastered"] == 1]
        if not mastered_errors:
            st.info("No mastered problems yet. Re-attempt active mistakes and mark them resolved.")
        else:
            st.write(f"**{len(mastered_errors)}** problems successfully mastered:")
            for err in mastered_errors:
                with st.container(border=True):
                    st.markdown(f"#### ✅ [{err['error_code']}] {err['topic_name']} *(Resolved on {err['mastered_date']})*")
                    st.markdown(f"**Question:** {err['question_details']}")
                    st.info(f"**Takeaway:** {err['correct_takeaway']}")

    with add_tab:
        st.markdown("#### Quarantine a Practice Mistake for Re-solving")
        with st.form("manual_error_form"):
            topic_choice = st.selectbox("Topic:", options=[t["topic_name"] for t in all_topics])
            err_code_choice = st.selectbox("Error Code:", options=list(ERROR_TAXONOMY.keys()), format_func=lambda c: f"[{c}] {ERROR_TAXONOMY[c]['name']}")
            q_desc = st.text_area("Question Description / Year / Source:", placeholder="e.g. GATE IN 2020 Question 42 on Nyquist encirclement count")
            q_mistake = st.text_input("What was your incorrect step / wrong thought?:", placeholder="e.g. Counted encirclement of origin instead of -1+j0")
            q_fix = st.text_input("What is the correct concept / formula to remember?:", placeholder="e.g. Encirclements N must be calculated strictly about -1+j0 point")
            
            submit_err = st.form_submit_button("Quarantine This Problem", type="primary")
            if submit_err:
                if q_desc:
                    matched_topic = next((t for t in all_topics if t["topic_name"] == topic_choice), None)
                    tid = matched_topic["id"] if matched_topic else "GEN"
                    today_str = date.today().strftime("%Y-%m-%d")
                    add_error_quarantine(
                        date_logged=st.session_state.get("checkin_date_str", today_str),
                        topic_id=tid,
                        topic_name=topic_choice,
                        error_code=err_code_choice,
                        question_details=q_desc,
                        wrong_attempt_notes=q_mistake,
                        correct_takeaway=q_fix
                    )
                    st.success(f"Problem for '{topic_choice}' added to quarantine queue!")
                    st.rerun()
                else:
                    st.warning("Please provide question description.")
