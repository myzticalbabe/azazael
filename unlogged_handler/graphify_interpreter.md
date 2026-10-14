# Swallow sites in tools/graphify_interpreter.py (3) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 142  unlogged_handler       OSError                          body: skill = ''
- line 96   return_default         (OSError, subprocess.TimeoutExpi body: return '?'
- line 82   return_default         (OSError, subprocess.TimeoutExpi body: return None
