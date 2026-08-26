import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
from database.seed_data import SYLLABUS_SEED_DATA
from config import DOMAINS, ERROR_TAXONOMY, TOTAL_WEEKS

def audit_seed_data():
    print(f"Total topics: {len(SYLLABUS_SEED_DATA)}")
    weeks = {}
    domains = {}
    ids = set()
    dup_ids = []
    latex_errors = []
    
    for idx, t in enumerate(SYLLABUS_SEED_DATA):
        tid = t.get("id")
        if tid in ids:
            dup_ids.append(tid)
        ids.add(tid)
        
        w = t.get("week_number")
        weeks[w] = weeks.get(w, 0) + 1
        
        d = t.get("domain")
        domains[d] = domains.get(d, 0) + 1
        
        latex = t.get("key_formula_latex", "")
        if latex.count("{") != latex.count("}"):
            latex_errors.append((tid, "Mismatched curly braces in LaTeX", latex))
        if latex.count("$") % 2 != 0:
            latex_errors.append((tid, "Mismatched $ in LaTeX", latex))
            
    print("\n--- WEEK DISTRIBUTION ---")
    for w in sorted(weeks.keys()):
        print(f"Week {w:2d}: {weeks[w]} topics")
        
    print("\n--- DOMAIN DISTRIBUTION ---")
    for d, count in domains.items():
        print(f"{d}: {count} topics (In config.DOMAINS: {d in DOMAINS})")
        
    print(f"\nDuplicate IDs: {dup_ids}")
    print(f"LaTeX syntax issues: {len(latex_errors)}")
    for err in latex_errors:
        print(" ", err)

if __name__ == "__main__":
    audit_seed_data()
