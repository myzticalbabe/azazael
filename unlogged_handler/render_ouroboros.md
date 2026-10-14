# Swallow sites in tools/render_ouroboros.py (4) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 246  unlogged_handler       Exception                        body: blind.append(f'{fname} unreadable')
- line 236  unlogged_handler       OSError                          body: blind.append(f'{fname} mtime unreadable')
- line 154  unlogged_handler       Exception                        body: _blind('state/%s (UNREADABLE: %s)' % (name, type(exc).__name__))
- line 135  unlogged_handler       OSError                          body: _blind('mtime of %s (%s)' % (p, type(exc).__name__))
