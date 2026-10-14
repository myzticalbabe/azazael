# Swallow sites in tools/swallow_inventory.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 245  silent_continue        OSError                          body: continue
- line 215  empty_literal_return   SyntaxError                      body: return []
