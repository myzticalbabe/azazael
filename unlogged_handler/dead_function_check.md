# Swallow sites in tools/dead_function_check.py (3) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 263  unlogged_handler       ValueError                       body: lineno = 0
- line 143  silent_pass            AttributeError                   body: pass
- line 112  silent_continue        (SyntaxError, OSError)           body: continue
