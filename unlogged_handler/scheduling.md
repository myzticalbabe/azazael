# Swallow sites in src/CORE/WORMS/expansion/scheduling.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 373  unlogged_handler       (TypeError, ValueError)          body: gaps.append('non-numeric-contribution:%s' % arm)
