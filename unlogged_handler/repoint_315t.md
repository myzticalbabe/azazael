# Swallow sites in tools/repoint_315t.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 152  unlogged_handler       Exception                        body: return (False, f're-parse FAILED: {type(exc).__name__}: {exc}')
- line 146  unlogged_handler       ImportError                      body: return (True, 'yaml not installed here; skipped re-parse')
