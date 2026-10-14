# Swallow sites in tools/deepseek_throughput_benchmark.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 86   unlogged_handler       Exception                        body: latency_ms = (time.perf_counter() - start) * 1000
