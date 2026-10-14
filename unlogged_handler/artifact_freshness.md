# Swallow sites in tools/artifact_freshness.py (4) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 224  unlogged_handler       OSError                          body: missing.append(rel)
- line 214  unlogged_handler       ValueError                       body: rel = path.name
- line 196  unlogged_handler       (OSError, ValueError)            body: out.update({'checked': True, 'reason': 'manifest unreadable: %s' % str(exc)[:80]})
- line 128  unlogged_handler       (OSError, ValueError)            body: out.update({'checked': True, 'mismatch': True, 'reason': 'graph.json unreadable: %s' % str(exc)[:80]})
