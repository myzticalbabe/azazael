# Swallow sites in tools/revert_selftest.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 123  unlogged_handler       Exception                        body: cases.append({'case': fn.__name__, 'passed': False, 'detail': repr(exc)[:200]})
