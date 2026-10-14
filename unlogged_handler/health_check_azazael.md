# Swallow sites in tools/health_check_azazael.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 57   unlogged_handler       Exception                        body: elapsed = time.perf_counter() - start
