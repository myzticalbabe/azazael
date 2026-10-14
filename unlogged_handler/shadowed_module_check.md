# Swallow sites in tools/shadowed_module_check.py (5) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 171  silent_continue        (SyntaxError, OSError)           body: continue
- line 143  unlogged_handler       (SyntaxError, OSError)           body: return out
- line 121  empty_literal_return   OSError                          body: return []
- line 93   silent_continue        ValueError                       body: continue
- line 85   silent_pass            OSError                          body: pass
