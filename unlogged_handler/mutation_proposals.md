# Swallow sites in tools/mutation_proposals.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 183  silent_continue        ValueError                       body: continue
- line 148  empty_literal_return   ValueError                       body: return {}
