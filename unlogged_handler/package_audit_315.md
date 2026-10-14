# Swallow sites in tools/package_audit_315.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 40   unlogged_handler       Exception                        body: return ([], str(e)[:120])
