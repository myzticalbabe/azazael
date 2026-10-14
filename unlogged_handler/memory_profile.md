# Swallow sites in tools/memory_profile.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 46   unlogged_handler       Exception                        body: results.append((mod_name, 0, 0, [], f'FAILED: {e}'))
