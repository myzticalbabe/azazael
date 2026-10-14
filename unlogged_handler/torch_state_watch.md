# Swallow sites in tools/torch_state_watch.py (5) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 152  silent_pass            Exception                        body: pass
- line 131  silent_pass            Exception                        body: pass
- line 123  silent_pass            Exception                        body: pass
- line 92   silent_pass            Exception                        body: pass
- line 71   unlogged_handler       Exception                        body: return (False, [], [])
