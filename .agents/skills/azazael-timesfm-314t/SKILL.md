---
name: azazael-timesfm-314t
description: TimesFM 3 second-opinion anomaly layer + Bai-Perron breakpoint dating on 3.14t free-threaded venv — 990-series financial analysis, verbose.
metadata:
  category: investigation
  project: azazael
---
# 🧮 Skill: TimesFM 3 + Bai-Perron on the 3.14t Free-Threaded Venv
*Second-opinion financial anomaly detection and formal regime-change dating for the BCC 990 series — built entirely on the production 3.14t free-threaded stack (venv-314t), per the free-threading-optimization directive. Proven end-to-end Sep 4, 2026.*
## Environment (venv-314t — reproducible setup)
| Item | Value |
|---|---|
| Interpreter | `venv-314t/Scripts/python.exe` (Python 3.14.7, `sys._is_gil_enabled() == False`) |
| torch | `2.14.0+cpu` — **cp314t free-threaded wheel** (124 MB) — do NOT install the GIL build |
| timesfm | `3.0.1` (ships `timesfm3` / `TimesFM3Forecaster`) |
| Model weights | `google/timesfm-3.0-pytorch` (~200M; one-time download ~166 s, then ~5 s load + ~0.1 s/forecast) |
| numpy / scipy | `2.4.6` / `1.18.0` (working on 3.14t) |
| statsmodels | `0.15.0` — **partially broken under 3.14t** (see trap below); not needed for these tools |
Install: `py -3.14t -m venv venv-314t` → `venv-314t/Scripts/python.exe -m pip install torch timesfm` → verify
`venv-314t/Scripts/python.exe -c "import sys, torch; print(sys._is_gil_enabled(), torch.__version__)"`.
## Tools (both numpy-only — no statsmodels dependency)
1. **`timesfm_pilot_314t.py`** — TimesFM 3 zero-shot forecast of the last series point (probe) per metric,
+ rolling z-score (w=5) baseline. Prints `TF err % / z / agreement` per metric.
Run: `venv-314t/Scripts/python.exe timesfm_pilot_314t.py --metrics revenue expenses officer_comp`
2. **`bai_perron_breakpoints.py`** — formal Bai-Perron (1998/2003) sequential breakpoint dating:
DP globally-optimal partitions (m=0..4, pure mean-shift), `supF(l+1|l)` sequential tests, UDmax,
**Monte-Carlo finite-sample critical values (10,000 sims at T=15)**. Output includes JSON dump via `--out`.
Run: `venv-314t/Scripts/python.exe azazael/scripts/bai_perron_breakpoints.py --series bcc_990_series.json --out bcc_bai_perron_results.json`
## Data
`bcc_990_series.json` — full 15-filing FY2011–2025 series (revenue / expenses / officer_comp),
built by `azazael/scripts/fetch_990_series.py` (source chain: IRS TEOS CSV index → ProPublica API v2 →
ProPublica `/full_text/{OBJECT_ID}/IRS990` via CDP network monitoring; the AWS `irs-form-990` bucket is DEPRECATED).
## Established findings (FY2011–2025, EIN 23-2043478)
- **Regime change formally dated = FY2018** (CCBHC start): revenue `supF(1|0)=91.18`, p=0.000 (finite-sample MC);
segment means 4.85M → 12.36M. UDmax=306.89 (p=0.000). Expenses mirror the same break dates (FY2014/18/21).
- **Officer comp broke a year EARLIER — FY2017** (`supF(1|0)=108.50`, p=0.000; 107.6K → 237.1K), then FY2020/FY2023.
- **FY2025 = first deficit of the CCBHC era (−$796,924)**, invisible to either detector alone:
TimesFM flags revenue −15.5% vs model (14.78M expected); rolling z flags comp (+2.79). Combination = structural story.
## Traps & gotchas (learned the hard way)
- **statsmodels 0.15.0 has NO `tsa.structural_break`/BaiPerron module** — not in any installed version; don't go
looking for it. Implement the procedure directly in numpy (as `bai_perron_breakpoints.py` does).
- **statsmodels compiled extensions break under 3.14t**: `statsmodels.robust._qn` and
`statsmodels.tsa._innovations` fail to import on the free-threaded build (venv-314t resolves statsmodels from
the system site-packages via `--system-site-packages`, but the compiled `.pyd` won't load with GIL off).
If you must use statsmodels (OLS/tables), use the **system GIL Python** (`python`), or numpy/scipy only.
- **CPython 3.14t wheel tags**: torch must be the `cp314t` wheel; pip resolves automatically on a 3.14t
interpreter. Installing the standard GIL torch build imports but loses free-threading.
- **N=15 humility**: at 15 annual points, asymptotic Bai-Perron tables are not defensible → use Monte-Carlo
finite-sample critical values (the `--nsim` default is 10,000). Break dates carry ±1yr uncertainty.
- **NYC label offset**: when labeling 0-based break indices as fiscal years over a series starting FY2011,
use `+2011`, not `+2010` (the year of index 0).
## Output contract → docs
Results are written into `BCC_FINANCIAL_ANOMALY.html` (Evidence & Analysis, inventory 20):
section 4 = Bai-Perron dating table + verdicts; section 2 = two-layer divergence tables.
Update `SESSION_MILESTONE_2026-09-01.md` with each new finding (Sep-4(31/32/33/37) pattern) and sync the
milestone to `G:/source-of-truth/` mirrors (hash-verify with a local copy). Nothing is sent;
BCC is excluded from all recipient lists.
*Second-opinion financial anomaly detection and formal regime-change dating for the BCC 990 series. Proven end-to-end Sep 4, 2026 on the 3.14t free-threaded stack (`venv-314t`), which was RETIRED and archived 2026-10-19. The commands below are re-pointed to the surviving interpreters; they have NOT been re-measured on 3.15t — treat their timings as historical.*
## Environment (re-pointed 2026-10-19)
| Interpreter (default) | `C:/Azazael/.venvs/py315t/Scripts/python.exe` (3.15.0rc3 free-threaded) |
| Interpreter (3.14-only fallback) | `C:/Azazael/.venvs/py314m/Scripts/python.exe` (3.14.5 GIL) — the ONLY sanctioned 3.14 runtime |
| torch | install a 3.15 build on py315t; otherwise `2.14.0+cpu` into py314m (**not installed there yet** — install on demand) |
| timesfm | `3.0.1` (ships `timesfm3` / `TimesFM3Forecaster`) — into whichever interpreter above carries torch |
| numpy / scipy | py315t ships `2.4.6` / `1.18.0`; py314m ships numpy only |
| statsmodels | `0.15.0` — **compiled extensions break under free-threading** (see trap below); not needed for these tools |
Verify the interpreter before running anything:
`C:/Azazael/.venvs/py315t/Scripts/python.exe -c "import sys; print(sys.version, sys._is_gil_enabled())"`.
Run: `C:/Azazael/.venvs/py315t/Scripts/python.exe timesfm_pilot_314t.py --metrics revenue expenses officer_comp`
(script filename keeps the historical `_314t` suffix; it is the same file)
Run: `C:/Azazael/.venvs/py315t/Scripts/python.exe azazael/scripts/bai_perron_breakpoints.py --series bcc_990_series.json --out bcc_bai_perron_results.json`
