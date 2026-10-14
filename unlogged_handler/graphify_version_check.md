# Swallow sites in tools/graphify_version_check.py (3) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 103  unlogged_handler       Exception                        body: resolved = None
- line 93   unlogged_handler       Exception                        body: return {'install': None, 'patched': False, 'reason': str(exc)}
- line 65   return_default         Exception                        body: return None
