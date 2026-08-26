import sys
import json
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.seed_data import SYLLABUS_SEED_DATA

print(f"=== RIGOROUS AUDIT OF {len(SYLLABUS_SEED_DATA)} SEED TOPICS ===")

errors = []
warnings = []

mcq_count = 0
nat_count = 0
topics_by_week = {}
topics_by_domain = {}

for idx, t in enumerate(SYLLABUS_SEED_DATA):
    tid = t.get("id")
    name = t.get("topic_name")
    week = t.get("week_number")
    domain = t.get("domain")
    formula = t.get("key_formula_latex", "")
    summary = t.get("core_summary", "")
    q_type = t.get("pyq_type", "MCQ")
    question = t.get("pyq_question", "")
    options = t.get("pyq_options", [])
    correct = t.get("pyq_correct_answer", "")
    explanation = t.get("pyq_explanation", "")
    yt_t_url = t.get("yt_theory_url", "")
    yt_p_url = t.get("yt_pyq_url", "")
    overflow_url = t.get("pyq_practice_url", "")

    topics_by_week.setdefault(week, []).append(tid)
    topics_by_domain.setdefault(domain, []).append(tid)

    # 1. Check ID and Week
    if not tid:
        errors.append(f"Topic index {idx} has no ID!")
    if not week or week < 1 or week > 23:
        errors.append(f"Topic {tid}: Invalid week {week}")

    # 2. Check LaTeX brackets
    open_curly = formula.count("{")
    close_curly = formula.count("}")
    if open_curly != close_curly:
        errors.append(f"Topic {tid}: Unbalanced curly braces in key_formula_latex ({open_curly} vs {close_curly}): {formula}")

    # 3. Check MCQ vs NAT
    if q_type == "MCQ":
        mcq_count += 1
        if not options or len(options) < 2:
            errors.append(f"Topic {tid}: MCQ has invalid options: {options}")
        elif correct not in options:
            errors.append(f"Topic {tid}: Correct answer '{correct}' NOT in options {options}")
    elif q_type == "NAT":
        nat_count += 1
        if options and len(options) > 0:
            warnings.append(f"Topic {tid}: NAT has non-empty options: {options}")
        if not correct:
            errors.append(f"Topic {tid}: NAT has no correct answer!")
    else:
        errors.append(f"Topic {tid}: Unknown pyq_type '{q_type}'")

    # 4. Check Explanation & Question length
    if not question or len(question.strip()) < 10:
        errors.append(f"Topic {tid}: Question is empty or too short!")
    if not explanation or len(explanation.strip()) < 10:
        errors.append(f"Topic {tid}: Explanation is empty or too short!")

    # 5. Check YouTube URL structure
    if not yt_t_url.startswith("https://www.youtube.com/watch?v=") and not yt_t_url.startswith("https://youtu.be/"):
        warnings.append(f"Topic {tid}: Non-standard yt_theory_url: {yt_t_url}")
    if not yt_p_url.startswith("https://www.youtube.com/watch?v=") and not yt_p_url.startswith("https://youtu.be/"):
        warnings.append(f"Topic {tid}: Non-standard yt_pyq_url: {yt_p_url}")

print(f"Total Topics: {len(SYLLABUS_SEED_DATA)}")
print(f"MCQ Count: {mcq_count}, NAT Count: {nat_count}")
print(f"Weeks distribution (1-23):")
for w in sorted(topics_by_week.keys()):
    print(f"  Week {w:02d}: {len(topics_by_week[w])} topics -> {topics_by_week[w]}")

print(f"\nDomains distribution:")
for d, t_list in topics_by_domain.items():
    print(f"  {d}: {len(t_list)} topics")

print(f"\nErrors found: {len(errors)}")
for e in errors:
    print(f"  [ERROR] {e}")

print(f"\nWarnings found: {len(warnings)}")
for w in warnings:
    print(f"  [WARNING] {w}")
