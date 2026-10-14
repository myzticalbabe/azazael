# Swallow sites in tools/model_driver.py (3) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 120  unlogged_handler       OSError                          body: return -1
- line 110  silent_continue        Exception                        body: continue
- line 91   unlogged_handler       Exception                        body: return {'ok': False, 'error': repr(exc)[:200], 'elapsed_s': round(time.time() - t0, 2)}
