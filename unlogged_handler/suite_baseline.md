# Swallow sites in tools/suite_baseline.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 72   unlogged_handler       subprocess.TimeoutExpired        body: timed_out = True
- line 51   silent_continue        Exception                        body: continue
