# Swallow sites in tools/verify_engram_mcp.py (14) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 589  unlogged_handler       Exception                        body: _note('handshake/kill-final', e)
- line 576  unlogged_handler       Exception                        body: _note('json-line', e)
- line 563  unlogged_handler       Exception                        body: _note('handshake/kill-after-write-failure', ke)
- line 560  unlogged_handler       Exception                        body: try:
- line 552  unlogged_handler       Exception                        body: _note('handshake/spawn', e)
- line 530  unlogged_handler       Exception                        body: _note('append_log', e)
- line 461  unlogged_handler       Exception                        body: _note('classify_restart/resolve', e)
- line 435  unlogged_handler       Exception                        body: _note('latest_marker', e)
- line 429  unlogged_handler       Exception                        body: _note('json-line', e)
- line 410  unlogged_handler       Exception                        body: _note('config_sha', e)
- line 401  unlogged_handler       Exception                        body: _note('count_log_lines', e)
- line 393  unlogged_handler       Exception                        body: _note('session-log/read', e)
- line 355  unlogged_handler       Exception                        body: _note('parse_ts', e)
- line 193  unlogged_handler       Exception                        body: _note('read_config', e)
