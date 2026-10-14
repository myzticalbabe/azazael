# Swallow sites in tools/audit_chain_repair.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 190  unlogged_handler       ValueError                       body: return (False, 'line %d is not JSON' % number)
- line 139  unlogged_handler       ValueError                       body: items.append(('torn', line))
