# Swallow sites in tools/monitor_data.py (23) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 658  return_default         Exception                        body: return None
- line 653  return_default         Exception                        body: return None
- line 638  unlogged_handler       Exception                        body: return default
- line 552  unlogged_handler       Exception                        body: d['_error'] = str(exc)[:120]
- line 550  unlogged_handler       ImportError                      body: d['_error'] = f'mesh modules unavailable: {exc}'
- line 548  silent_pass            ImportError                      body: pass
- line 481  unlogged_handler       Exception                        body: d['_error'] = str(exc)[:120]
- line 479  unlogged_handler       ImportError                      body: d['_error'] = f'registry unavailable: {exc}'
- line 463  unlogged_handler       Exception                        body: d['_error'] = str(exc)[:120]
- line 411  unlogged_handler       Exception                        body: payload['published'] = False
- line 386  unlogged_handler       ImportError                      body: payload['written_by'] = 'unknown'
- line 379  unlogged_handler       Exception                        body: previous = {}
- line 320  unlogged_handler       Exception                        body: d['_error'] = str(exc)[:120]
- line 263  unlogged_handler       Exception                        body: d['_error'] = str(exc)[:120]
- line 229  unlogged_handler       Exception                        body: d['_error'] = str(exc)[:120]
- line 227  unlogged_handler       ImportError                      body: d['_error'] = f'spine unavailable: {exc}'
- line 166  unlogged_handler       Exception                        body: return float('inf')
- line 125  unlogged_handler       Exception                        body: return ('absent', True)
- line 113  unlogged_handler       Exception                        body: return ('unparseable', True)
- line 87   return_default         (TypeError, ValueError)          body: return None
- line 76   silent_continue        Exception                        body: continue
- line 68   unlogged_handler       Exception                        body: return out
- line 58   empty_literal_return   Exception                        body: return {}
