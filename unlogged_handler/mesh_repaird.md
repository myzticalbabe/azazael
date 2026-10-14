# Swallow sites in tools/mesh_repaird.py (6) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 143  unlogged_handler       Exception                        body: escalate.append(f'M5 disk check failed: {e}')
- line 135  unlogged_handler       Exception                        body: escalate.append(f'M3 spine_registry unreadable: {e}')
- line 111  marker_hidden          (ValueError, TypeError)          body: pass
- line 92   unlogged_handler       Exception                        body: escalate.append(f'M2 scheduler query failed: {e}')
- line 79   unlogged_handler       Exception                        body: escalate.append(f'M1 workspace walk failed: {e}')
- line 50   unlogged_handler       OSError                          body: return -1.0
