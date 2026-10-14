# Swallow sites in tools/psyche_live_fit.py (3) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 215  unlogged_handler       Exception                        body: return 'emit-theta: FAILED (%s)' % exc
- line 101  unlogged_handler       Exception                        body: return blank
- line 92   silent_pass            (TypeError, ValueError)          body: pass
