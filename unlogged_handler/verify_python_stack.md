# Swallow sites in tools/verify_python_stack.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 142  silent_pass            Exception                        body: pass
- line 89   unlogged_handler       subprocess.TimeoutExpired        body: return {'module': module, 'status': 'TIMEOUT', 'detail': f'>{timeout:g}s', 'seconds': timeout}
