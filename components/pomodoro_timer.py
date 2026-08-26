"""
Synchronized 3-Phase GATE Pomodoro Study Timer (Recall + Theory + PYQs)
"""
import streamlit as st
import time


def render_pomodoro_timer() -> None:
    st.subheader("⏱️ Synchronized 3-Phase GATE Study Sprint Timer")
    st.caption("Execute your daily study window with structured intervals: Recall (20%) -> Theory Deep Dive (50%) -> PYQs (30%).")

    if "timer_running" not in st.session_state:
        st.session_state.timer_running = False
    if "timer_seconds_left" not in st.session_state:
        st.session_state.timer_seconds_left = 90 * 60
    if "selected_window_mins" not in st.session_state:
        st.session_state.selected_window_mins = 90
    if "active_phase" not in st.session_state:
        st.session_state.active_phase = "Recall Session"

    # Time Window Selection
    col_preset, col_custom = st.columns([2, 1])
    with col_preset:
        preset = st.radio(
            "Select Daily Study Window:",
            options=[45, 60, 90, 120],
            format_func=lambda m: f"{m} Minutes ({round(m/60, 2)} hrs)",
            horizontal=True,
            index=2
        )
        if preset != st.session_state.selected_window_mins and not st.session_state.timer_running:
            st.session_state.selected_window_mins = preset
            st.session_state.timer_seconds_left = preset * 60

    total_mins = st.session_state.selected_window_mins
    recall_mins = max(10, int(total_mins * 0.20))
    theory_mins = max(20, int(total_mins * 0.50))
    pyq_mins = total_mins - recall_mins - theory_mins

    # Phase Breakdown Visualizer
    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        st.info(f"**Phase 1: 🔁 Recall Session**\n\n`{recall_mins} Mins` (Active formula retrieval & [F]/[C] error fixes)")
    with p_col2:
        st.info(f"**Phase 2: 📖 Theory Deep Dive**\n\n`{theory_mins} Mins` (Derivations, theorems & boundary cases)")
    with p_col3:
        st.info(f"**Phase 3: 🎯 PYQ Sprint**\n\n`{pyq_mins} Mins` (1-Mark & 2-Mark questions under timer)")

    st.markdown("---")

    # Timer Display Box
    mins = st.session_state.timer_seconds_left // 60
    secs = st.session_state.timer_seconds_left % 60
    timer_formatted = f"{mins:02d}:{secs:02d}"

    elapsed_mins = total_mins - mins
    if elapsed_mins <= recall_mins:
        curr_phase = "🔁 Phase 1: Recall Session"
        phase_color = "#3B82F6"
    elif elapsed_mins <= (recall_mins + theory_mins):
        curr_phase = "📖 Phase 2: Theory Deep Dive"
        phase_color = "#F59E0B"
    else:
        curr_phase = "🎯 Phase 3: Targeted PYQ Sprint"
        phase_color = "#10B981"

    st.markdown(f"""
    <div style="background-color: #0F172A; text-align: center; padding: 25px; border-radius: 12px; border: 2px solid {phase_color}; margin-bottom: 20px;">
        <h4 style="color: {phase_color}; margin-bottom: 5px;">{curr_phase}</h4>
        <h1 style="color: #F8FAFC; font-family: monospace; font-size: 64px; margin: 0;">{timer_formatted}</h1>
    </div>
    """, unsafe_allow_html=True)

    # Timer Controls
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if not st.session_state.timer_running:
            if st.button("▶️ Start Study Sprint", type="primary", use_container_width=True):
                st.session_state.timer_running = True
                st.rerun()
        else:
            if st.button("⏸️ Pause Sprint", use_container_width=True):
                st.session_state.timer_running = False
                st.rerun()

    with btn_col2:
        if st.button("🔄 Reset Timer", use_container_width=True):
            st.session_state.timer_running = False
            st.session_state.timer_seconds_left = st.session_state.selected_window_mins * 60
            st.rerun()

    with btn_col3:
        if st.button("🏁 Log Completed Session", use_container_width=True):
            st.session_state.timer_running = False
            st.success(f"Session of {round(st.session_state.selected_window_mins/60, 2)} hours marked complete! Head over to the Daily Check-In tab to log cleared topics.")
