# Swallow sites in tools/adoption_census.py (7) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 690  silent_continue        (OSError, IndexError, ValueError body: continue
- line 679  silent_continue        (OSError, IndexError, ValueError body: continue
- line 600  silent_continue        (OSError, IndexError, ValueError body: continue
- line 429  silent_continue        OSError                          body: continue
- line 279  unlogged_handler       OSError                          body: text = ''
- line 257  unlogged_handler       (SyntaxError, ValueError, Memory body: _tree = None
- line 154  unlogged_handler       (SyntaxError, ValueError, Memory body: return skip
