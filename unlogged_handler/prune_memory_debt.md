# Swallow sites in tools/prune_memory_debt.py (5) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 328  unlogged_handler       sqlite3.Error                    body: result['ok'] = False
- line 313  unlogged_handler       OSError                          body: result['ok'] = False
- line 254  unlogged_handler       sqlite3.Error                    body: result['ok'] = False
- line 221  unlogged_handler       sqlite3.Error                    body: rejected.append('%s: query failed (%s)' % (col, exc))
- line 140  unlogged_handler       OSError                          body: group['files'].append((entry.name, 0, 0.0, directory))
