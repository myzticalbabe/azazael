# Swallow sites in tools/commit_scope_check.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 118  unlogged_handler       OSError                          body: same = False
