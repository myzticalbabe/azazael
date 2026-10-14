# Swallow sites in tools/pmb_session_observe.py (3) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 175  unlogged_handler       Exception                        body: fc = {'error': repr(exc)}
- line 166  unlogged_handler       Exception                        body: if not args.quiet:
- line 116  unlogged_handler       Exception                        body: return out
