# Swallow sites in tools/pytest_fixture_watch.py (4) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 118  silent_pass            Exception                        body: pass
- line 90   return_default         Exception                        body: return
- line 80   unlogged_handler       TypeError                        body: return repr(value)[:80]
- line 59   silent_pass            Exception                        body: pass
