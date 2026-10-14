# Swallow sites in tools/verify_mesh_html.py (5) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 281  unlogged_handler       Exception                        body: proc.kill()
- line 275  unlogged_handler       Exception                        body: problems.append(f'browser harness error: {type(exc).__name__}: {exc}')
- line 157  silent_pass            Exception                        body: pass
- line 149  silent_continue        Exception                        body: continue
- line 130  silent_continue        Exception                        body: continue
