# Swallow sites in tools/tiktok_batch.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 37   unlogged_handler       Exception                        body: return {'error': str(e)}
