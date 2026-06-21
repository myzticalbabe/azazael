import sys, re
sys.stdout.reconfigure(encoding="utf-8")
import pathlib

paths = {
    "SI": pathlib.Path("C:/Users/clint/azazael/SYSTEM_INSTRUCTIONS.md"),
    "SOP": pathlib.Path("C:/Users/clint/azazael/SOP.md"),
    "MANDATES": pathlib.Path("C:/Users/clint/azazael/MANDATES.md"),
}
doc_labels = ["SI", "SOP", "MANDATES"]

docs = {}
for name, path in paths.items():
    docs[name] = path.read_text("utf-8")

# Extract RULE headers
all_rules = {}
for doc_name, content in docs.items():
    matches = re.findall(
        r'^(#{2,3})\s+.*?RULE\s+([0-9][A-Z]?(?:-[A-Z0-9])?)\s*:\s*(.*?)$',
        content, re.MULTILINE
    )
    for level, num, title in matches:
        if num not in all_rules:
            all_rules[num] = {}
        all_rules[num][doc_name] = {
            "level": len(level),
            "title": title.strip()[:150]
        }

# Show only mismatches
all_nums = sorted(all_rules.keys(), key=lambda x: (
    int(re.sub(r"[^0-9]", "", x) or 0), x
))

mismatches = 0
for num in all_nums:
    if len(all_rules[num]) < 2:
        continue
    titles = {d: all_rules[num][d]["title"] for d in all_rules[num]}
    norm = {}
    for d, t in titles.items():
        nt = re.sub(r"\s+", " ", t.lower().strip().rstrip(".,"))
        norm[d] = nt
    if len(set(norm.values())) > 1:
        mismatches += 1
        print(f"\n--- RULE {num} ---")
        for d in doc_labels:
            if d in titles:
                level = "#" * all_rules[num][d]["level"]
                print(f"  {d} ({level}): \"{titles[d]}\"")
        # Show what matches
        print(f"  Canonical (SI): \"{titles.get('SI', 'N/A')}\"")

print(f"\n{'='*60}")
print(f"Total title mismatches: {mismatches}")
print(f"Docs to align: SOP, MANDATES -> SI (canonical)")
