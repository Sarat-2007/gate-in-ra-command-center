"""
TCS iON GATE Virtual Scientific Calculator & Scratchpad Component
"""
import streamlit as st
import math


def render_virtual_calc() -> None:
    st.subheader("🖩 TCS iON GATE Virtual Calculator & Scratchpad")
    st.caption("Practice on the official GATE on-screen calculator layout to completely eliminate calculation slips ([S] errors).")

    if "calc_display" not in st.session_state:
        st.session_state.calc_display = "0"
    if "calc_rad_mode" not in st.session_state:
        st.session_state.calc_rad_mode = True
    if "calc_memory" not in st.session_state:
        st.session_state.calc_memory = 0.0

    calc_col, scratch_col = st.columns([1.2, 1])

    with calc_col:
        # Mode indicator & Display
        mode_str = "RAD" if st.session_state.calc_rad_mode else "DEG"
        st.markdown(f"""
        <div style="background-color: #1E293B; color: #38BDF8; font-family: monospace; font-size: 24px; text-align: right; padding: 12px; border-radius: 8px; border: 2px solid #334155; margin-bottom: 10px;">
            <span style="float: left; font-size: 14px; color: #94A3B8;">[{mode_str}] M:{st.session_state.calc_memory}</span>
            {st.session_state.calc_display}
        </div>
        """, unsafe_allow_html=True)

        # Radian/Degree toggle & Memory functions
        row0_1, row0_2, row0_3, row0_4, row0_5 = st.columns(5)
        with row0_1:
            if st.button("Deg/Rad", use_container_width=True):
                st.session_state.calc_rad_mode = not st.session_state.calc_rad_mode
                st.rerun()
        with row0_2:
            if st.button("MC", use_container_width=True):
                st.session_state.calc_memory = 0.0
                st.rerun()
        with row0_3:
            if st.button("MR", use_container_width=True):
                st.session_state.calc_display = str(st.session_state.calc_memory)
                st.rerun()
        with row0_4:
            if st.button("M+", use_container_width=True):
                try:
                    st.session_state.calc_memory += float(st.session_state.calc_display)
                except Exception:
                    pass
                st.rerun()
        with row0_5:
            if st.button("M-", use_container_width=True):
                try:
                    st.session_state.calc_memory -= float(st.session_state.calc_display)
                except Exception:
                    pass
                st.rerun()

        # Scientific Functions Row 1
        r1_1, r1_2, r1_3, r1_4, r1_5 = st.columns(5)
        with r1_1:
            if st.button("ln", use_container_width=True):
                apply_single_op(math.log)
        with r1_2:
            if st.button("log10", use_container_width=True):
                apply_single_op(math.log10)
        with r1_3:
            if st.button("sqrt", use_container_width=True):
                apply_single_op(math.sqrt)
        with r1_4:
            if st.button("1/x", use_container_width=True):
                apply_single_op(lambda x: 1.0 / x if x != 0 else "Error")
        with r1_5:
            if st.button("C", use_container_width=True):
                st.session_state.calc_display = "0"
                st.rerun()

        # Scientific Functions Row 2 (Trigonometry)
        r2_1, r2_2, r2_3, r2_4, r2_5 = st.columns(5)
        with r2_1:
            if st.button("sin", use_container_width=True):
                apply_trig_op(math.sin)
        with r2_2:
            if st.button("cos", use_container_width=True):
                apply_trig_op(math.cos)
        with r2_3:
            if st.button("tan", use_container_width=True):
                apply_trig_op(math.tan)
        with r2_4:
            if st.button("e^x", use_container_width=True):
                apply_single_op(math.exp)
        with r2_5:
            if st.button("DEL", use_container_width=True):
                if len(st.session_state.calc_display) > 1:
                    st.session_state.calc_display = st.session_state.calc_display[:-1]
                else:
                    st.session_state.calc_display = "0"
                st.rerun()

        # Numeric Keypad Row 1
        n1_1, n1_2, n1_3, n1_4, n1_5 = st.columns(5)
        with n1_1:
            if st.button("7", use_container_width=True): append_digit("7")
        with n1_2:
            if st.button("8", use_container_width=True): append_digit("8")
        with n1_3:
            if st.button("9", use_container_width=True): append_digit("9")
        with n1_4:
            if st.button("/", use_container_width=True): append_operator("/")
        with n1_5:
            if st.button("pi", use_container_width=True):
                st.session_state.calc_display = str(math.pi)
                st.rerun()

        # Numeric Keypad Row 2
        n2_1, n2_2, n2_3, n2_4, n2_5 = st.columns(5)
        with n2_1:
            if st.button("4", use_container_width=True): append_digit("4")
        with n2_2:
            if st.button("5", use_container_width=True): append_digit("5")
        with n2_3:
            if st.button("6", use_container_width=True): append_digit("6")
        with n2_4:
            if st.button("*", use_container_width=True): append_operator("*")
        with n2_5:
            if st.button("e", use_container_width=True):
                st.session_state.calc_display = str(math.e)
                st.rerun()

        # Numeric Keypad Row 3
        n3_1, n3_2, n3_3, n3_4, n3_5 = st.columns(5)
        with n3_1:
            if st.button("1", use_container_width=True): append_digit("1")
        with n3_2:
            if st.button("2", use_container_width=True): append_digit("2")
        with n3_3:
            if st.button("3", use_container_width=True): append_digit("3")
        with n3_4:
            if st.button("-", use_container_width=True): append_operator("-")
        with n3_5:
            if st.button("^", use_container_width=True): append_operator("**")

        # Numeric Keypad Row 4
        n4_1, n4_2, n4_3, n4_4, n4_5 = st.columns(5)
        with n4_1:
            if st.button("0", use_container_width=True): append_digit("0")
        with n4_2:
            if st.button(".", use_container_width=True): append_digit(".")
        with n4_3:
            if st.button("+/-", use_container_width=True):
                if st.session_state.calc_display.startswith("-"):
                    st.session_state.calc_display = st.session_state.calc_display[1:]
                else:
                    st.session_state.calc_display = "-" + st.session_state.calc_display
                st.rerun()
        with n4_4:
            if st.button("+", use_container_width=True): append_operator("+")
        with n4_5:
            if st.button("=", type="primary", use_container_width=True): evaluate_expression()

    with scratch_col:
        st.markdown("#### 📝 Virtual Scratchpad & Precision Rules")
        st.caption("GATE Virtual Calculator Guidelines & Traps:")
        st.markdown("""
        1. **Trig Angle Mode**: Always verify whether the calculation requires **RAD** (e.g. vibrations $\\omega t$, calculus) or **DEG** (e.g. phasor angles, polar impedance).
        2. **NAT Truncation**: Enter answers up to **2 to 3 decimal places** exactly as specified in the question prompt.
        3. **Order of Operations**: The on-screen calculator evaluates sequentially; use parentheses when evaluating complex transfer functions.
        """)
        scratch_notes = st.text_area("Scratch Working Notes / Step Calculations:", placeholder="Write calculation steps here...", height=240)


