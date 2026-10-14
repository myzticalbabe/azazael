# Swallow sites in tools/audit_parseable_files.py (4) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 185  empty_literal_return   Exception                        body: return set()
- line 165  unlogged_handler       Exception                        body: corrupt_pdf.append({'path': rel, 'error': type(exc).__name__, 'detail': str(exc)[:120]})
- line 147  silent_continue        OSError                          body: continue
- line 135  unlogged_handler       ImportError                      body: deep_unavailable = True
