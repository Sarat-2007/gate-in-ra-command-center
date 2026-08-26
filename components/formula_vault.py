"""
Spaced Repetition Formula Vault (Leitner / SuperMemo-2) Component
"""
import streamlit as st
from database.db import get_formula_vault, update_formula_review
from engine.spaced_repetition import get_formula_deck_statistics, process_formula_feedback


def render_formula_vault() -> None:
    st.subheader("🧠 Spaced Repetition Formula Vault")
    st.caption("Prevent formula decay ([F] errors) using spaced active recall intervals (1d, 3d, 7d, 14d, 30d).")

    stats = get_formula_deck_statistics()

    # Deck Statistics Metrics Bar
    s_col1, s_col2, s_col3, s_col4, s_col5 = st.columns(5)
    with s_col1:
        st.metric("Total Cards", stats["total_cards"])
    with s_col2:
        st.metric("Due Today", stats["due_today"], delta=f"{stats['due_today']} to review", delta_color="inverse")
    with s_col3:
        st.metric("Learning", stats["learning"])
    with s_col4:
        st.metric("Reviewing", stats["reviewing"])
    with s_col5:
        st.metric("Mastered", stats["mastered"], delta=f"{stats['mastery_rate']}%")

    # Export Cheat Sheet Button & View Filter
    c_btn1, c_btn2 = st.columns([2, 1])
    with c_btn1:
        view_mode = st.radio("View Mode:", options=["📅 Due for Review Today", "📚 Browse All Formula Cards"], horizontal=True)
    with c_btn2:
        all_deck = get_formula_vault(due_only=False)
        cheat_sheet_md = "# 📐 GATE High-Yield Formula Vault Cheat Sheet\n\n"
        for c in all_deck:
            cheat_sheet_md += f"### [{c['topic_id']}] {c['formula_title']} ({c['domain']})\n"
            cheat_sheet_md += f"$$\n{c['formula_latex']}\n$$\n"
            cheat_sheet_md += f"*Status: {c['mastery_status']} | Repetitions: {c['repetition_count']}*\n\n---\n\n"
        
        st.download_button(
            label="📥 Download Complete Formula Sheet (.md)",
            data=cheat_sheet_md,
            file_name="gate_formula_vault_cheatsheet.md",
            mime="text/markdown",
            use_container_width=True
        )

    due_only = (view_mode == "📅 Due for Review Today")

    cards = get_formula_vault(due_only=due_only)

    if not cards:
        if due_only:
            st.success("🎉 All due formula cards reviewed for today! Great job maintaining memory retention.")
        else:
            st.info("No formula cards found.")
        return

    st.write(f"Showing **{len(cards)}** formula flashcards:")

    for card in cards:
        status_color = "green" if card["mastery_status"] == "Mastered" else ("orange" if card["mastery_status"] == "Reviewing" else "blue")
        with st.container(border=True):
            c_head1, c_head2 = st.columns([3, 1])
            with c_head1:
                st.markdown(f"#### 🏷️ [{card['topic_id']}] {card['formula_title']}")
                st.caption(f"**Domain:** {card['domain']} | Repetitions: {card['repetition_count']} | Interval: {card['interval_days']} days | Next Review: {card['next_review_date']}")
            with c_head2:
                st.markdown(f":{status_color}[**Status: {card['mastery_status']}**]")

            reveal_key = f"reveal_{card['topic_id']}"
            if reveal_key not in st.session_state:
                st.session_state[reveal_key] = False

            if not st.session_state[reveal_key]:
                if st.button(f"👁️ Reveal Formula (${card['topic_id']}$)", key=f"btn_rev_{card['topic_id']}"):
                    st.session_state[reveal_key] = True
                    st.rerun()
            else:
                st.markdown("##### 📐 Formula & Model:")
                st.latex(card["formula_latex"])

                st.markdown("##### How easily did you recall this?")
                fb_col1, fb_col2, fb_col3 = st.columns(3)
                with fb_col1:
                    if st.button("🔴 Forgot / Hard", key=f"fb_0_{card['topic_id']}", use_container_width=True):
                        process_formula_feedback(card["topic_id"], "forgot")
                        st.session_state[reveal_key] = False
                        st.success(f"Reset interval for '{card['formula_title']}' to 1 day.")
                        st.rerun()
                with fb_col2:
                    if st.button("🟡 Hesitated / Medium", key=f"fb_1_{card['topic_id']}", use_container_width=True):
                        process_formula_feedback(card["topic_id"], "hesitated")
                        st.session_state[reveal_key] = False
                        st.info(f"Updated review interval for '{card['formula_title']}'.")
                        st.rerun()
                with fb_col3:
                    if st.button("🟢 Easy Recall", key=f"fb_2_{card['topic_id']}", use_container_width=True):
                        process_formula_feedback(card["topic_id"], "easy")
                        st.session_state[reveal_key] = False
                        st.success(f"Advanced mastery for '{card['formula_title']}'!")
                        st.rerun()
