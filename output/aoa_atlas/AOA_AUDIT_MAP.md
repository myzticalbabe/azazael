# AOA Audit & Map — Sep 2, 2026

_Source of truth: `azazael/src/AOA/` (in-repo, runnable). Canonical: `Desktop/AOA/` (newest gen). Historical: G: gen 1 / gen 2 + `archive/restored/AOA/`. Method: SHA-256 per .py file across all 5 locations + compile + full test suite + AST extraction of the registered arm map._

## 1. Provenance audit — who matches whom

| Comparison | Result |
|---|---|
| **repo `src/AOA` ↔ Desktop (canonical)** | ✅ **23/23 byte-identical** — the in-repo wiring is faithful to the newest generation |
| G: gen 1 ↔ G: gen 2 | ✅ 20/20 identical |
| `archive/restored/AOA` ↔ G: gen 1 | ✅ 20/20 identical — restored reference is faithful |
| Desktop-era ↔ G:-era (evolved files) | 7 expected: `libra_arm.py`, `build.py`, `build_disclosure.py`, `cli/__init__.py`, `gen_html.py`, `inject.py`, `rebuild_html.py` — newer generation, **not drift** |

**Verdict: zero unaccounted drift.** The only differences are generation evolution (Desktop superset is newest; archived generations retained) and test files that only exist in the Desktop/repo era (`conftest.py`, `test_cross_arm.py`, `test_benchmark_workflow.py`). Full machine-readable detail: `output/aoa_atlas/aoa_audit_2026-09-02.json`.

## 2. Code health

| Check | Result |
|---|---|
| `py_compile` (23 .py, Python 3.14.7) | ✅ all clean |
| `test_cross_arm.py` | ✅ PASSED — lifecycle INIT→READY 9/9→SHUTDOWN; cross-arm flow 4/4 (14 events); 17 EventBus events; 1.7 s |
| `test_benchmark_workflow.py` | ✅ PASSED — 9/9 steps, 0 failed; 8 arms through CrossArmRouter; 29 events; 0.3 s |
| pycache | ✅ 0 remnants after runs |

## 3. Arm map (extracted from source, sorted by priority)

| # | Arm | Category | Pri | Capabilities |
|---|---|---|---|---|
| 1 | **azazael** (Neural Mesh) | quartet | 10 | discover_worms, run_cluster, run_metacluster, get_status |
| 2 | **libra** (Legal Automation) | quartet | 9 | list_templates, generate_document, get_filing_types, calculate_fees, calculate_deadline, get_status, check_berks_rules, calculate_berks_fees, generate_berks_ifp, prepare_berks_filing, get_berks_calendar |
| 3 | **codex** (Video Engine) | quartet | 8 | render_video, render_mermaid, get_status |
| 4 | **pams** (Memory System) | support | 8 | record_event, get_memories, get_status |
| 5 | **eve** (AI Selector) | quartet | 7 | select_model, run_benchmark, run_inference, get_status |
| 6 | **kali** (Kali Toolchain) | support | 6 | get_status + **39 tool capabilities** (one per verified-installed Kali tool: recon 8, web 8, osint 8, security 4, cracking 3, intercept 3, network 1, ids 1, forensics 1, ai 1, media 1) |
| 7 | **perfmon** (Performance Monitor) | support | 6 | get_metrics, get_status |
| 8 | **agent_selector** (Agent Selector) | support | 6 | select_agent, get_status |
| 9 | **llama** (LlamaServer) | support | 5 | infer, get_status |

**Totals: 9 arms (4 quartet + 5 support) · 71 capabilities.**

### Kali arm (added 2026-09-02 — capability audit driven closure)

The Kali Toolchain arm (`arms/kali_arm.py`, registered `arm_id=kali`, priority 6, support) closes the
previously-documented gap: AOA had **no toolchain arm** while 39 Kali tools were verified installed in the
`kali-linux` WSL distro (typed `azazael-bin-*` skills, 46 documented). Design:

- **1 capability per tool** — `nmap`, `sqlmap`, `sherlock`, … each maps 1:1 to its installed binary;
  `get_status` reports WSL reachability + installed counts per family. Capability `category` = the tool's
  `azazael-bin-*` skill family (recon/web/osint/security/cracking/intercept/network/ids/forensics/ai/media).
- **WSL bridge** — execution via `wsl -d kali-linux -- bash -lc "<tool> <shlex-quoted args>"`; tool name is
  allow-listed from the registry dict, args are shlex-quoted (no free-form shell).
- **Dry-run-safe by default** — `execute()` with no payload args only runs a version probe (`--version`/`-V`/`--help`),
  returns `dry_run: True`; real tool runs require explicit `payload {"args": [...]}`. Mirrors the session's
  guarded-action discipline for Libra action modules.
- **Verified live:** INIT OK, `get_status` = 39 installed / 39 total, per-family counts match the WSL `command -v`
  probe set; safe no-args probe returns version line. Full capability table: see skill #1247 `aoa-kali-arm`.

### Wiring
- **Quartet** (p7–10): azazael → libra → codex → eve. Each has `initialize/execute/get_capabilities/shutdown` on `BaseArm`, registered via `@register_arm`.
- **Support** (p5–8): pams (memory), perfmon (metrics), agent_selector (routing), llama (inference endpoint), **kali (Kali toolchain over WSL)**.
- **Cross-arm flow** (verified by test): `get_metrics → record_event → discover_worms → run_cluster → render_mermaid` (PerfMon → PAMS → Azazael×2 → CODEX).
- **Routing**: `core/router.py` CrossArmRouter resolves capability → arm dynamically (runtime-derived; no static route table).
- **Integration points**: azazael → `src/CORE` (worm_registry, CLUSTERWORMS, METACLUSTER); codex → `src/CODEX/CODEX_Studio.py`; libra → `archive/restored/Libra_Desktop` (reference; arm delegates to the legal package by sys.path); kali → `wsl -d kali-linux` (WSL bridge).

## 4. Cross-checks

- Matches the corrected `aoa-architecture` skill (8 arms, 17 categories, 77 worms, Libra cap set, Eve `select_model`, llama `infer/get_status`, AgentSelector `select_agent`) — extracted from source, not memory.
- Supersedes the Aug 27 `aoa_mirror_drift.json` / `aoa_provenance.json` snapshots (those covered only g1 vs g2; this covers all 5 generations).