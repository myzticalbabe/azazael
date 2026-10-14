# Swallow sites in tools/evolution_progress.py (4) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 382  unlogged_handler       Exception                        body: prev = None
- line 215  unlogged_handler       ValueError                       body: value = ast.literal_eval(text)
- line 171  unlogged_handler       Exception                        body: BEST_PARSE_FAILURES.append('%s: %s' % (m.group(1), exc))
- line 131  unlogged_handler       OSError                          body: return {'path': path, 'found': True, 'bytes': 0, 'unreadable': True, 'reason': 'stat failed: %s' % exc}
