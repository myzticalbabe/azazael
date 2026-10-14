# Swallow sites in tools/prepare_guard.py (6) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 157  silent_pass            Exception                        body: pass
- line 140  return_default         Exception                        body: return False
- line 133  return_default         Exception                        body: return False
- line 125  return_default         Exception                        body: return False
- line 100  empty_literal_return   Exception                        body: return {}
- line 75   unlogged_handler       Exception                        body: entries = []
