# Swallow sites in tools/monitor_theme.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 143  return_default         (TypeError, ValueError)          body: return 'unknown'
- line 71   silent_pass            Exception                        body: pass
