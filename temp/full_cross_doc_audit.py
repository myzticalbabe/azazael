import sys, re
sys.stdout.reconfigure(encoding='utf-8')

paths = {
    'SI': r'C:/Users/clint/azazael/SYSTEM_INSTRUCTIONS.md',
    'SOP': r'C:/Users/clint/azazael/SOP.md',
    'MANDATES': r'C:/Users/clint/azazael/MANDATES.md',
}
doc_labels = ['SI', 'SOP', 'MANDATES']

docs = {}
for name, path in paths.items():
    with open(path, 'r', encoding='utf-8') as f:
        docs[name] = f.read()

# Extract RULE headers with full title text and header level
all_rules = {}
for doc_name, content in docs.items():
    # Match ## or ### headers containing "RULE <num>"
    matches = re.findall(
        r'^(#{2,3})\s+.*?RULE\s+([0-9][A-Z]?(?:-[A-Z0-9])?)\s*:\s*(.*?)$',
        content, re.MULTILINE
    )
    for level, num, title in matches:
        if num not in all_rules:
            all_rules[num] = {}
        all_rules[num][doc_name] = {
            'level': '##' if len(level) == 2 else '###',
            'title': title.strip()[:100]
        }

all_nums = sorted(all_rules.keys(), key=lambda x: (
    int(re.sub(r'[^0-9]', '', x) or 0),
    x
))

print('=' * 80)
print('COMPREHENSIVE CROSS-DOC RULE AUDIT')
print(f'{len(all_nums)} unique RULE numbers across 3 canonical docs')
print(f'Scanned: SYSTEM_INSTRUCTIONS.md (SI), SOP.md (SOP), MANDATES.md (MANDATES)')
print('=' * 80)

print()
print('--- SECTION 1: RULE DEFINITION PRESENCE ---')
print()

presence_issues = []
title_issues = []
level_issues = []
ok_count = 0

for num in all_nums:
    present_in = [d for d in doc_labels if d in all_rules[num]]
    missing_in = [d for d in doc_labels if d not in all_rules[num]]
    
    if missing_in:
        presence_issues.append((num, missing_in))
        print(f'  🔴 RULE {num}: PRESENT in {", ".join(present_in)}, MISSING in {", ".join(missing_in)}')
    else:
        ok_count += 1

if presence_issues:
    print(f'\n  🔴 {len(presence_issues)} RULE(s) missing from at least one doc')
else:
    print(f'  ✅ All {ok_count} RULEs present in all 3 docs')

print()
print('--- SECTION 2: HEADER LEVEL CONSISTENCY ---')
print()

for num in all_nums:
    if len(all_rules[num]) < 2:
        continue
    levels = {d: all_rules[num][d]['level'] for d in all_rules[num]}
    unique_levels = set(levels.values())
    if len(unique_levels) > 1:
        level_issues.append((num, levels))
        print(f'  ⚠️  RULE {num}: {levels}')

if not level_issues:
    print('  ✅ All RULEs use consistent header levels across docs')
print(f'  ({len(level_issues)} mismatches found)')

print()
print('--- SECTION 3: TITLE PHRASING INCONSISTENCIES ---')
print()

for num in all_nums:
    if len(all_rules[num]) < 2:
        continue
    titles = {d: all_rules[num][d]['title'] for d in all_rules[num]}
    # Normalize: lowercase, collapse whitespace, remove trailing punctuation
    norm = {}
    for d, t in titles.items():
        nt = re.sub(r'\s+', ' ', t.lower().strip().rstrip('.').rstrip(','))
        norm[d] = nt
    unique_norm = set(norm.values())
    if len(unique_norm) > 1:
        title_issues.append((num, titles))
        print(f'  🟡 RULE {num}:')
        for d in doc_labels:
            if d in titles:
                print(f'       {d}: "{titles[d]}"')

if not title_issues:
    print('  ✅ All RULEs use identical title phrasing across docs')
print(f'  ({len(title_issues)} mismatches found)')

print()
print('--- SECTION 4: SUMMARY TABLE ---')
print()

# Build a presence matrix
header = f"{'RULE':<10} {'SI':<8} {'SOP':<8} {'MANDATES':<10} {'Level?':<8} {'Title?'}"
print(header)
print('-' * len(header))
for num in all_nums:
    si = '✅' if 'SI' in all_rules[num] else '❌'
    sop = '✅' if 'SOP' in all_rules[num] else '❌'
    mand = '✅' if 'MANDATES' in all_rules[num] else '❌'
    
    # Level consistency
    levels_present = {d: all_rules[num][d]['level'] for d in all_rules[num] if d in all_rules[num]}
    level_str = 'OK' if len(set(levels_present.values())) <= 1 else '⚠️'
    
    # Title consistency (only if present in 2+ docs)
    if len(levels_present) >= 2:
        titles_p = {d: re.sub(r'\s+', ' ', all_rules[num][d]['title'].lower().strip().rstrip('.').rstrip(','))
                     for d in all_rules[num]}
        title_str = 'OK' if len(set(titles_p.values())) <= 1 else '🟡'
    else:
        title_str = 'N/A'
    
    print(f"{num:<10} {si:<8} {sop:<8} {mand:<10} {level_str:<8} {title_str}")

print()
print('--- FINAL SCORE ---')
print(f'  Total unique RULEs:   {len(all_nums)}')
print(f'  Presence issues:      {len(presence_issues)}')
print(f'  Level mismatches:     {len(level_issues)}')
print(f'  Title mismatches:     {len(title_issues)}')
print()

if not presence_issues and not level_issues and not title_issues:
    print('  ✅ PERFECT CONSISTENCY — All RULEs match across all 3 docs')
else:
    print('  Issues to address:')
    if presence_issues:
        print(f'    🔴 Presence: Fix missing RULE headers')
    if level_issues:
        print(f'    ⚠️  Levels:  Normalize header levels')
    if title_issues:
        print(f'    🟡 Titles:  Align phrasing across docs')
