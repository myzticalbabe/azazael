# Drift alarm - 2026-10-06 06:00:01

**Verdict: DRIFT**

| signal | status | detail |
|---|---|---|
| `baseline-contract` | FAIL | 3 contract violation(s) across win-313tools, ubuntu |
| `environment-shape` | FAIL | win-main: 637 -> 655 (+18); win-313tools: 127 -> 158 (+31); ubuntu: 300 -> 420 (+120) |
| `sync-integrity` | FAIL | OUT OF SYNC | failing: docs_g, tests, tests_kali, scripts, scripts_kali |
| `disk-headroom` | ACCEPTED | C: 18G free (floor 40G)  [ACCEPTED since 2026-09-20] |
| `adaptation-stack` | OK | 8/8 import free-threaded |

## Environment shape

| environment | distributions |
|---|---:|
| kali | 1009 |
| ubuntu | 420 |
| win-313tools | 158 |
| win-314t | 193 |
| win-interp | 149 |
| win-main | 655 |
