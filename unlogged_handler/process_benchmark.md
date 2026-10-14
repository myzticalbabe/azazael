# Swallow sites in tools/process_benchmark.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 138  unlogged_handler       Exception                        body: return {'status': 'NO_DATA', 'why': f'{type(e).__name__}: {e}'}
