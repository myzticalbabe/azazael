# Swallow sites in tools/fs_hygiene.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 221  unlogged_handler       ValueError                       body: base = {}
- line 69   unlogged_handler       OSError                          body: size = 0
