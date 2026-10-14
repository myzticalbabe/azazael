# Swallow sites in tools/pmb_capture.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 74   unlogged_handler       Exception                        body: sys.stderr.write('pmb_capture failed: %r\n' % (exc,))
