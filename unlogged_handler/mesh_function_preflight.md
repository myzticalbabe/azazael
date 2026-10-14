# Swallow sites in tools/mesh_function_preflight.py (11) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 1452 unlogged_handler       Exception                        body: prior = {}
- line 1198 silent_continue        SyntaxError                      body: continue
- line 1141 unlogged_handler       ValueError                       body: rel = path.as_posix()
- line 1137 silent_continue        OSError                          body: continue
- line 1119 silent_pass            OSError                          body: pass
- line 1076 silent_continue        SyntaxError                      body: continue
- line 975  silent_continue        SyntaxError                      body: continue
- line 810  silent_continue        SyntaxError                      body: continue
- line 513  silent_continue        SyntaxError                      body: continue
- line 276  silent_continue        SyntaxError                      body: continue
- line 196  return_default         OSError                          body: return ''
