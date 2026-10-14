# Swallow sites in tools/live_record_probe_315t.py (6) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 230  unlogged_handler       Exception                        body: report['probes'].append({'store': probe.__name__, 'verdict': FAIL, 'notes': [f'probe crashed: {type(exc).__nam
- line 216  unlogged_handler       Exception                        body: result['notes'].append(f'end() raised {type(exc).__name__}: {exc}')
- line 189  unlogged_handler       Exception                        body: result['notes'].append(f'record() raised {type(exc).__name__}: {exc}')
- line 147  unlogged_handler       Exception                        body: result['notes'].append(f'read path raised {type(exc).__name__}: {exc}')
- line 142  silent_continue        TypeError                        body: continue
- line 121  unlogged_handler       Exception                        body: result['notes'].append(f'record_event raised {type(exc).__name__}: {exc}')
