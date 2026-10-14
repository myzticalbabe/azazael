# Swallow sites in tools/accelerator_preflight.py (6) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 362  unlogged_handler       Exception                        body: write_error = ('%s: %s' % (type(e).__name__, e))[:160]
- line 206  unlogged_handler       Exception                        body: rec['status'] = 'ERROR'
- line 201  unlogged_handler       subprocess.TimeoutExpired        body: rec['status'] = 'TIMEOUT'
- line 179  unlogged_handler       Exception                        body: rec['status'] = 'UNPARSEABLE'
- line 170  unlogged_handler       Exception                        body: rec['status'] = 'ERROR'
- line 166  unlogged_handler       subprocess.TimeoutExpired        body: rec['status'] = 'TIMEOUT'
