import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.seed_data import SYLLABUS_SEED_DATA

for t in SYLLABUS_SEED_DATA:
    print(f"[{t['id']}] W{t['week_number']:02d} | {t['domain']:<30} | {t['module_name']:<25} | {t['topic_name']}")
