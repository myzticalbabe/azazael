# Swallow sites in tools/terence_watch.py (3) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 131  unlogged_handler       Exception                        body: status = {'error': f'{type(e).__name__}: {e}'}
- line 127  unlogged_handler       Exception                        body: patterns = {'error': f'{type(e).__name__}: {e}'}
- line 122  unlogged_handler       Exception                        body: apply_error = f'{type(e).__name__}: {e}'
