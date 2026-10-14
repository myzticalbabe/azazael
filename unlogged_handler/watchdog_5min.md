# Swallow sites in tools/watchdog_5min.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 43   unlogged_handler       Exception                        body: rec['error'] = str(e)[:200]
