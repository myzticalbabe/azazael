# Swallow sites in tools/engram_supervise.py (3) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 153  unlogged_handler       Exception                        body: parse_error = '%s: %s' % (type(exc).__name__, exc)
- line 75   unlogged_handler       ValueError                       body: n = 0
- line 42   unlogged_handler       Exception                        body: return f'__ERR__ {e}'
