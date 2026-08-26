# 🎯 GATE IN & RA Master Preparation Command Center (23-Week Cycle)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An all-in-one, distraction-free preparation command center built specifically for **GATE Instrumentation Engineering (IN)** and **GATE Robotics & Automation (RA)** candidates navigating the rigorous **23-Week Preparation Cycle** aligned with official IIT Madras examination standards.

---

## 🚀 Key Features & Architectural Modules

1. **🌅 5-Minute Morning Recap & Memory Refresh**:
   - Visual cards reviewing yesterday's cleared topics, governing formulas, and diagnostic error takeaways.
   - Interactive 3-question active recall memory check with a 5-minute timer.
2. **📺 100% In-App Study Studio (Zero Tab Switching)**:
   - **Split Screen**: Embedded YouTube Video Player (`st.video`) with Theory and PYQ lectures side-by-side with high-yield notes.
   - **Interactive GATE PYQ Solver**: Real GATE 1-mark & 2-mark questions with MCQ/NAT instant answer verification and step-by-step mathematical solutions on screen.
   - **1-Click Error Quarantine**: Instantly tag and save any missed problems into your Redo Mistakes Queue (`[C]`, `[F]`, `[A]`, `[I]`, `[T]`, `[S]`).
3. **🖩 Integrated TCS iON Virtual Scientific Calculator**:
   - Authentic on-screen calculator simulator (Deg/Rad toggle, trigonometry, natural logarithms, memory keys, powers) and working scratchpad.
4. **🧠 Spaced Repetition Formula Vault (SuperMemo-2)**:
   - Formula flashcards with memory decay scheduling and 1-click Markdown cheat-sheet export.
5. **🎯 Weekend General Aptitude Tracker**:
   - Strict 2-hour weekend study block quota enforcement for compulsory 15-mark General Aptitude.
6. **🤖 Gemini AI Action Planner**:
   - Live SQLite state injection generating tailored daily schedules (Recall + Theory + PYQ Sprints) with deterministic offline heuristic fallback.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit, Plotly
- **Database**: SQLite3 (automatically seeded on first launch)
- **AI Engine**: Google Gemini API (with offline rule engine fallback)
- **Language**: Python 3.12+

---

## 💻 Local Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/gate-in-ra-command-center.git
   cd gate-in-ra-command-center
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

4. Open `http://localhost:8501` in your browser.

---

## ☁️ 1-Click Free Cloud Deployment (Streamlit Community Cloud)

You can deploy this application for free to run 24/7 in the cloud:

1. Create a new public or private repository on **[GitHub](https://github.com/new)** (e.g., `gate-in-ra-command-center`).
2. Push your local code to GitHub:
   ```bash
   git remote add origin https://github.com/<your-username>/gate-in-ra-command-center.git
   git branch -M main
   git push -u origin main
   ```
3. Visit **[share.streamlit.io](https://share.streamlit.io/)** and click **"New app"**.
4. Select your repository, set the branch to `main`, and main file path to `app.py`.
5. Click **"Deploy!"** Your GATE Command Center will be live on the web!

---

## 📝 Diagnostic Error Taxonomy

- **`[C]` Conceptual Gap**: Misunderstood fundamental physical/mathematical principle.
- **`[F]` Formula Recall Decay**: Forgot or misremembered a standard formula or constant.
- **`[A]` Strategy Deficit**: Chose an inappropriate solving approach or sub-optimal method.
- **`[I]` Reading / Boundary Slip**: Misread problem constraints, units, or question wording.
- **`[T]` Time Pressure Panic**: Spent excessive time (>4 min) or rushed under timer.
- **`[S]` Virtual Calc / Arithmetic Error**: Keypad typo or sign inversion.
