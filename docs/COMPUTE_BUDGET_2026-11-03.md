# ONE COMPUTE BUDGET, REPLACING 114 EQUIPMENT JUSTIFICATIONS

**Date:** 2026-11-03 · **Scope:** all 33 funding profiles under
`Project_Scribe/profiles/` · **Status:** recommendation, not an executed change —
the profiles are generated artefacts and were not hand-edited.

---

## 0. What this document replaces

The 33 profiles carry **126 `equipment_justification` rows**, collapsing to **114
distinct strings**. Every application the tree can emit copies one of them. They
are not budgets; they are template fragments concatenated with a project name, and
most of them describe hardware this project does not have.

This document replaces all 114 with **one costed budget** — owned versus rented,
priced at published rates — plus a small set of sentence templates for the cases
where a funder's form demands prose.

## 1. The measurement

Run over `Project_Scribe/profiles/*_profile.json`, reading every
`overrides.<funder>.equipment_justification`:

| property | count |
| --- | --- |
| profiles scanned | 33 |
| distinct justification strings | 114 |
| total justification rows (one string reused across funders) | 126 |
| rows naming an **RTX 4090** | 83 |
| rows naming an **A100** | 33 |
| rows naming an **H100** | 4 |
| rows naming **DGX Sparks** | 2 |
| rows naming the hardware the project actually documents (**Intel Arc 140T**) | **0** |
| rows that say "no GPU" or "minimal" | 1 |
| rows with UTF-8 mojibake (`1Ã—`, `â‚¬50K`, `Â£12.5K`) | 16 |

The hardware the tree documents, in `Project_CRADLE/HARDWARE.md` and
`Project_Nurse_Ratchet/HARDWARE.md`:

```
| **iGPU** | Intel Arc 140T (8 GB shared VRAM) |
| memory   | 32 GB LPDDR5x-8533                |
| CPU      | Intel Core Ultra 9 285H           |
| OS       | Windows 11 Pro 24H2               |
```

A discrete GPU is not documented anywhere in this repository's hardware references.
`grep -ril "RTX 4090" --include=*.md` matches only the funding profiles themselves,
the funding register, and the generated GitHub Secure OSS applications — that is,
the claim cites only itself.

**This is the defect in one line: 0 of 114 justifications describe the machine the
project says it runs on, and the one repeated 83 times describes a card the project
does not own.**

## 2. Why it is worse than untidy

1. **It is checkable, and it fails on check.** A reviewer opens the repository,
   sees standard-library Python and an `HARDWARE.md` naming an iGPU, and reads a
   request for an RTX 4090 "for integration testing". That single inconsistency
   costs the application credibility on every other number in it.
2. **It is a category error, not an exaggeration.** "RTX 4090 for stdlib-only
   orchestration" (the CRADLE row, verbatim) asks a GPU to accelerate code with no
   GPU path. The same shape appears in "A100 for OSPO integration", "RTX 4090 for
   SBOM signing", "RTX 4090 for AI-assisted orchestration logic verification".
   Signing a manifest and verifying orchestration logic are CPU work.
3. **The largest asks are the least supported.** Two rows request
   **30,000 H100 80GB GPU-hours plus 2× DGX Sparks**. At the observed H100 median
   of USD 3.25/GPU-hour, 30,000 hours is **USD 97,500 in compute before the DGX
   hardware** — larger than several of the grants it is attached to. No row states a
   training objective that would consume it.
4. **Cloud prices are named but never costed.** 22 rows name AWS P4de, EC2 P5,
   Azure NDv4, Trainium/Inferentia or Codespaces. None states an hourly rate, an
   instance count or a month count, so no figure in those rows can be checked or
   totalled.
5. **The mojibake is a disclosure risk.** 16 rows contain `1Ã—`, `â‚¬`, `Â£` — UTF-8
   decoded as latin-1 somewhere upstream. Pasting that into a funder's form looks
   like a copy from an unmaintained pipeline, because it is one.

## 3. The one budget

Prices are **published on-demand medians observed 2026-11-03**, converted at an
assumed EUR/USD 0.92 and rounded. They are planning rates; re-quote at submission.

