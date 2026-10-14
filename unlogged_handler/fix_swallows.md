# Swallow sites in tools/fix_swallows.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 298  unlogged_handler       SyntaxError                      body: return (src, False)
