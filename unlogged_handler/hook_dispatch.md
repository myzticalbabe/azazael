# Swallow sites in tools/hook_dispatch.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 221  unlogged_handler       Exception                        body: return (False, f'{type(e).__name__}: {e}'[:80])
