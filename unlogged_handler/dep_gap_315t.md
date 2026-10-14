# Swallow sites in tools/dep_gap_315t.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 131  silent_continue        SyntaxError                      body: continue