def append_digit(digit: str):
    if st.session_state.calc_display in ["0", "Error"]:
        st.session_state.calc_display = digit
    else:
        st.session_state.calc_display += digit
    st.rerun()


def append_operator(op: str):
    if st.session_state.calc_display != "Error":
        st.session_state.calc_display += f" {op} "
    st.rerun()


def apply_single_op(func):
    try:
        val = float(eval_safe(st.session_state.calc_display))
        res = func(val)
        st.session_state.calc_display = str(round(res, 8) if isinstance(res, float) else res)
    except Exception:
        st.session_state.calc_display = "Error"
    st.rerun()


def apply_trig_op(func):
    try:
        val = float(eval_safe(st.session_state.calc_display))
        if not st.session_state.calc_rad_mode:
            val = math.radians(val)
        res = func(val)
        st.session_state.calc_display = str(round(res, 8))
    except Exception:
        st.session_state.calc_display = "Error"
    st.rerun()


def eval_safe(expr: str):
    allowed_names = {"math": math}
    clean_expr = expr.replace("^", "**")
    return eval(clean_expr, {"__builtins__": None}, allowed_names)


def evaluate_expression():
    try:
        res = eval_safe(st.session_state.calc_display)
        if isinstance(res, float):
            st.session_state.calc_display = str(round(res, 8))
        else:
            st.session_state.calc_display = str(res)
    except Exception:
        st.session_state.calc_display = "Error"
    st.rerun()
