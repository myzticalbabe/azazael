import sys, re
sys.stdout.reconfigure(encoding="utf-8")
import pathlib

paths = {
    "SI": pathlib.Path("C:/Users/clint/azazael/SYSTEM_INSTRUCTIONS.md"),
    "SOP": pathlib.Path("C:/Users/clint/azazael/SOP.md"),
    "MANDATES": pathlib.Path("C:/Users/clint/azazael/MANDATES.md"),
}

# Read canonical SI headers
si_content = paths["SI"].read_text("utf-8")
si_headers = {}
for m in re.finditer(
    r'^(#{2,3}\s+.*?RULE\s+([0-9][A-Z]?(?:-[A-Z0-9])?)\s*:\s*(.*?))$',
    si_content, re.MULTILINE
):
    num = m.group(2)
    si_headers[num] = {"full": m.group(1), "title": m.group(3).strip()[:150]}

def normalize_doc(doc_name, content, si_headers):
    """Replace headers in doc to match SI canonical titles."""
    lines = content.split("\n")
    changes = 0
    
    for i, line in enumerate(lines):
        # Only process header lines
        m = re.match(
            r'^(#{2,3}\s+.*?RULE\s+([0-9][A-Z]?(?:-[A-Z0-9])?)\s*:\s*)(.*?)$',
            line
        )
        if not m:
            continue
        
        num = m.group(2)
        header_prefix = m.group(1)  # e.g. "## RULE 0A: " or "### 🔴 RULE 0A: "
        current_title = m.group(3).strip()
        
        if num not in si_headers:
            continue
        
        si_title = si_headers[num]["title"]
        # Normalize for comparison
        si_norm = re.sub(r"\s+", " ", si_title.lower().strip().rstrip(".,"))
        cur_norm = re.sub(r"\s+", " ", current_title.lower().strip().rstrip(".,"))
        
        if si_norm == cur_norm:
            continue  # Already matches
        
        # Replace just the title portion after the colon
        old_line = line
        new_line = header_prefix + si_title
        lines[i] = new_line
        changes += 1
        print(f"  [{doc_name}] RULE {num}: UPDATED")
    
    return "\n".join(lines), changes

total_changes = 0

for doc_name in ["SOP", "MANDATES"]:
    path = paths[doc_name]
    content = path.read_text("utf-8")
    updated, changes = normalize_doc(doc_name, content, si_headers)
    if changes > 0:
        path.write_text(updated, "utf-8")
    total_changes += changes
    print(f"  {doc_name}: {changes} headers updated")

print(f"\nTotal: {total_changes} header title changes across SOP and MANDATES")
