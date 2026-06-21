"""Step 1: Un-merge statements squashed onto single lines by the regex."""
import re, os

base = 'src'
files = [
    'CORE/FREETHREAD_UPGRADE.py',
    'CORE/NeuralPipeline.py',
    'CORE/WORMS/CLUSTERWORMS.py',
    'CORE/WORMS/METACLUSTER.py',
    'CORE/WORMS/NATURE_CLUSTERS.py',
    'CORE/WORMS/expansion/learning.py',
    'CORE/cd2_verifier.py',
    'CORE/freethreading.py',
    'CORE/postgres_memory.py',
    'CORE/threading_utils.py',
    'METAWORMS_ENRICHED.py',
]

# Patterns: (regex, replacement) - insert newline+indent before merged keywords
# We look for a Python token (word/paren/eq) followed by 2+ spaces and a keyword
MERGE_FIXES = [
    # def inside a class or at module level after another statement
    (r'(\w)\s{2,}(def\s)', r'\1\n\2'),
    # class after another statement
    (r'(\w)\s{2,}(class\s)', r'\1\n\2'),
    # import after another statement (like `= True    import`)
    (r'(= \w+)\s{2,}(import\s)', r'\1\n\2'),
    # Variable after another assignment (like `= dict    ThreadSafeList`)
    (r'(= (?:dict|list|None|True|False))\s{2,}([A-Z]\w+)', r'\1\n\2'),
    # @property / @staticmethod after code
    (r'(\w)\s{2,}(@\w+)', r'\1\n\2'),
    # z3 import pattern
    (r'(import z3)\s{2,}(Z3_AVAILABLE)', r'\1\n\2'),
    # self._lock after another assignment
    (r'(= None)\s{2,}(self\.)', r'\1\n        \2'),
]

for rel_path in files:
    filepath = f'{base}/{rel_path}'
    if not os.path.exists(filepath):
        print(f'MISSING: {rel_path}')
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    changes = 0
    for pattern, replacement in MERGE_FIXES:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            changes += 1
            content = new_content

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'FIXED: {rel_path} ({changes} pattern(s))')
    else:
        print(f'NO CHANGE: {rel_path}')

print('\nStep 1 complete. Next: Step 2 - fix specific lines.')
