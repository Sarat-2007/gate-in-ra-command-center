import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.seed_data import SYLLABUS_SEED_DATA

print(f"Total topics: {len(SYLLABUS_SEED_DATA)}")

for idx, t in enumerate(SYLLABUS_SEED_DATA):
    print("=" * 70)
    print(f"[{idx+1}/{len(SYLLABUS_SEED_DATA)}] Topic ID: {t['id']} | Week: {t['week_number']}")
    print(f"Domain: {t['domain']}")
    print(f"Module: {t['module_name']}")
    print(f"Topic: {t['topic_name']}")
    print(f"Priority: {t.get('priority')} | Weightage: {t.get('weightage_approx_marks')}")
    print(f"Formula: {t.get('key_formula_latex')}")
    print(f"Summary: {t.get('core_summary')}")
    print(f"PYQ Type: {t.get('pyq_type')}")
    print(f"Question: {t.get('pyq_question')}")
    print(f"Options: {t.get('pyq_options')}")
    print(f"Answer Key: {t.get('pyq_correct_answer')}")
    print(f"Explanation: {t.get('pyq_explanation')}")
    print(f"Theory YT: {t.get('yt_theory_title')} | {t.get('yt_theory_url')}")
    print(f"PYQ YT: {t.get('yt_pyq_title')} | {t.get('yt_pyq_url')}")
    print(f"Practice: {t.get('pyq_practice_url')}")
