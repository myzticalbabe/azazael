# Swallow sites in tools/dict_key_contract.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 266  silent_continue        (SyntaxError, OSError)           body: continue
