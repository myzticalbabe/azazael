# Swallow sites in tools/converge_315.py (4) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 259  silent_pass            Exception                        body: pass
- line 119  unlogged_handler       Exception                        body: return {**out, 'parse_error': str(e)[:200]}
- line 94   unlogged_handler       Exception                        body: return (set(), [f'unreadable quarantine file: {e}'[:200]])
- line 67   unlogged_handler       subprocess.TimeoutExpired        body: return {'ok': False, 'timeout': True, 'tail': ['TIMEOUT']}
