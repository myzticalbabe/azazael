# Swallow sites in tools/run_suite_chunked.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 124  unlogged_handler       subprocess.TimeoutExpired        body: stdout = exc.stdout or b''
