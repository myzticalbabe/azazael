import sys, re
sys.stdout.reconfigure(encoding='utf-8')
import pathlib

root = pathlib.Path('C:/Users/clint/azazael/.agents/skills')

paths = {
    'SI': root / 'azazael-system-startup/SKILL.md',
    'SOP': root / 'azazael-sop/SKILL.md',
    'MANDATES': root / 'azazael-mandates/SKILL.md',
}

print('=== SYNCED SKILL FILE AUDIT ===')
print()

all_ok = True

for name, path in paths.items():
    if not path.exists():
        # Fall back to canonical source
        alt = pathlib.Path(f'C:/Users/clint/azazael/skills/{name.lower()}.md')
        if alt.exists():
            path = alt
            print(f'  {name}: using canonical {alt.name} (no SKILL.md)')
        else:
            print(f'  MISSING: {name}')
            all_ok = False
            continue
    
    c = path.read_text(encoding='utf-8')
    
    # Check size
    print(f'  {name} ({path.name}): {len(c):,} bytes')
    
    # Check RULE headers
    headers = re.findall(
        r'^(#{2,3})\s+.*?RULE\s+([0-9][A-Z]?(?:-[A-Z0-9])?)',
        c, re.MULTILINE
    )
    print(f'    RULE headers: {len(headers)} found')
    
    # Check for full "June" dates (should be "Jun")
    full_june = re.findall(r'June\s+\d+,?\s+2026', c)
    if full_june:
        print(f'    ⚠️  {len(full_june)} remaining "June" dates (should be "Jun")')
        for m in full_june:
            print(f'         -> "{m}"')
        all_ok = False
    else:
        print(f'    ✅ All dates use "Jun" format')
    
    # Check for "Jun" dates
    jun_dates = re.findall(r'Jun\s+\d+,?\s+2026', c)
    print(f'    Jun dates: {len(jun_dates)}')
    
    # Check specific RULEs of interest
    for target in ['0E', '0F', '0G', '0H', '0J', '0P', '0Z', '0E-1']:
        found = bool(re.search(
            r'^(#{2,3})\s+.*?RULE\s+' + target + r'(?:[^0-9A-Z]|$)',
            c, re.MULTILINE
        ))
        status = '✅' if found else '❌'
        print(f'    RULE {target}: {status}')
    
    print()

if all_ok:
    print('✅ All skill files consistent')
else:
    print('⚠️  Issues found (see above)')
