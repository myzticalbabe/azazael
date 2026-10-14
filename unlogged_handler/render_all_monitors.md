# Swallow sites in tools/render_all_monitors.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 33   unlogged_handler       Exception                        body: return (False, f'{target}: spawn failed: {exc}'[:160])
