import sys, re
sys.stdout.reconfigure(encoding='utf-8')
import pathlib

root = pathlib.Path('C:/Users/clint/azazael')

paths = {
    'SI': root / 'SYSTEM_INSTRUCTIONS.md',
    'SOP': root / 'SOP.md',
    'MANDATES': root / 'MANDATES.md',
}

# Old greedy regex: [^\n]*RULE\s+([0-9][A-Z]?...)
# Would backtrack to LAST RULE on line instead of first

print("=" * 80)
print("CHECKING HEADERS WITH MULTIPLE RULE REFERENCES")
print("=" * 80)

all_multi_rule_headers = []

for doc_name, path in paths.items():
    content = path.read_text('utf-8')
    lines = content.splitlines()
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith('#'):
            continue
        
        # Count RULE occurrences in this line
        rule_count = len(re.findall(r'RULE\s+', stripped))
        
        if rule_count >= 2:
            # Found a header with multiple RULE references!
            # Determine what the greedy regex would match vs non-greedy
            
            # Greedy: [^\n]* would match to LAST RULE on line
            greedy_match = re.search(
                r'^(#{2,3})\s+[^\n]*RULE\s+([0-9][A-Z]?(?:-[A-Z0-9])?)\s*:\s*(.*?)$',
                stripped, re.MULTILINE
            )
            
            # Non-greedy: .*? would match to FIRST RULE on line
            nongreedy_match = re.search(
                r'^(#{2,3})\s+.*?RULE\s+([0-9][A-Z]?(?:-[A-Z0-9])?)\s*:\s*(.*?)$',
                stripped, re.MULTILINE
            )
            
            greedy_num = greedy_match.group(2) if greedy_match else 'NO MATCH'
            nongreedy_num = nongreedy_match.group(2) if nongreedy_match else 'NO MATCH'
            
            # Find all RULE+number patterns on the line
            all_rules = re.findall(r'RULE\s+([0-9][A-Z]?(?:-[A-Z0-9])?)', stripped)
            
            all_multi_rule_headers.append({
                'doc': doc_name,
                'line': i + 1,
                'text': stripped[:160],
                'rule_count': rule_count,
                'all_rules': all_rules,
                'greedy_matches': greedy_num,
                'nongreedy_matches': nongreedy_num,
                'affected': greedy_num != nongreedy_num
            })

if not all_multi_rule_headers:
    print("\n  ✅ No headers with multiple RULE references found — greedy regex was not an issue")
else:
    print(f"\n  Found {len(all_multi_rule_headers)} header(s) with multiple RULE references:\n")
    for h in all_multi_rule_headers:
        icon = '🔴 AFFECTED' if h['affected'] else '✅ NOT AFFECTED'
        print(f"  {icon} — {h['doc']} L{h['line']}")
        print(f"       Line: {h['text']}")
        print(f"       RULEs found: {', '.join(h['all_rules'])}")
        print(f"       Greedy matches: {h['greedy_matches']}")
        print(f"       Non-greedy matches: {h['nongreedy_matches']}")
        print(f"       {'Greedy bug would match WRONG RULE!' if h['affected'] else 'Both match the same RULE — no issue'}")
        print()

# Now also check specifically for RULE 0J and 0Z headers in all 3 docs
print()
print("=" * 80)
print("SPECIFIC CHECK: RULE 0J and RULE 0Z headers in all 3 docs")
print("=" * 80)

for doc_name, path in paths.items():
    content = path.read_text('utf-8')
    lines = content.splitlines()
    
    for target in ['0J', '0Z']:
        matches = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('#') and f'RULE {target}' in stripped:
                # Extract the full title (what regex captures after the colon)
                title_match = re.search(r':\s*(.*?)$', stripped)
                title = title_match.group(1)[:100] if title_match else '(no colon)'
                matches.append((i+1, stripped[:160], title))
        
        print(f"\n  RULE {target} in {doc_name}:")
        if matches:
            for ln, text, title in matches:
                print(f"    L{ln}: {text}")
                # Check if title has embedded RULE references
                if re.search(r'RULE\s+', title):
                    print(f"          ⚠️  Title CONTAINS embedded RULE reference: \"{title}\"")
                else:
                    print(f"          ✅ Clean title, no embedded RULE refs")
        else:
            print(f"    ❌ No ##/### header found")
