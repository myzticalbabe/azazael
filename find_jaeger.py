import os
path = 'src/CODEX/Azazael_DUAL_PANE.md'
src = open(path, encoding='utf-8', errors='replace').read()
for i, line in enumerate(src.split('\n')):
    if 'jaeger' in line.lower() or 'zipkin' in line.lower():
        print('line', i+1, ':', line.strip()[:120].encode('ascii', errors='replace').decode('ascii'))