import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.seed_data import SYLLABUS_SEED_DATA

for i, t in enumerate(SYLLABUS_SEED_DATA):
    print(f"--- Topic {t['id']}: {t['topic_name']} ({t['domain']}) ---")
    print(f"  Summary: {t['core_summary']}")
    print(f"  Formula: {t['key_formula_latex']}")
    print(f"  Theory URL: {t['yt_theory_url']}")
    print(f"  PYQ URL: {t['yt_pyq_url']}")
    print(f"  Overflow URL: {t['pyq_practice_url']}")
