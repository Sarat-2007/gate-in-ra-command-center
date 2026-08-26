"""
5-Minute Morning Recap & Flash Recall Carousel Component
Provides a zero-friction, distraction-free morning memory refresh before today's study.
"""
import streamlit as st
from datetime import date, timedelta
from database.db import get_all_checkins, get_all_topics, get_formula_vault, log_daily_checkin
from config import ERROR_TAXONOMY


def render_morning_recap() -> None:
    st.subheader("🌅 5-Minute Morning Recap & Memory Refresh")
    st.caption("Review yesterday's cleared topics, refresh high-yield formulas, and execute a 3-question active recall check before today's session.")

    checkins = get_all_checkins()
    all_topics = get_all_topics()
    topic_map = {t["id"]: t for t in all_topics}

    # Find the most recent checkin
    today_str = date.today().strftime("%Y-%m-%d")
    yesterday_str = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    recent_checkin = None
    
    for c in reversed(checkins):
        if c["date"] != today_str:
            recent_checkin = c
            break

    # Top Status & 5-Minute Timer
    top_col1, top_col2 = st.columns([2.5, 1])
    with top_col1:
        if recent_checkin:
            st.markdown(f"#### 📅 Last Session: **{recent_checkin['date']}** ({recent_checkin['hours_logged']} hrs logged)")
        else:
            st.markdown("#### 🌟 Welcome to Day 1 of your 23-Week GATE IN & RA Journey!")
    with top_col2:
        if "recap_timer_sec" not in st.session_state:
            st.session_state.recap_timer_sec = 5 * 60
        r_mins = st.session_state.recap_timer_sec // 60
        r_secs = st.session_state.recap_timer_sec % 60
        st.markdown(f"""
        <div style="background-color: #1E293B; color: #38BDF8; font-family: monospace; font-size: 18px; text-align: center; padding: 6px; border-radius: 6px; border: 1px solid #334155;">
            ⏱️ Morning Timer: {r_mins:02d}:{r_secs:02d}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Card 1: Yesterday's Topics & Formulas
    card1, card2 = st.columns([1.2, 1])

    with card1:
        st.markdown("### 📚 Topics Cleared in Previous Session")
        if recent_checkin and recent_checkin.get("completed_topics"):
            cleared_ids = recent_checkin["completed_topics"]
            for tid in cleared_ids:
                t = topic_map.get(tid)
                if t:
                    with st.container(border=True):
                        st.markdown(f"**[{t['id']}] {t['topic_name']}**")
                        st.caption(f"Domain: {t['domain']} | Module: {t['module_name']}")
                        if t.get("key_formula_latex"):
                            st.latex(t["key_formula_latex"])
        else:
            st.info("No completed topics from yesterday. Starting fresh! Check off today's topics in the Study Studio as you master them.")

    with card2:
        st.markdown("### ⚠️ Diagnostic Mistakes Logged")
        if recent_checkin and recent_checkin.get("error_codes"):
            err_codes = recent_checkin["error_codes"]
            st.write(f"Logged **{len(err_codes)}** diagnostic errors to watch out for today:")
            for code in err_codes:
                meta = ERROR_TAXONOMY.get(code, {"name": "Error", "icon": "⚠️", "description": ""})
                with st.container(border=True):
                    st.markdown(f"**{meta['icon']} [{code}] {meta['name']}**")
                    st.caption(meta["description"])
            if recent_checkin.get("roadblocks_text"):
                st.warning(f"**Reported Roadblock:** {recent_checkin['roadblocks_text']}")
        else:
            st.success("✅ Clean slate! No practice errors logged in the previous session. Maintain high precision today.")

    st.markdown("---")

    # Interactive Flash Memory Quiz (3 Questions)
    st.markdown("### 🧠 3-Question Active Recall Flash Check")
    st.caption("Test your recall of key governing GATE formulas before diving into new topics.")

    q1_col, q2_col, q3_col = st.columns(3)
    
    with q1_col:
        with st.container(border=True):
            st.markdown("**Q1: Strain Gauge Bridge**")
            st.write("What is the output voltage $V_o$ for a full Wheatstone push-pull bridge?")
            q1_ans = st.radio("Select formula:", ["Vo = Vs * GF * ε", "Vo = (Vs/4) * GF * ε", "Vo = (Vs/2) * GF * ε"], key="recap_q1")
            if st.button("Check Q1", key="btn_q1"):
                if q1_ans == "Vo = Vs * GF * ε":
                    st.success("🎯 Correct! Full bridge gives 4x output of quarter bridge.")
                else:
                    st.error("❌ Remember: Full push-pull bridge output is $V_o = V_s \\cdot GF \\cdot \\epsilon$.")

    with q2_col:
        with st.container(border=True):
            st.markdown("**Q2: D-H Parameter Twist**")
            st.write("Link twist angle $\\alpha_i$ is measured around which axis?")
            q2_ans = st.radio("Select axis:", ["Around x_i axis", "Around z_{i-1} axis", "Around y_i axis"], key="recap_q2")
            if st.button("Check Q2", key="btn_q2"):
                if q2_ans == "Around x_i axis":
                    st.success("🎯 Correct! $\\alpha_i$ is the angle from $z_{i-1}$ to $z_i$ about $x_i$.")
                else:
                    st.error("❌ Remember: $\\alpha_i$ is measured around the common normal $x_i$.")

    with q3_col:
        with st.container(border=True):
            st.markdown("**Q3: 2nd Order Damping**")
            st.write("For an underdamped system ($0 < \\zeta < 1$), peak overshoot $M_p$ depends on:")
            q3_ans = st.radio("Select factor:", ["Only on damping ratio ζ", "Both ζ and natural freq ωn", "Only on steady state gain K"], key="recap_q3")
            if st.button("Check Q3", key="btn_q3"):
                if q3_ans == "Only on damping ratio ζ":
                    st.success("🎯 Correct! $M_p = e^{-\\frac{\\pi\\zeta}{\\sqrt{1-\\zeta^2}}}$ is independent of $\\omega_n$.")
                else:
                    st.error("❌ Remember: $M_p$ depends strictly on the damping ratio $\\zeta$.")

    st.markdown("---")

    # Primary Transition Call to Action
    st.info("💡 **Ready to begin today's study?** Head over to the **🎯 In-App Study Studio** tab to watch your lecture, solve embedded GATE PYQs, and use the on-screen calculator in one unified view.")
