"""
Gemini AI Action Plan Engine with Full State Injection & Smart Offline Fallback
Enforces strict 3-part schedule output: Recall Session, Theory Deep Dive, Targeted PYQs.
"""
import os
import json
from datetime import datetime, date
from typing import Dict, Any, Optional
from database.db import get_all_topics, get_all_checkins, get_setting
from engine.analytics import calculate_dashboard_metrics, get_error_distribution


def generate_next_day_action_plan(
    study_window_hours: float,
    recent_errors: list,
    roadblocks: str = "",
    api_key_override: Optional[str] = None
) -> str:
    """
    Generates tomorrow's tailored study schedule using Gemini API with full SQLite state injection.
    Falls back to intelligent heuristic rule engine if offline or API key is not provided.
    """
    # 1. Gather live database state
    metrics = calculate_dashboard_metrics()
    all_topics = get_all_topics()
    uncompleted_topics = [t for t in all_topics if not t["is_completed"]]
    target_paper = get_setting("target_paper", "IN (Instrumentation Engineering)")

    next_topics = uncompleted_topics[:3] if uncompleted_topics else []
    primary_topic = next_topics[0] if next_topics else {
        "id": "REV_01",
        "topic_name": "Full Syllabus Mock Test & High-Weightage Revision",
        "domain": "Revision",
        "key_formula_latex": r"\text{Full Formula Recall}",
        "core_summary": "Comprehensive revision across all GATE domains."
    }

    # Calculate allocated time splits based on study window (ensuring positive minutes for all segments)
    effective_window = max(0.25, study_window_hours) if study_window_hours > 0 else 1.5
    total_minutes = int(effective_window * 60)
    if total_minutes <= 45:
        recall_mins = max(5, int(total_minutes * 0.20))
        theory_mins = max(5, int(total_minutes * 0.50))
        pyq_mins = max(5, total_minutes - recall_mins - theory_mins)
    else:
        recall_mins = max(15, int(total_minutes * 0.20))
        theory_mins = max(30, int(total_minutes * 0.50))
        pyq_mins = max(10, total_minutes - recall_mins - theory_mins)

    # Extract recent error codes description
    error_summary_list = []
    for code in recent_errors:
        if code == "C":
            error_summary_list.append("[C] Conceptual Gaps (Misunderstood fundamental principles)")
        elif code == "F":
            error_summary_list.append("[F] Formula Decay (Forgotten standard relations/constants)")
        elif code == "A":
            error_summary_list.append("[A] Strategy Selection (Sub-optimal solving approach)")
        elif code == "I":
            error_summary_list.append("[I] Interpretation Slip (Misread boundary conditions/units)")
        elif code == "T":
            error_summary_list.append("[T] Time Mismanagement (Clock pressure rushes)")
        elif code == "S":
            error_summary_list.append("[S] Calculation Slip (Virtual calculator or sign error)")

    recent_errors_text = ", ".join(error_summary_list) if error_summary_list else "No significant errors logged recently."

    # Check for Gemini API key
    api_key = api_key_override or os.environ.get("GEMINI_API_KEY")

    if api_key:
        try:
            prompt_content = f"""
You are the Chief IIT Madras GATE Exam Mentor for {target_paper}.
The candidate has an available daily study window of {study_window_hours} hours ({total_minutes} minutes).

### Live Candidate State:
- Target Paper: {target_paper}
- Current Pacing: Week {metrics['current_week']} of 23 ({metrics['pacing_status']})
- Overall Syllabus Progress: {metrics['overall_progress_pct']}% completed ({metrics['completed_count']} of {metrics['total_topics']} topics)
- Target Micro-Topic for Tomorrow: {primary_topic['topic_name']} ({primary_topic['domain']})
- Core Topic Formula / Concept: {primary_topic.get('key_formula_latex', '')}
- Topic Summary: {primary_topic.get('core_summary', '')}
- Recent Error Patterns to Remediate: {recent_errors_text}
- Candidate Friction / Roadblocks: {roadblocks if roadblocks else "None reported"}

### Required Action Plan Structure:
You MUST output tomorrow's study plan in EXACTLY 3 numbered sections:

### 🔁 Part 1: Recall Session (Active Recall & Formula Blitz) [Allocated: {recall_mins} Mins]
- Specifically remediate recent [F] and [C] mistakes.
- Provide 3 rapid conceptual flash-questions or key derivations to write from memory.

### 📖 Part 2: Theory Deep Dive (High-Yield Core Concepts) [Allocated: {theory_mins} Mins]
- Essential theoretical principles, boundary conditions, and mathematical models for "{primary_topic['topic_name']}".
- Highlight typical GATE traps (e.g. sign conventions, units, NAT precision).

### 🎯 Part 3: Targeted PYQ Problem Set (1-Mark & 2-Mark Sprints) [Allocated: {pyq_mins} Mins]
- 3 to 4 specific standard GATE question archetypes for this topic.
- Step-by-step solving strategy to prevent [A], [I], and [S] slips using the Virtual Calculator.
"""

            # Try google.genai first, then google.generativeai
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt_content
                )
                if response and response.text:
                    return response.text
            except Exception:
                import google.generativeai as genai_legacy
                genai_legacy.configure(api_key=api_key)
                model = genai_legacy.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt_content)
                if response and response.text:
                    return response.text
        except Exception as e:
            # If API call fails, seamlessly fall back to heuristic generator
            pass

    # =========================================================================
    # Heuristic Rule-Based Fallback Generator
    # =========================================================================
    return generate_heuristic_action_plan(
        primary_topic=primary_topic,
        study_window_hours=study_window_hours,
        recall_mins=recall_mins,
        theory_mins=theory_mins,
        pyq_mins=pyq_mins,
        recent_errors=recent_errors,
        roadblocks=roadblocks
    )


