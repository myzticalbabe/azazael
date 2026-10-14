# Swallow sites in tools/graph_rebuild.py (4) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 172  unlogged_handler       subprocess.TimeoutExpired        body: return {'rc': None, 'tail': ['timeout']}
- line 141  unlogged_handler       subprocess.TimeoutExpired        body: text = exc.stdout or '' if isinstance(exc.stdout, str) else ''
- line 116  silent_continue        OSError                          body: continue
- line 99   silent_pass            (OSError, subprocess.TimeoutExpi body: pass
