# Swallow sites in tools/accelerator_bench.py (3) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 83   unlogged_handler       Exception                        body: return {'ok': False, 'error': '%s: %s' % (type(e).__name__, e)}
- line 81   unlogged_handler       urllib.error.HTTPError           body: return {'ok': False, 'error': 'HTTP %s: %s' % (e.code, e.read()[:200])}
- line 68   unlogged_handler       Exception                        body: return 'unknown (probe failed: %s)' % type(e).__name__
