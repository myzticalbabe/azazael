# Swallow sites in tools/self_modify.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 170  silent_pass            Exception                        body: pass
- line 60   unlogged_handler       subprocess.TimeoutExpired        body: return {'rc': None, 'out': '', 'err': 'timeout', 'timeout': True}
