import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.seed_data import SYLLABUS_SEED_DATA
from collections import Counter

theory_urls = Counter(t["yt_theory_url"] for t in SYLLABUS_SEED_DATA)
pyq_urls = Counter(t["yt_pyq_url"] for t in SYLLABUS_SEED_DATA)
overflow_urls = Counter(t["pyq_practice_url"] for t in SYLLABUS_SEED_DATA)

print(f"Unique Theory URLs: {len(theory_urls)}")
print(f"Unique PYQ URLs: {len(pyq_urls)}")
print(f"Unique Overflow URLs: {len(overflow_urls)}")

print("\nOverflow URLs Breakdown:")
for u, c in overflow_urls.items():
    print(f"  {u}: {c} topics")
