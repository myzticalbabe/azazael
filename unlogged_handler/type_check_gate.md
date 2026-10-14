# Swallow sites in tools/type_check_gate.py (4) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 276  empty_literal_return   (OSError, ValueError)            body: return {}
- line 181  unlogged_handler       OSError                          body: text = ''
- line 169  unlogged_handler       (ValueError, OSError)            body: return raw
- line 130  empty_literal_return   (OSError, ValueError)            body: return []
