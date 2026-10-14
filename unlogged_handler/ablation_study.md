# Swallow sites in src/CORE/WORMS/expansion/ablation_study.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 321  unlogged_handler       Exception                        body: duration_ms = (time.perf_counter() - start) * 1000
