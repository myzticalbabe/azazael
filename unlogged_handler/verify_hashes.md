# Swallow sites in tools/verify_hashes.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 18   silent_pass            (AttributeError, ValueError)     body: pass
