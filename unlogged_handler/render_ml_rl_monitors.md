# Swallow sites in tools/render_ml_rl_monitors.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 475  unlogged_handler       Exception                        body: q_err = f'{type(exc).__name__}: {exc}'[:100]
