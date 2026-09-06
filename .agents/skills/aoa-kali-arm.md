---
name: aoa-kali-arm
description: AOA Kali Toolchain arm (arm_id=kali, v1.0.0) — 39 verified Kali Linux tools over WSL mapped 1:1 to AOA capabilities (recon, web, osint, security, cracking, intercept, network, ids, forensics, ai, media), dry-run-safe WSL bridge, per-tool azazael-bin-* skill cross-reference. Load before invoking Kali tools through AOA.
metadata:
  category: architecture
  projects: aoa, azazael, kali
  auto_load: false
  date_created: 2026-09-02
---

# AOA Kali Toolchain Arm — Capability Index

## Identity

| Field | Value |
|-------|-------|
| Source | `azazael/src/AOA/arms/kali_arm.py` (in-repo, runnable) |
| Registration | `@register_arm(arm_id="kali", category="support", priority=6)` |
| Added | 2026-09-02 (closes the documented no-toolchain-arm gap; AOA went 8 arms/31 caps → **9 arms/71 caps**) |
| Edit convention | CRLF line endings (matches AOA source tree) |

## Why this arm exists (audit)

The AOA capability audit (2026-09-02) found AOA had **zero toolchain capability** while 39 Kali tools were
verified installed in the `kali-linux` WSL distro (`command -v` probe) and documented as `azazael-bin-*` skills
(46 typed skills; 7 are venv/pip-only: osintgram, open-webui, llama-server, vllm, sglang, seclists, open-webui —
excluded from the install count, listed in the tool dict for status reporting).

## Capability index (39 tools, 1 capability each + get_status)

Family (capability `category`) mirrors the `azazael-bin-*` skill category. Family column = the skill's metadata category.

| Family | Tools (capability name = tool) |
|--------|--------------------------------|
| recon (8) | `amass` `dnsx` `masscan` `naabu` `nmap` `nuclei` `rustscan` `subfinder` |
| web (8) | `dirb` `feroxbuster` `ffuf` `gobuster` `joomscan` `nikto` `sqlmap` `wpscan` |
| osint (8) | `exiftool` `ghunt` `maigret` `phoneinfoga` `sherlock` `social-analyzer` `spiderfoot` `theHarvester` |
| security (4) | `gitleaks` `syft` `trivy` `trufflehog` |
| cracking (3) | `hashcat` `hydra` `john` |
| intercept (3) | `bettercap` `mitmproxy` `responder` |
| network (1) | `tshark` |
| ids (1) | `snort` |
| forensics (1) | `foremost` |
| ai (1) | `ollama` |
| media (1) | `ffmpeg` |

Each per-tool `azazael-bin-*` skill documents the tool's canonical invocations — the arm is the AOA-side entry
point; the bin skill is the per-tool reference.

## Execution contract (safety)

- **Dry-run-safe default:** `execute("<tool>")` with no payload args = version probe only (`--version` / `-V` /
  `--help`), returns `dry_run: True`. No scanning, no network action.
- **Real runs:** `payload={"args": ["-sV", "127.0.0.1"]}` → tool name allow-listed from the registry dict, args
  shlex-quoted, executed as `wsl -d kali-linux -- bash -lc "<tool> <args>"` (120 s timeout, stdout capped 2000).
- **get_status** reports WSL reachability, installed counts (39/39 expected on this machine), per-family counts.
- Mirrors the session's guarded-action discipline for Libra action modules: never pass free-form shell input.

## Verified state (2026-09-02)

- `test_cross_arm.py` PASSED — 9 arms discovered, lifecycle INITIALIZE 9/9, 71 total capabilities, TEST 1 + TEST 2 green.
- `test_benchmark_workflow.py` PASSED — all 9 arms through CrossArmRouter, 29 events, 0 failures.
- WSL `kali-linux` reachable; nmap etc. confirmed at `/usr/bin/` (Nmap 7.99).
- **Real payload path VERIFIED END-TO-END (2026-09-02):** `execute("nmap", {"args": ["-sV", "-p", "1-1024", "127.0.0.1"]})` → status ok, returncode 0, `dry_run` flag absent, full Nmap 7.99 scan output (host up, 1024 ports probed — all closed/reset on the fresh WSL loopback, expected); `execute("sqlmap", {"args": ["--version"]})` → `1.10.6#stable`. The no-args version-probe path returns `dry_run: True`; the payload path provably reaches the tool. (Elapsed 0.3 s/0.14 s — loopback.)
- Files: `arms/kali_arm.py` (new), `cli/aoa_cli.py` + both tests gained `import arms.kali_arm` (5 CLI import blocks).

## Related

- `aoa-architecture` (#1223) — 9-arm / 71-capacity map
- `azazael-bin-*` (46 skills) — per-tool invocation references
- `output/aoa_atlas/AOA_AUDIT_MAP.md` — updated arm map + resolved KALI-CAP-GAP finding
- `aoa-artifact-cross-check` (#1250) — proves the arm map (incl. kali s6/40) is consistent across registry ↔ audit map ↔ diagrams ↔ audit JSON
- `background-sweep-resilience` (#1251) — crash-resilient long-run patterns for wide tool sweeps (per-file try/except, resume-from-crash-point)
- `builder-status-discipline` (#1252) — producer-status thinking applies to toolchain wrappers as much as HTML builders