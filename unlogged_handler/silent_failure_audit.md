# Swallow sites in tools/silent_failure_audit.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 103  silent_continue        SyntaxError                      body: continue
