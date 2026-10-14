# Swallow sites in tools/aggregate_suite_gate.py (7) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 378  silent_pass            OSError                          body: pass
- line 362  silent_pass            Exception                        body: pass
- line 330  unlogged_handler       queue_mod.Empty                  body: line = ''
- line 314  silent_pass            Exception                        body: pass
- line 290  unlogged_handler       OSError                          body: if handle:
- line 281  unlogged_handler       OSError                          body: handle = None
- line 244  empty_literal_return   (OSError, ValueError)            body: return []
