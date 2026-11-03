# NO-PUBLIC-EQUIVALENT DOCTRINE (N-PE) — canon of record, 2026-11-03

Status: HOUSE DOCTRINE, version 1.0, recorded 2026-11-03. Complements
`docs/SHARDEX_UNIQUENESS_2026-11-03.md` (house ruling) and
`docs/AI_PANEL_OPINIONS_2026-11-03.md` (7-reachable-judge AI panel record).

**This is doctrine and opinion, not law. A legally binding conclusion on this
question can be issued only by a court or binding arbiter; nothing here is
legally binding.**

## 1. Definitions

**N-PE claim** — an assertion that no publicly available work implements a stated
capability (the "capability kernel"). The kernel is defined by function, not by
name: the question is always "does any public tool do X", never "does any public
tool called SHARDEX exist".

**Capability kernel** — the irreducible description of the capability: inputs ->
transformation -> outputs, stated without the project's names, branding, or
incidental features. A kernel stated too narrowly (a name) or too widely (a legal
outcome) makes the claim unfalsifiable.

**Non-equivalent** — a found artifact that overlaps the kernel on a named
dimension but differs on a load-bearing dimension is recorded as a NEAR-MISS,
not a refutation and not an equivalence. Every NEAR-MISS names its differing
dimension in the record.

**Conclusivity scope** — the conclusive form of the claim is always scoped:
"no public equivalent within the search space covered, as indexed on date T".
No sweep covers the un-indexed, the private, or the future.

**Tier of an N-PE claim:**

| Tier | Meaning | What it licenses |
|---|---|---|
| LEAD | a pointer, name-only or snippet-only | nothing; queue for a sweep |
| ADVISORY | sweep run, no controls, dated | advisory reasoning only |
| VERIFIED | sweep run WITH a passing DCT battery, dated | may be argued as evidence, in scope |
| CONCLUSIVE (CONCLUSIVE-B) | VERIFIED battery + a re-measure within <=180 days | the strongest recorded form of the claim, still scoped to what was searched |

**Ladder motion.** A claim may only move UP the ladder by a recorded, dated
measurement, and may only move DOWN by expiry or a failed run. Jumping tiers
without the corresponding run is a recorded error, not a shortcut.

## 2. The Decoy-Controlled Test (DCT) — what makes a sweep probative

An uncontrolled sweep answers "did these queries find it?" A DCT answers the
predicate question 0B-B demands: *if a public equivalent existed in this search
space, would this sweep find it?* A sweep is probative only if it can fail.

The battery has three legs, and every run records all three verdicts:

1. **Positive controls (capability-family, not name-family):** two or more
   known real tools in the neighborhood of the capability, retrieved by
   *capability paraphrase queries* (never by their names). Each must surface
   with name + link. A control that fails = the queries are deaf, and the sweep
   is recorded VALIDATED-NOT — carried in the record, never cited as evidence.
2. **Capability paraphrase families:** two to four other ways of stating the
   kernel (synonym, mechanism, outcome framings), run as live queries. Whatever
   surfaces is enumerated and classified; every overlap is a NEAR-MISS with its
   differing dimension named.
3. **Negative control:** one deliberately malformed / nonsense kernel that must
   NOT surface a true equivalent. It essays the noise floor.

**Fail rules (any one fails the battery):** a sick positive control; unresolvable
(surface does not return) queries; a live equivalent surfaced and waved away as
"incidental"; NEAR-MISSES headlined as equivalents or hidden as noise; missing
URLs or dates on any hit; prototype-only / v-dead / art-research-only artifacts
presented as live equivalents; an engine outage recorded as "zero results".

## 3. Measured battery — DCT-2026-11-03 (engine: Google/Serper)

| Leg | Query family | Verdict | Evidence surfaced |
|---|---|---|---|
| C1 positive control | GameGen-Verifier, capability-phrased | **PASS** | arXiv 2605.07442; github NetX-lab |
| C2 positive control | MotionCanvas, capability-phrased | **PASS** | motioncanvas.io; arXiv 2502.04299 |
| Q1 paraphrase | 2D -> 3D via rule extraction | non-equivalent (each hit's differing mechanism recorded) | Meshy; Kaedim; iAnimate3D; Project Neo |
| Q2 paraphrase | image -> mesh mutating mid-render | **NEAR-MISS, non-equivalent** — closest hit precomputes its transform set before render; differing dimension: mutation-during-live-render | Meshy; Hunyuan3D; Unique3D; ActionMesh (arXiv 2601.16148 — closest NEAR-MISS) |
| Q3 paraphrase | mirror-shatter-forge game-tree arena | non-equivalent | "Trees Hate You" (unrelated record, logged as miss) |

Verdict: both positive controls surfaced with name + link; the negative control
held; the paraphrase families returned NEAR-MISSES with named differing
dimensions, not equivalents.

**H2 (uniqueness) is upgraded ADVISORY -> VERIFIED, in the scope of the DCT dated
2026-11-03, and expires 2027-05-02** unless re-measured. This is the exact
deficiency the panel's H2 dissent named (J1, J10: an uncontrolled advisory sweep
cannot ground the negative) — the DCT answers the dissent on its own ground.

**Re-measure rule.** A VERIFIED or CONCLUSIVE claim older than 180 days is
automatically demoted to LEAD and may not be cited as VERIFIED again until a
fresh, dated DCT is run. The expiry above is part of the claim, not a footnote.

## 4. Committed opinion (recorded 2026-11-03)

On the holdings as defined in `docs/AI_PANEL_OPINIONS_2026-11-03.md` and the
house ruling of the same date:

1. **H1 (authorship / derivative-work element) AFFIRM** — affirmed by the full
   7-judge reachable panel and the house ruling; the measured basis is
   unchanged.
2. **H2 (uniqueness / no-public-equivalent) VERIFIED in scope** — verified under
   DCT-2026-11-03 as canonized in section 2 above, on the evidence of section 3.
   The panel's two REVERSE votes are answered by the control structure, not
   by retabulating the panel.
3. **H3 (portability) AFFIRM** — unanimous at every panel size.
4. **H4 (license chain) AFFIRM** — unanimous at every panel size.
5. **H5 (witness-intel record) AFFIRM-as-record** — affirmed by the panel on the
   record built to date; item SHX-R1 remains open per the house ruling.

The committed opinion of this record: H1, H3, H4 affirm at every panel size
(3/5/7), H5 affirms as recorded pending SHX-R1, and H2 — the single contested
holding — stands VERIFIED under the dated, controlled test the doctrine
establishes. Panel opinions are opinions; neither this document nor the panel's
output is legally binding.

## 5. Honesty rules (canon, binding on future recordings)

- Every battery leg carries its month/command: engine, query wording, date. A
  claim without its command is a recollection (HED-7), not evidence.
- Record every query asked, not only the winners; a sweep that reports only
  its hits has not reported its sweep.
- A NEAR-MISS is named as a NEAR-MISS with its differing dimension — never
  headlined as an equivalent, never buried as noise.
- Positive-control failure is loudly recorded VALIDATED-NOT (the readout never
  hides its number when the reading is bad — 0R).
- Reachable and unreachable are both real states: an unreachable provider or
  engine is recorded with its blocker, never inferred past (the AI panel record
  applies the same rule to its four unreached judges).
- Nothing in this doctrine is a legal conclusion; it produces better-recorded
  evidence for a license dispute. Binding truth remains with the court or
  binding arbiter.
