# Swallow sites in tools/evolution_chain_audit.py (3) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 163  unlogged_handler       Exception                        body: result['error'] = '%s: %s' % (type(exc).__name__, str(exc)[:200])
- line 95   unlogged_handler       SyntaxError                      body: rows.append({'module': rel, 'error': 'syntax: %s' % exc})
- line 72   silent_continue        (OSError, ValueError)            body: continue
