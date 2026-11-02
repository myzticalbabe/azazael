src = open('src/CODEX/Azazael_DUAL_PANE.md', encoding='utf-8').read()
lines = src.split('\n')
old = lines[688]
lines[688] = old + '  <!-- MOCKUP: display only, not evidence -->'
open('src/CODEX/Azazael_DUAL_PANE.md', 'w', encoding='utf-8').write('\n'.join(lines))
print('done')