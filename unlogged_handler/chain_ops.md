# Swallow sites in tools/chain_ops.py (3) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 129  silent_continue        OSError                          body: continue
- line 90   unlogged_handler       Exception                        body: dur = None
- line 58   return_default         Exception                        body: return None
