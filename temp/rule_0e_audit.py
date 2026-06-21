import sys, re
sys.stdout.reconfigure(encoding='utf-8')

paths = {
    'SYSTEM_INSTRUCTIONS.md': r'C:/Users/clint/azazael/SYSTEM_INSTRUCTIONS.md',
    'SOP.md': r'C:/Users/clint/azazael/SOP.md',
    'MANDATES.md': r'C:/Users/clint/azazael/MANDATES.md',
}

def extract_rule_section(content, rule_num):
    """Extract full body content of a RULE section."""
    pattern = r'^(#{2,3})\s+[^\n]*RULE\s+' + re.escape(rule_num) + r'[^\n]*$'
    match = re.search(pattern, content, re.MULTILINE)
    if not match:
        return None

    start = match.start()
    header_end = match.end()
    rest = content[header_end:]

    # Find next RULE header or major section break
    end_search = re.search(r'\n#{2,3}\s+[^\n]*RULE\s+[0-9]', rest)
    if end_search:
        end_pos = header_end + end_search.start()
    else:
        sep_search = re.search(r'\n---\n', rest)
        if sep_search:
            end_pos = header_end + sep_search.start()
        else:
            end_pos = len(content)

    return content[start:end_pos]


for doc_name, path in paths.items():
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    print('=' * 70)
    print(f'{doc_name} — RULE 0E')
    print('=' * 70)
    section = extract_rule_section(content, '0E')
    if section:
        lines = section.split('\n')
        print(f'  ({len(section)} chars, {len(lines)} lines)')
        print(f'  Content:')
        for i, line in enumerate(lines):
            if line.strip():
                print(f'    {line[:250]}')
        print()
    else:
        print('  ❌ NOT FOUND')
        print()

    print(f'--- {doc_name} — RULE 0E-1 ---')
    section_e1 = extract_rule_section(content, '0E-1')
    if section_e1:
        lines_e1 = section_e1.split('\n')
        print(f'  ({len(section_e1)} chars, {len(lines_e1)} lines)')
        print(f'  Content:')
        for i, line in enumerate(lines_e1):
            if line.strip():
                print(f'    {line[:250]}')
    else:
        print('  ❌ NOT FOUND')
    print()
