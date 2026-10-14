# Swallow sites in tools/capability_liveness.py (9) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 317  unlogged_handler       Exception                        body: status, detail = (FAIL, f'check raised {type(exc).__name__}: {exc}')
- line 277  unlogged_handler       Exception                        body: rc = f'raised {type(exc).__name__}'
- line 274  unlogged_handler       SystemExit                       body: rc = 0 if exc.code is None else exc.code
- line 264  unlogged_handler       Exception                        body: return (DORMANT, f'artifact_freshness unavailable ({type(exc).__name__})')
- line 140  return_default         ValueError                       body: return False
- line 126  return_default         ValueError                       body: return False
- line 120  return_default         ValueError                       body: return False
- line 104  return_default         (TypeError, ValueError)          body: return 0
- line 82   unlogged_handler       Exception                        body: return {'__error__': f'{type(exc).__name__}: {exc}'}
