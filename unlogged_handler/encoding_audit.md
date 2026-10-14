# Swallow sites in tools/encoding_audit.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 201  unlogged_handler       ValueError                       body: return str(path)
- line 169  unlogged_handler       SyntaxError                      body: return {'path': path, 'scanned': False, 'findings': [], 'undetermined': [], 'skipped': 'line %s: %s' % (exc.li
