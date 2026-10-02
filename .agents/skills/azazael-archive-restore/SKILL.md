---
name: azazael-archive-restore
description: >-
  Archive-restore provenance pattern — restoring old-only functionality from the
  G: historical archive as reference copies: copy-don't-move, generation labels,
  byte-verification (robocopy + SHA-256 + cmp), inherited-defect documentation
  in the provenance README, and post-restore sanity passes (syntax check,
  safe-import list, guarded dry-run for action modules).
metadata:
  category: process
  project: azazael
  auto_load: false
  version: 1.0.0
  created: 2026-09-01
---

# Archive-Restore Provenance Pattern

Restoring "old-only" functionality from G: (or Desktop) into the repo as a
**reference copy** — never as live code — while preserving provenance,
verifying byte-fidelity, and documenting inherited defects so future sessions
don't re-derive them. Proven in Session 28 (2026-09-01) restoring `archive/restored/`
(AOA gen 1, Libra gen 1, Libra_Desktop BCC superset, META Z-modules).

## Core Rules

1. **Copy, don't move.** Sources on G: and Desktop stay untouched — the
   historical archive is read-only per the standing directive. Robocopy /MIR-free
   plain copy; verify the source still exists after.
2. **Reference-only, labeled by generation.** Restored trees live in
   `archive/restored/<Name>_<gen>/`, never wired into imports. Document which
   generation each copy is (gen 1 = `G:\AZAZAEL`, gen 2 = `G:\AZAZAEL_SOURCE_OF_TRUTH`,
   newest = Desktop) and why that generation was chosen.
3. **Byte-verify everything.** Three layers: robocopy report (0 failed / 0
   mismatched), spot SHA-256 MATCHes against the source, and generation diffs
   (identical / differ / new-only file counts) so the copy's relationship to
   other generations is known.
4. **Document inherited defects, don't fix them.** A restored file that fails
   to compile/import in the repo's Python is usually byte-faithful to a source
   that fails identically. Record it in the README's "Known caveats" — fixing
   it would make the reference copy diverge from the original it documents.
5. **Provenance table in the README.** Source path, generation, file counts,
   exclusions, verification results, and the "why old-only" rationale.

## Procedure

### 1. Survey the source before copying

- `du`-style sizes lie: exFAT on G: uses 128 KB clusters, so a "26 MB" tree may
  be ~1 MB logical. Use logical (copied) size, not cluster size, for decisions
  and reporting.
- List files by size to design exclusions: render noise (`.mp4`, `output/test_video/`,
  `graphify-out/`) and `__pycache__/` are excluded by default; **real data
  (e.g. BCC sweep CSVs) is kept** even when large.
- Check what a side-effect scan shows BEFORE importing anything (see Sanity
  passes).

### 2. Copy with robocopy

```bash
cd /c/Users/clint/azazael
MSYS_NO_PATHCONV=1 robocopy "C:\Users\clint\Desktop\Libra" \
  "C:\Users\clint\azazael\archive\restored\Libra_Desktop" /E \
  /XD __pycache__ "output\test_video" /NJH /NJS /NP
```

- **CRITICAL — MSYS path bug:** under `MSYS_NO_PATHCONV=1`, POSIX paths like
  `/g/...` are passed literally and robocopy roots them at the current drive
  (creating `C:\g\...` strays). Always pass native `G:\` / `C:\` destinations
  to robocopy, and check the report's destination column.
- The report prints "Files: N ... 0 Failed, 0 Mismatched" — that is the
  byte-fidelity claim. Record it.

### 3. Verify byte-fidelity

```bash
# spot hashes vs source
sha256sum archive/restored/Libra_Desktop/libra/jurisdictions/pa/berks/bcc_parser.py \
  Desktop/Libra/libra/jurisdictions/pa/berks/bcc_parser.py
# byte-compare a suspicious file
cmp archive/restored/Libra_Desktop/MILESTONE.py Desktop/Libra/MILESTONE.py && echo IDENTICAL
# .py count parity
find archive/restored/Libra_Desktop -name '*.py' | wc -l   # must equal source's count
```

- 5/5 spot MATCH + full .py count parity is the bar.
- Generation diff (identical/differ/new-only) comes from `hashdeep`-style
  cross-comparison of the restored tree vs each other archived generation —
  record the totals in the README so the lineage is explicit.

### 4. Sanity passes (post-restore)

Layered, safe-first — **never execute action modules bare**:

1. **Syntax:** `python -m compileall <tree>` — safe, no execution. Expect
   ~100% clean; investigate every failure (see Inherited defects below).
2. **Safe imports:** scan for import-level side effects first (module-level
   `requests`/`socket`/`smtplib`/`subprocess`/`os.unlink`/`webbrowser` calls),
   then import only side-effect-free modules.
3. **Guarded dry-run for action modules:** patch `socket`, `requests`,
   `smtplib`, `subprocess`, `webbrowser`, `os.unlink` to BLOCK and import in
   isolated per-module subprocesses with timeouts. Module-level blocked attempts
   are findings: document them as "never import outside its pipeline."

> **Harness gotcha:** block `subprocess.Popen` with a *class*, not a function —
> `asyncio.windows_utils` subclasses Popen and crashes if you replace it with a
> plain function (3 false positives in Session 28).

### 5. Document in the provenance README

`archive/restored/README.md` sections:

- **Source & provenance** — table: subfolder | source path | generation |
  files/size/.py count. Note why the generation was chosen (superset content).
- **What was excluded** — render noise, `__pycache__`, regenerable artifacts.
- **Why these are "old-only"** — cross-ref the generation diff (Phase 9) and
  which current-codebase references existed (skills, docs).
- **Verification** — robocopy results, spot hashes, byte-identical checks,
  "sources untouched" restated.
- **Known caveats** — every inherited defect, with exact reproduction (which
  byte/line, which interpreter version), proof it's inherited (byte-identical
  to source), impact (does it break the package?), and the remedy **without
  altering the source copy**.

### 6. Record in the session milestone

Session Memory entries: restore executed (N files / size / 0 failures),
verification results, inherited defects found, harness bugs encountered, and
the "copy-only, sources untouched" restatement.

## Inherited-Defect Canon (Session 28)

- **`Libra_Desktop/MILESTONE.py`** — `0x97` byte (Windows-1252 em-dash), no
  encoding declaration → `compileall` rejects it on Python 3.14.7. Byte-identical
  to Desktop source (fails identically). Standalone root script, never imported
  by the `libra` package → no operability impact. Remedy: `# -*- coding: cp1252 -*-`
  locally, never on the restore.
- **`cain/capture.py` + `cain/hevc.py`** — attempt `os.unlink` at import time.
  Genuine, expected (encoder pipeline cleanup); never import outside that
  pipeline.

## Anti-Patterns

- Moving (not copying) from G: — destroys the archive.
- Fixing inherited defects in the restore — destroys the reference copy.
- `MSYS_NO_PATHCONV=1` + POSIX `/g/...` robocopy destinations — creates
  `C:\g\...` strays; verify the destination column.
- Trusting `du` cluster sizes for exFAT G: — always report logical size.
- Importing action modules bare to "test" them — always guard or exclude.

## Related Skills

- `azazael-separation` — extraction/provenance thinking for sub-projects
- `azazael-dedup` — hash comparison when generations overlap
- `azazael-error-prevention` — anti-pattern catalog (same class of process bugs)
- `azazael-testing` — syntax/integration verification conventions
- `azazael-kali-graph-protocol` — sibling protocol for the Kali mirror/scan