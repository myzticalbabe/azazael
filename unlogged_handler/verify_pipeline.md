# Swallow sites in tools/verify_pipeline.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 81   empty_literal_return   (ValueError, IndexError)         body: return []
- line 63   unlogged_handler       json.JSONDecodeError             body: sys.stderr.write('  [%s] torn line %d skipped\n' % (path.name, lineno))
