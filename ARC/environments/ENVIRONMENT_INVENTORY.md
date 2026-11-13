# Environment inventory for ARC inclusion

Measured 2026-11-04 from the Windows production tree. Every count below is the
output of the command in the method section; none is recalled.

## What was looked for

Two classes of material decide an environment's verdict:

- **Esquire material** — anything whose name matches `*esquire*` or `*admissib*`.
  This is the admissibility apparatus: canon article E-11, the instrument, the pin
  ledger, the pin checker. An environment holding a *newer or primary* copy of any
  of these is a candidate for inclusion.
- **CAIN material** — anything whose name matches `*cain*`. This is the material
  for the queued `cain/` wing (accountability mark, planned obsolescence), and it
  is the only arc-relevant asset the non-Windows environments actually hold.

## Method

Per root, full depth for Esquire material and depth <= 2 for CAIN:

```bash
find <root> \( -iname '*esquire*' -o -iname '*admissib*' \) | wc -l
find <root> -maxdepth 2 -iname '*cain*' | wc -l
```

WSL roots were reached through the `//wsl$/...` UNC paths. A first attempt at an
unbounded `find` across all roots at once **timed out at 120 s** (the UNC walk, not
a finding); the probe was re-run one root at a time with a wall bound, and the
per-root results below are those runs.

## Results

| environment | root | Esquire matches | CAIN matches | verdict |
| --- | --- | ---: | ---: | --- |
| Windows production | `C:/Azazael/azazael` | 4 (host) | present | **INCLUDED** |
| WSL Kali | `//wsl$/kali-linux/root/azazael` | 0 | 5 | **DEFERRED** |
| WSL Ubuntu | `//wsl$/Ubuntu-26.04/root/azazael` | 0 | 40 | **DEFERRED** |
| G: archive | `/g/AZAZAEL` | 0 | 4 | **DEFERRED** |
| G: source of truth | `/g/AZAZAEL_SOURCE_OF_TRUTH` | 0 | 7 | **DEFERRED** |
| G: Ubuntu staging | `/g/AZAZAEL_UBUNTU` | 0 | 0 | **EXCLUDED** |
| G: standalone build | `/g/AZAZAEL_Standalone` | 0 | 1 | **DEFERRED** |

### Verdict definitions

- **INCLUDED** — holds the apparatus itself (the host: canon article, instrument,
  pin ledger, pin checker).
- **DEFERRED** — holds ARC-relevant material but none of the admissibility
  apparatus; queued for the `cain/` wing rather than copied now.
- **EXCLUDED** — holds nothing that satisfies the entry rule.

## Findings

1. **The admissibility apparatus is Windows-only.** Zero Esquire matches in all six
   non-production environments, at full depth. The pins exist in exactly one place:
   `ARC/esquire/` in the production tree. Anything said about the wing being
   "in the canon everywhere" is false today.
2. **The CAIN material is duplicated, not developed.** Both WSL roots and two G:
   trees hold `CAIN_DELIVERABLE_MATH_2026-06-05.md` and `CAIN_injected.html`;
   `G:/AZAZAEL_SOURCE_OF_TRUTH` additionally holds
   `scripts/cain_video_pipeline_demo.py` and the two `azazael-cain-*` skills;
   `G:/AZAZAEL_Standalone` holds `CAIN_Analyzer_314t.bat`. These are the inputs to
   the `cain/` wing, and the wing is queued precisely because none of them carries
   a checker.
3. **`G:/AZAZAEL_UBUNTU` is empty of both.** Excluded, not deferred: staging with
   no distinguishable content adds a drift surface and no evidence.

## Why nothing is copied yet

The ARC entry rule refuses an inhabitant without a checker. Copying the pin ledger
into five environments would create five copies that can silently drift, which is
the failure the checker exists to detect — and `tools/esquire_pins.py` resolves its
ledger relative to the repository root, so a copy outside the tree is not checked
by anything. Portability is a later step and it belongs to the checker, not to the
documents.

## What would change a verdict

- An environment holding a **primary** text not present in Windows (for example a
  fetched *Bullcoming* opinion) moves to candidate: the pin's tier could rise only
  if that text were read there.
- An environment holding a **newer** `pins.json` than the production tree outranks
  this one, and the production ledger would be the copy to reconcile.
- `cain/` gains a checker: the five environments holding CAIN material become
  sources for that wing's evidence, not for the admissibility wing.

## Limits of this measurement

- **Filename-based, not content-based.** A document about admissibility named
  `evidence_rules.md` would not match. No content grep was run across the corpora.
- **UNC reads can skip.** `find` errors were discarded (`2>/dev/null`); a directory
  the share refused would not appear as a zero, it would simply be absent. The
  zero counts are therefore "no match among the entries `find` could read".
- **CAIN depth is capped at 2.** A CAIN file deeper than that in any root is not
  counted. Esquire counts are full depth.
- **No BCC/AOA material was assessed.** Those trees hold investigation records, not
  an accountability apparatus; they are out of scope for this inventory.
