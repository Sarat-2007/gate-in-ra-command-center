import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.seed_data import SYLLABUS_SEED_DATA

output_lines = []
for idx, t in enumerate(SYLLABUS_SEED_DATA):
    output_lines.append(f"--- [TOPIC {idx+1}/{len(SYLLABUS_SEED_DATA)}] ID: {t['id']} | Week: {t['week_number']} | Domain: {t['domain']} ---")
    output_lines.append(f"Topic: {t['topic_name']} (Module: {t['module_name']})")
    output_lines.append(f"Formula: {t['key_formula_latex']}")
    output_lines.append(f"Summary: {t['core_summary']}")
    output_lines.append(f"Type: {t.get('pyq_type')} | Options: {t.get('pyq_options')}")
    output_lines.append(f"Question: {t.get('pyq_question')}")
    output_lines.append(f"Correct Answer: {t.get('pyq_correct_answer')}")
    output_lines.append(f"Explanation: {t.get('pyq_explanation')}")
    output_lines.append(f"Theory YT: {t.get('yt_theory_title')} | {t.get('yt_theory_url')}")
    output_lines.append(f"PYQ YT: {t.get('yt_pyq_title')} | {t.get('yt_pyq_url')}")
    output_lines.append("")

out_file = Path(__file__).resolve().parent / "full_syllabus_dump.txt"
with open(out_file, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"Dumped {len(SYLLABUS_SEED_DATA)} topics to {out_file}")
