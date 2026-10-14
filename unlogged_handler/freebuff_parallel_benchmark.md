# Swallow sites in tools/freebuff_parallel_benchmark.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 54   unlogged_handler       Exception                        body: duration = time.perf_counter() - start
- line 51   unlogged_handler       subprocess.TimeoutExpired        body: duration = time.perf_counter() - start
