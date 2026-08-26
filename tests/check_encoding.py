with open("database/seed_data.py", "rb") as f:
    raw = f.read()

import re

for line_no, line in enumerate(raw.split(b"\n"), 1):
    try:
        line.decode("utf-8")
    except UnicodeDecodeError as e:
        print(f"Decode error on line {line_no}: {e}")
        
# Check for common problematic replacement characters or non-standard characters
text = raw.decode("utf-8", errors="replace")
for line_no, line in enumerate(text.split("\n"), 1):
    if "\ufffd" in line:
        print(f"Replacement char (\\ufffd) on line {line_no}: {line}")
    if any(ord(c) > 127 and c not in "αβγδεζηθικλμνξοπρστυφχψωΩΔ∑∏√≈≤≥≠±°–—’“”•·" for c in line):
        non_std = [c for c in line if ord(c) > 127 and c not in "αβγδεζηθικλμνξοπρστυφχψωΩΔ∑∏√≈≤≥≠±°–—’“”•·"]
        print(f"Non-standard char on line {line_no}: {non_std} -> {line[:80]}...")
