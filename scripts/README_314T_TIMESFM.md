# 3.14t TimesFM Setup (venv-314t)

Free-threaded production environment for the **TimesFM 3 second-opinion anomaly layer**
on the BCC financial series. Both the pilot script and this setup were built on
**Python 3.14.7 free-threading (3.14t)** by directive — the free-threaded `torch`
build (`cp314t`) is the first one in use in this ecosystem.

## Environment

| Item | Value |
|---|---|
| Interpreter | `venv-314t/Scripts/python.exe` (Python 3.14.7, `_is_gil_enabled() == False`) |
| Location | `/c/Users/clint/venv-314t` |
| torch | `2.14.0+cpu` — **cp314t free-threaded wheel** (124 MB) |
| timesfm | `3.0.1` (ships `timesfm3` / `TimesFM3Forecaster`) |
| Model weights | `google/timesfm-3.0-pytorch` (~200 M params, one-time HuggingFace download ~166 s) |
| Supporting | `numpy 2.4.6`, `pandas 3.0.3`, `scipy 1.18.0`, `statsmodels 0.15.0` |

## Install (reproducible)

```bash
# 1. Create the free-threaded venv (one-time; already exists on this machine)
py -3.14t -m venv venv-314t

# 2. Install torch — use the cp314t free-threaded wheel (NOT the GIL build)
venv-314t/Scripts/python.exe -m pip install torch

# 3. Install TimesFM 3
venv-314t/Scripts/python.exe -m pip install timesfm

# 4. Verify free-threading + imports
venv-314t/Scripts/python.exe -c "import sys, torch; print(sys._is_gil_enabled(), torch.__version__)"
venv-314t/Scripts/python.exe -c "from timesfm3 import TimesFM3Forecaster; print('timesfm OK')"
```

> **Note:** free-threaded wheels are shipped as `cp314t`/`cp313t`+abi3 — Pip resolves
> them automatically on a 3.14t interpreter. Do **not** install the standard GIL
> torch build into this venv; it will import but loses free-threading benefits.

## Usage

```bash
# Default: all three metrics (revenue, expenses, officer_comp)
venv-314t/Scripts/python.exe azazael/scripts/timesfm_pilot_314t.py

# Single metric with explicit series path
venv-314t/Scripts/python.exe azazael/scripts/timesfm_pilot_314t.py --metrics revenue --series bcc_990_series.json
```

First run downloads `google/timesfm-3.0-pytorch` (~166 s); afterwards ~5 s load
+ ~0.1 s per forecast on 8 threads.

## Output contract

Each metric prints: `TF err` (forecast-vs-actual residual %), `z` (rolling z-score,
window w=5), and an `agreement` verdict (`DIVERGENT` when the two layers disagree).
See `BCC_FINANCIAL_ANOMALY.html` (renamed from FINANCIAL_ANOMALY_LAYER) for the Sep-4, 2026 interpretation: TimesFM flags
FY2025 revenue −15.5 % vs model where rolling z misses it (−0.33); comp z=+2.79 flags
where TimesFM is +9.0 %. The deficit (−$796,924) is only visible as the *combination*.

## Honest caveats (carried into BCC_FINANCIAL_ANOMALY.html)

- N=15 ≪ TimesFM's ≥256-point sweet spot — **pilot, not court-defensible**; z-scores remain primary.
- Single probe point (FY2025); expanding needs the pre-e-file FY2001–2010 PDF era.
- Forecast = continuation, not fact.

## Related

- `azazael/scripts/fetch_990_series.py` — builds `bcc_990_series.json` (FY2011–2025, 15 filings)
  + fully documented IRS source chain (IRS TEOS CSV index → ProPublica API v2 → `/full_text/` CDP endpoint).
- `bcc_990_series.json` + `timesfm_pilot_314t.py` live beside `BCC_FINANCIAL_ANOMALY.html` in the investigation corpus root.