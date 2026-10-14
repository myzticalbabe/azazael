# Swallow sites in tools/canon_drift_check.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 215  unlogged_handler       Exception                        body: res = None
- line 78   unlogged_handler       Exception                        body: _MERGE_SOPS = None