def generate_heuristic_action_plan(
    primary_topic: Dict[str, Any],
    study_window_hours: float,
    recall_mins: int,
    theory_mins: int,
    pyq_mins: int,
    recent_errors: list,
    roadblocks: str
) -> str:
    """Generates a high-quality deterministic action plan tailored to topic metadata."""
    topic_name = primary_topic.get("topic_name", "Core Engineering Topic")
    domain = primary_topic.get("domain", "Engineering Core")
    formula = primary_topic.get("key_formula_latex", "")
    summary = primary_topic.get("core_summary", "")

    # Tailored recall questions based on topic and errors
    recall_bullet_1 = f"Write down from memory the primary governing formula: ${formula}$ and explain each term's physical unit."
    if "F" in recent_errors or "C" in recent_errors:
        recall_bullet_2 = "Derive the boundary conditions or limiting cases where this formula fails or simplifies."
    else:
        recall_bullet_2 = "List the top 3 assumptions underlying this derivation (e.g. linearity, isotropic material, ideal source)."
    recall_bullet_3 = "Quick 5-minute active recall drill: explain the core principle out loud in simple terms without looking at notes."

    # Roadblock advice
    roadblock_section = ""
    if roadblocks:
        roadblock_section = f"\n> **Remediation Note for Reported Roadblock:** *'{roadblocks}'*\n> Dedicate the first 10 minutes of the theory block to dissecting this exact bottleneck with a textbook diagram or lecture snippet.\n"

    plan = f"""### 🔁 Part 1: Recall Session (Active Recall & Formula Blitz) [Allocated: {recall_mins} Mins]
- **Targeting Formula Recall & Conceptual Precision**
- [ ] {recall_bullet_1}
- [ ] {recall_bullet_2}
- [ ] {recall_bullet_3}

---

### 📖 Part 2: Theory Deep Dive (High-Yield Core Concepts) [Allocated: {theory_mins} Mins]
- **Active Focus Module:** `{topic_name}` *({domain})*
{roadblock_section}
- [ ] **Core Concept Mastery:** {summary}
- [ ] **Mathematical Modeling:** Review the derivation for:
  $$\\displaystyle {formula}$$
- [ ] **GATE Trap Checklist:**
  - Double check unit conversions before substituting (e.g. $\\text{{kN}} \\to \\text{{N}}$, $\\text{{mm}} \\to \\text{{m}}$, $\\text{{rad/s}} \\to \\text{{Hz}}$).
  - Note sign conventions (e.g. tension vs compression, clockwise vs counter-clockwise encirclement).
  - Verify whether problem asks for peak-to-peak, RMS, or maximum amplitude.

---

### 🎯 Part 3: Targeted PYQ Problem Set (1-Mark & 2-Mark Sprints) [Allocated: {pyq_mins} Mins]
- **Targeting Execution Accuracy & Virtual Calculator Fluency**
- [ ] **Problem 1 (1-Mark Concept Check):** Direct formula substitution question from GATE 2018–2022 to lock in basics.
- [ ] **Problem 2 (2-Mark Analytical / NAT):** Multi-step calculation testing parameter variations. Practice strictly using the on-screen calculator.
- [ ] **Problem 3 (2-Mark Tricky / MSQ):** Multiple-statement question testing theoretical edge cases and non-ideal behaviors.
- [ ] **Post-Solve Audit:** Categorize any wrong attempts immediately as `[C]`, `[F]`, `[A]`, `[I]`, `[T]`, or `[S]` in the Check-In form.
"""
    return plan