| item | owned | rented | rate (EUR) | qty | EUR | purpose |
| --- | --- | --- | --- | --- | --- | --- |
| Intel Core Ultra 9 285H | ✔ | | 0 | — | 0 | already in hand; CPU path |
| Intel Arc 140T, 8 GB shared | ✔ | | 0 | — | 0 | already in hand; local smoke tests |
| 32 GB LPDDR5x-8533 | ✔ | | 0 | — | 0 | already in hand |
| Windows 11 Pro 24H2 workstation | ✔ | | 0 | — | 0 | already in hand |
| A100 80GB | | ✔ | 1.60/h | 700 h | 1,120 | runtime-compatibility testing (vLLM, llama.cpp) |
| L40S | | ✔ | 1.20/h | 250 h | 300 | lower-cost serving tests |
| H100 SXM | | ✔ | 3.00/h | 100 h | 300 | bounded test against the largest model |
| CI / CPU runner | | ✔ | 0.02/min | 8,000 min | 160 | interpreter × OS matrix |
| Storage and egress | | ✔ | — | — | 120 | weights and images during portability work |
| Buffer, 25% on rented hours | | ✔ | — | — | 500 | provider price moves, re-runs |
| **total rented** | | | | | **2,500** | |
| **total owned, cost to a grant** | | | | | **0** | |

**Equipment purchase: €0.** Owned hardware costs the funder nothing because it is
already owned; charging a grant for it would be double-billing, and charging for an
upgrade the work does not need is the defect this document exists to stop.

Rate basis, so a reviewer can check it: A100 ≈ USD 1.76/GPU-hour median, L40S ≈
USD 1.29, H100 ≈ USD 3.25 (provider-comparison indices read 2026-11-03; the spread
across providers is wide — H100 ranges roughly USD 1.49–6.98 — which is exactly why
a single quoted rate must be named rather than implied).

## 4. The replacement text

Four sentences cover every project class in this tree. Use the one that is true; do
not blend them.

**A — no compute need (the default for every stdlib-only project):**

> No equipment is requested. This project is standard library only and runs on the
> maintainer's existing workstation (Intel Core Ultra 9 285H, Intel Arc 140T iGPU,
> 32 GB RAM). Any release run against a hosted model is billed separately and is not
> part of this request.

**B — rented serving hours, no training:**

> No equipment is purchased. Testing against OpenAI-compatible model servers
> (vLLM, llama.cpp) uses rented GPU-hours at published on-demand rates: €2,500 for
> 700 A100-hours, 250 L40S-hours, 100 H100-hours, CI minutes and storage. The
> project has no training step.

**C — genuine training, with a stated objective and a stated quantity:**

> Training is required for one stated objective: <the objective>. Budgeted as
> <N> GPU-hours of <type> at <rate>, totalling <amount>, with the evaluation run
> (holdout, seed, metric) costed separately at <N> hours. If the objective is
> dropped, this line is dropped with it.

**D — inference only under a funder's programme that supplies credits:**

> This request uses the programme's own compute allotment. No equipment and no
> rental is requested; a local model on the maintainer's workstation is used for
> development.

Class C is the only one that may name an A100 or H100, and only with an objective,
a quantity and a rate on the same line. **No template may name a device the project
does not own as if it were being purchased** — that is what produced the 83 rows.

## 5. Mapping

| project class | template | examples in this tree |
| --- | --- | --- |
| stdlib-only orchestration, verification, audit | A | CRADLE, FLAMING SWORD, SHARDEX |
| wraps a hosted or local model, no training | B | FLAME, MultiProviderInference |
| has a real, bounded training objective | C | none established today — see §6 |
| funder supplies compute | D | programmes with an allotment |

## 6. When C is allowed, and what has to exist first

A training line is permitted only when the repository can show all four:

1. a training script that runs to completion on a small input;
2. a named dataset with a licence and a size;
3. a holdout and a metric, fixed before the run;
4. a prior run's wall-clock and GPU-hour figure, so the quantity is measured rather
   than imagined.

No project in this tree presently shows all four. Until one does, **every profile
uses A, B or D**, and a 30,000-H100-hour line has no route into any application.

## 7. Limits of this document

- It does not re-price what a funder will actually pay; it prices what the work
  needs, which is the part this tree controls.
- It does not fix the profiles. They are generated; the template and the generator
  are the fix, and editing the 114 strings by hand would leave the generator
  producing them again — the same defect reappearing on the next run.
- The euro conversions are an assumption (0.92), stated so that a reviewer can
  redo them.
- "Not documented in this repository" is not the same claim as "does not exist on
  the applicant's desk". Where a device exists but is undocumented, the profile is
  still wrong to claim it as a purchase without saying so.

## 8. Re-measure

Re-run the counts in §1 after any change to the profile generator, and re-quote GPU
rates at submission — the 2026-11-03 figures are cached readings. **Expiry: 2026-12-03.**
