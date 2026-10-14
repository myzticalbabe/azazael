# Swallow sites in tools/pmb_e2e_check.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 173  return_default         NameError                        body: return False
- line 26   unlogged_handler       Exception                        body: ok, detail = (False, '%s: %s' % (type(exc).__name__, exc))
