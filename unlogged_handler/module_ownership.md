# Swallow sites in tools/module_ownership.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 55   silent_continue        OSError                          body: continue
