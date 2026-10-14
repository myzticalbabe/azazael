# Swallow sites in tools/terence_env_digest.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 55   unlogged_handler       Exception                        body: return {'error': str(exc)}
- line 42   unlogged_handler       Exception                        body: return 'view failed: %s' % exc
