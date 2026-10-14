# Swallow sites in tools/sync_codex_to_g.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 78   silent_pass            Exception                        body: pass
