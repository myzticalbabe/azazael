# Swallow sites in tools/pmb_client.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 114  unlogged_handler       (ValueError, TypeError)          body: return text
- line 68   unlogged_handler       Exception                        body: entries = []
