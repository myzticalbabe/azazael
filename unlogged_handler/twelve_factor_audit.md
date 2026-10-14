# Swallow sites in tools/twelve_factor_audit.py (6) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 486  unlogged_handler       ValueError                       body: rel = path.name
- line 476  silent_continue        OSError                          body: continue
- line 273  silent_continue        OSError                          body: continue
- line 227  silent_continue        OSError                          body: continue
- line 194  unlogged_handler       OSError                          body: diverged.append(p.name)
- line 145  silent_continue        OSError                          body: continue
