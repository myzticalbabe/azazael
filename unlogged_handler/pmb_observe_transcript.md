# Swallow sites in tools/pmb_observe_transcript.py (4) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 110  unlogged_handler       Exception                        body: result['followcheck'] = {'error': repr(exc)}
- line 103  silent_continue        Exception                        body: continue
- line 88   unlogged_handler       Exception                        body: if not args.quiet:
- line 71   empty_literal_return   (OSError, ValueError)            body: return []
