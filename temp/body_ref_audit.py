import sys, re
sys.stdout.reconfigure(encoding='utf-8')

paths = {
    'SI': r'C:/Users/clint/azazael/SYSTEM_INSTRUCTIONS.md',
    'SOP': r'C:/Users/clint/azazael/SOP.md',
    'MANDATES': r'C:/Users/clint/azazael/MANDATES.md',
}

# First, extract all RULE headers so we know which exist in each doc
headers = {}
for doc_name, path in paths.items():
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    header_set = set()
    for m in re.finditer(r'^#{2,3}\s+[^\n]*RULE\s+([0-9][A-Z]?(?:-[A-Z0-9])?)', content, re.MULTILINE):
        header_set.add(m.group(1))
    headers[doc_name] = header_set

all_valid_rules = set()
for h in headers.values():
    all_valid_rules.update(h)
all_valid_rules = sorted(all_valid_rules, key=lambda x: (int(re.sub(r'[^0-9]', '', x) or 0), x))

print('=' * 80)
print('BODY TEXT RULE REFERENCE AUDIT')
print('=' * 80)

print(f'\nValid RULE headers per doc:')
for doc_name in ['SI', 'SOP', 'MANDATES']:
    print(f'  {doc_name}: {sorted(headers[doc_name])}')

print(f'\nComplete valid RULE set: {all_valid_rules}')

# Track all body text references
all_refs = {}
for doc_name, path in paths.items():
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    refs = []  # (line_num, ref_text, context)
    for i, line in enumerate(lines):
        # Find RULE references in body text (not header lines)
        if line.strip().startswith('#'):
            continue
        
        # Match patterns like "RULE 0H", "per RULE 0Q-A", "See RULE 0T", etc.
        for m in re.finditer(r'RULE\s+([0-9][A-Z]?(?:-[A-Z0-9])?)', line, re.IGNORECASE):
            ref_num = m.group(1)
            start = max(0, m.start() - 20)
            end = min(len(line), m.end() + 20)
            context = line[start:end].strip()[:80]
            refs.append((i + 1, ref_num, context))
    
    all_refs[doc_name] = refs

# Now find issues
print('\n' + '=' * 80)
print('SECTION 1: STALE/BROKEN RULE REFERENCES IN BODY TEXT')
print('(References to RULE numbers that do NOT exist as headers in the same doc)')
print('=' * 80)

issues = []
for doc_name, refs in all_refs.items():
    doc_headers = headers[doc_name]
    doc_issues = [(ln, rn, ctx) for ln, rn, ctx in refs if rn not in doc_headers]
    
    if doc_issues:
        print(f'\n  {doc_name} — {len(doc_issues)} stale reference(s):')
        for ln, rn, ctx in doc_issues:
            exists_anywhere = rn in all_valid_rules
            status = '✅ EXISTS in another doc' if exists_anywhere else '❌ NOT FOUND in ANY doc'
            print(f'    Line {ln}: RULE {rn} — {status}')
            print(f'      Context: "...{ctx}..."')
            issues.append((doc_name, ln, rn, exists_anywhere))
    else:
        print(f'\n  {doc_name} — ✅ All body references point to valid headers in this doc')

print('\n' + '=' * 80)
print('SECTION 2: CROSS-DOC REFERENCE COUNT')
print('(How many times each RULE is referenced in body text of each doc)')
print('=' * 80)

# Count refs per RULE per doc
ref_count = {}
for doc_name, refs in all_refs.items():
    counts = {}
    for _, rn, _ in refs:
        counts[rn] = counts.get(rn, 0) + 1
    ref_count[doc_name] = counts

print(f'\n{"RULE":<10} {"SI refs":<10} {"SOP refs":<10} {"MANDATES refs":<15} {"Has header?"}')
print('-' * 65)
for rn in all_valid_rules:
    si_c = ref_count.get('SI', {}).get(rn, 0)
    sop_c = ref_count.get('SOP', {}).get(rn, 0)
    mand_c = ref_count.get('MANDATES', {}).get(rn, 0)
    si_h = '✅' if rn in headers['SI'] else '❌'
    sop_h = '✅' if rn in headers['SOP'] else '❌'
    mand_h = '✅' if rn in headers['MANDATES'] else '❌'
    print(f'{rn:<10} {si_c:<10} {sop_c:<10} {mand_c:<15} SI:{si_h} SOP:{sop_h} MAND:{mand_h}')

print('\n' + '=' * 80)
print('SECTION 3: SUSPICIOUS REFERENCE PATTERNS')
print('=' * 80)

suspicious = []

for doc_name, refs in all_refs.items():
    for ln, rn, ctx in refs:
        # Check 1: Reference to a RULE that doesn't exist in ANY doc
        if rn not in all_valid_rules:
            suspicious.append((doc_name, ln, rn, ctx, 'REFERENCE TO NON-EXISTENT RULE'))
        
        # Check 2: Reference to a sub-rule without its parent existing
        # (e.g., references RULE 0H-A but doc lacks RULE 0H header)
        if '-' in rn:
            parent = rn.split('-')[0]
            if parent not in headers[doc_name] and rn in headers[doc_name]:
                suspicious.append((doc_name, ln, rn, ctx, f'SUB-RULE PRESENT BUT PARENT {parent} MISSING FROM HEADERS'))

if suspicious:
    print(f'\n  Found {len(suspicious)} suspicious patterns:')
    for doc_name, ln, rn, ctx, reason in suspicious:
        print(f'    🔴 {doc_name} line {ln}: RULE {rn} — {reason}')
        print(f'       Context: "...{ctx}..."')
else:
    print('\n  ✅ No suspicious reference patterns found')

print('\n' + '=' * 80)
print('FINAL SUMMARY')
print('=' * 80)
print(f'  Body references scanned: {sum(len(v) for v in all_refs.values())}')
print(f'  Stale/broken refs: {len(issues)}')
print(f'  Suspicious patterns: {len(suspicious)}')
print()
if issues:
    print('  Issues requiring attention:')
    for doc_name, ln, rn, exists_anywhere in issues:
        loc = 'exists in another doc' if exists_anywhere else 'does NOT exist anywhere'
        print(f'    {doc_name}:{ln} — RULE {rn} ({loc})')
