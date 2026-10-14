# Swallow sites in tools/install_pams_315t.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 195  silent_continue        ValueError                       body: continue
- line 80   unlogged_handler       SyntaxError                      body: return found
