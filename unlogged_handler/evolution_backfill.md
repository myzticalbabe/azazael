# Swallow sites in tools/evolution_backfill.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 66   silent_continue        Exception                        body: continue
