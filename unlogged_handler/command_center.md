# Swallow sites in tools/command_center.py (10) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 460  unlogged_handler       Exception                        body: errors.append(f'{key}: {type(exc).__name__}: {exc}')
- line 291  unlogged_handler       Exception                        body: return _panel('exmachina', 'EX MACHINA', 'unknown', 'collector unavailable', [_metric('Severity', 'unknown'), 
- line 257  unlogged_handler       (TypeError, ValueError)          body: violation_count = 0
- line 237  unlogged_handler       Exception                        body: return _panel('aoa', 'AOA', 'unknown', 'collector unavailable', [_metric('Arms', 'unknown'), _metric('Workflow
- line 223  return_default         ValueError                       body: return None
- line 153  unlogged_handler       Exception                        body: live_chain_detail = f'{type(exc).__name__}: {exc}'[:160]
- line 120  unlogged_handler       Exception                        body: return _panel('azazael', 'AZAZAEL', 'unknown', 'collector unavailable', [_metric('Mesh', 'unknown'), _metric('
- line 75   unlogged_handler       (TypeError, ValueError)          body: return str(value)
- line 66   return_default         OSError                          body: return None
- line 39   unlogged_handler       (OSError, ValueError)            body: return default
