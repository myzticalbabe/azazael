import re
src = open('src/AOA/core/router.py', encoding="utf-8").read()
for m in re.finditer(r'_outcome', src):
    line = src[:m.start()].count('\n') + 1
    ctx = src[max(0,m.start()-40):m.start()+40].replace('\n', ' ')
    print(f'line {line}: {ctx}')