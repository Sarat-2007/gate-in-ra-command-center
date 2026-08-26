import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.seed_data import SYLLABUS_SEED_DATA

for t in SYLLABUS_SEED_DATA[24:]:
    print(f"[{t['id']}] {t['topic_name']} ({t['domain']})")
    print(f"   Formula: {t['key_formula_latex']}")
    print(f"   Theory:  {t['yt_theory_title']} -> {t['yt_theory_url']}")
    print(f"   PYQ:     {t['yt_pyq_title']} -> {t['yt_pyq_url']}")
    print()
