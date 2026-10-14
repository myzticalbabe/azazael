# Swallow sites in tools/fitness_arm_liveness.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 89   unlogged_handler       OSError                          body: return {'path': path, 'found': True, 'bytes': 0, 'unreadable': True, 'reason': 'stat failed: %s' % exc}
