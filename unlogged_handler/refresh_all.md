# Swallow sites in tools/refresh_all.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 117  unlogged_handler       subprocess.TimeoutExpired        body: return {'cmd': ' '.join(args), 'rc': None, 'error': 'timeout'}
- line 81   silent_continue        ValueError                       body: continue
