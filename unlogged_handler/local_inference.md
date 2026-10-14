# Swallow sites in tools/local_inference.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 153  silent_continue        ValueError                       body: continue
- line 84   empty_literal_return   Exception                        body: return []
