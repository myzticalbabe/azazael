# Swallow sites in tools/wsl_revision_diff.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 130  unlogged_handler       OSError                          body: return {'path': rel, 'status': 'UNREADABLE', 'local_lines': 0, 'mirror_lines': 0, 'local_only': 0, 'mirror_onl
