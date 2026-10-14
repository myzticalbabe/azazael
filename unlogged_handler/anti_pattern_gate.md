# Swallow sites in tools/anti_pattern_gate.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 184  unlogged_handler       ValueError                       body: rel = r.filepath
