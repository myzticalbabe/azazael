# Swallow sites in tools/vacuous_check_audit.py (3) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 190  unlogged_handler       OSError                          body: return findings
- line 181  unlogged_handler       (tokenize.TokenError, Indentatio body: MASK_FAILURES.append('tokenize: %s' % type(exc).__name__)
- line 159  unlogged_handler       (SyntaxError, ValueError)        body: MASK_FAILURES.append('ast: %s' % type(exc).__name__)
