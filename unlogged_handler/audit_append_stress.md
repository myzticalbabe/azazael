# Swallow sites in tools/audit_append_stress.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 91   unlogged_handler       ValueError                       body: broken.append(i)
