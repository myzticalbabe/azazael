# HYPER-EDGE custom protocol work — assessment (measured 2026-11-12)

## What hyper-edge already is (the leg protocol)

`tools/deep_dive.py` runs 5 forensic legs; `hyper_edge` fans out over
8 auditors in-process on 3.16t with per-leg timeout (300s), per-auditor
budgets (`BUDGET_S`), 5 recorded states (ok/empty/skipped/error/timeout),
a strictness ratchet (latches after 3 clean, shrink-only), and
`leg_ledger` auditing the previous report. Per HED-8, a new capability
joins as a leg: one row in `HYPER_EDGE_TOOLS`, one knob in
`config/defaults.json`, one `BUDGET_S`. That is the whole integration
surface — ~20 lines across 3 files. `fusion_status.py` already speaks
the shape (`--json`, exit codes); it still needs `BUDGET_S` + knob.

## Transport facts (measured this session, not assumed)

- `.wslconfig`: `networkingMode=mirrored` — Windows and WSL share
  loopback. TCP crosses the boundary both directions TODAY (the MCP
  gate proves WSL→Win :8765 every run).
- 9P bulk tax: 100MB write inside VHD 0.1s vs via `/mnt/c` 1.3s
  (13x). 9P carries BOTH directions (`\\wsl$` and drvfs); it is
  load-bearing and irreplaceable inside WSL2.
- `sshd` present in both distros (config work, not install work).
- No "8p" exists anywhere in the tree (only `8px` pixel hits). A custom
  filesystem protocol would be greenfield kernel-class work.

## Three scopes, priced

A. LEG-PROTOCOL (small, paved). Add the fusion auditor as the 9th leg:
   `BUDGET_S` on `fusion_status.py`, knob, ratchet covers it. DO — it
   is the HED-8 path and makes fusion estate part of every deep dive.

B. TRANSPORT-PROTOCOL (medium, greenfield-lite). SSH lane transport:
   per-distro `sshd` on allocated loopback ports (mirrored mode shares
   127.0.0.1, so Kali/Ubuntu/Windows-OpenSSH must not collide), key-only
   auth, tool traffic over exec channels instead of `\\wsl$`/drvfs.
   Identical on WSL and BM — migration-proof. DO after BM is live;
   premature now (BM has no address yet).

C. FILESYSTEM-PROTOCOL "8p" (do not build). Replacing 9P means
   reimplementing served-file semantics the kernel already provides,
   and WSL2 mandates 9P regardless — zero payoff inside WSL2, all cost.
   NEVER; the BM runbook is the severance path, not a protocol.

## Sequencing

A now (one commit, ratchet-covered). B at first BM boot (same week as
GO-MOVE if BM proves out). C never — cite this doc when it resurfaces.
