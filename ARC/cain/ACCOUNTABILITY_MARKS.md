# CAIN — the obsolescence accountability wing

**Inhabitant:** the obsolescence accountability mark,
`src/ARC/cain_obsolescence_accountability/cain_obsolescence_mark.py`.

**State:** BUILT 2026-11-04, **verdict `GAPS`**. Entry is satisfied by having a
checker, not by having a green one: ARC's entry rule asks for a mark, an evidence
state and a checker, and the marker returns `GAPS` with twelve named defects. The
wing is built *because* the checker reports them.

The wing answers one question with evidence rather than assertion: *what does the
mark claim about a vendor, and at what tier may each part of that claim be
quoted?* It is not a finding against any vendor or system, and it is not a
measurement of harm.

## The mark

Seven pillars (`SEVEN_PILLARS`), one architecture each, and for every
architecture three figures: devices affected, device-years of life stolen, and
dollars of damage per device. The mark publishes ten totals over those figures
and one `total_emotional_damage`.

The mark is graded as an artifact, not argued with. Two of its parts are not
evidence at all and the checker says so by name:

- `seal = "SHA256:CAIN-OBSOLESCENCE-MARK-v1.0-KILO-AUTHORIZED"` — a **label**, not
  a digest. It is identical on every mark, it is not the hash of any bytes, and a
  reader cannot recompute it. A seal a reader cannot recompute seals nothing.
- `witness_signature = "KILO-NEMOTRON-3-ULTRA-2026-11-05T02:30:00Z"` — dated
  **after** the mark it witnesses (`mark_date` 2026-11-04T22:15:01Z on the run
  recorded below). A witness stamped in the future is a forecast, not a witness.

Neither is repaired here. The seal belongs to the mark's owner; a checker that
rewrites its own subject is measuring itself.

## Per-pillar evidence state, read 2026-11-04

Every pillar cites exactly one URL. All seven were requested from this host on
2026-11-04. **Six did not resolve; one returned a page that does not carry the
figure it is cited for.**

| pin | pillar | mark's citation | read 2026-11-04 | premise tier |
| --- | --- | --- | --- | --- |
| C1 | TPM 2.0 / Secure Boot Gate (Microsoft) | `learn.microsoft.com/.../windows-10` | **HTTP 404** | UNVERIFIABLE-HERE |
| C2 | Battery Age Throttling (Apple) | `apple.com/battery-and-performance` | **HTTP 404** | UNVERIFIABLE-HERE |
| C3 | Microcode Overvoltage (Intel) | `community.intel.com/.../1598392` | **HTTP 404** | UNVERIFIABLE-HERE |
| C4 | Play Integrity Attestation Gate (Google) | `developer.android.com/.../integrity` | HTTP 200 — product overview, no population | **B** |
| C5 | Firmware DRM / Subscription Ink (HP/Canon/Epson/Brother) | `hop.asso.fr/...` | **NXDOMAIN** — host did not resolve | UNVERIFIABLE-HERE |
| C6 | ECU Software Locks + DMCA 1201 (John Deere) | `repair.org/.../Deere_Statement.pdf` | **HTTP 404** | UNVERIFIABLE-HERE |
| C7 | Recycle Mode OTA Brick (Sonos) | `sonos.com/en-us/recycle-mode` | **HTTP 404** | UNVERIFIABLE-HERE |

This ledger cites **only what the mark cites**. No substitute source is
introduced, because the mark's own citations are what is being graded: a ledger
that quietly swapped in a working URL would hide that six of the seven citations
are dead. Where a substitute is later justified, the pin must also record
`mark_evidence_url` (the citation it replaced) and `mark_evidence_status` (the
dated reading that justified replacing it), so a substitution can never be silent.

### The four counts asserted as fact

The mark's prose asserts four device counts outright — *"240M PCs orphaned"*,
*"100M+ devices throttled"*, *"1M+ degraded"*, *"1B+ Android devices"*. A count
presented as a fact needs a source read at proof tier. None of the four has one,
and the checker refuses the presentation rather than the number: the same figure
may stay in the mark if it is presented as an estimate with a named method.

The other three counts and all fourteen world-years and damage figures are
recorded as estimates; each carries the method the mark implies and the reason the
figure cannot be recomputed from the artifact. Two examples of what that means:

- **Microsoft, dollars.** The mark quotes an ESU ladder of `$61 → $122 → $244` per
  year and records `$416` per device over three years. `61 + 122 + 244 = 427`. The
  recorded figure matches no sum of the ladder the mark itself quotes, and no
  derivation is recorded.
- **Google, dollars.** Described only as *"Forced upgrade cost"*: no device price
  band, no trade-in value, no upgrade rate. A replacement price is not a damage
  figure without a counterfactual service life.

## Machine gates: the mark's own arithmetic

These need no ledger. They are answered by running the mark, and a total that does
not add up is a defect in the artifact rather than a matter of evidence.

| gate | tests | 2026-11-04 |
| --- | --- | --- |
| M1 | every pillar yields a mark with an identity and an architecture | pass |
| M2 | a mark's JSON is an object tree, not `repr` strings | pass |
| M3 | vendor totals equal the sum of the parts the mark publishes | pass |
| M4 | the seal is a recomputable digest | **fail** |
| M5 | the witness is not dated after the mark it witnesses | **fail** |
| M6 | the compliance score equals its own formula `max(0, 1 − violations/5)` | pass |

M3 passing is worth stating precisely: the ten published totals **are** the
arithmetic of the architectures beneath them. The damage in this wing is not in
the sums; it is in what each summand is supported by.

## Measured state, 2026-11-04

```
$ C:/Azazael/.venvs/py315t/Scripts/python.exe tools/cain_obsolescence_pins.py --gates
verdict: GAPS
ledger: 7 marks, 8 pins, 21 figures, 4/6 machine gates, 1 declared gaps
errors: 12
  [GAP] M4 seal-is-a-digest: CAIN-MARK-MICROSOFT-20261104 seals with
        'SHA256:CAIN-OBSOLESCENCE-MARK-v1.0-KILO-AUTHORIZED': a label, not a
        digest over any bytes; a reader cannot recompute it and it is identical
        on every mark
  [GAP] M5 witness-before-mark: CAIN-MARK-MICROSOFT-20261104 is witnessed at
        2026-11-05T02:30:00, after the mark it witnesses (2026-11-04T22:15:01)
  [GAP] C1 mechanism is recorded at tier UNVERIFIABLE-HERE: the pillar's premise
        is unproven by any source this ledger names
  [GAP] C1.affected_devices_count is presented as fact at tier
        UNVERIFIABLE-HERE: a count asserted as fact needs a source read at
        proof tier
  ... (C2, C3, C5, C6, C7 mechanism; C2, C3, C4 count)
exit 1
```

Twelve errors in three classes: **two artifact defects** (M4, M5), **six
unsupported premises** (every pillar whose citation is dead), and **four counts
presented as fact without a proof-tier read**. The count error for C4 survives
even though C4's page is live: a live product overview establishes that an API
exists, not that a billion devices depend on it.

## What would move this wing to READY

Each item is a change to the mark or to a source, not to the checker:

1. **M4** — replace the label seal with a digest over the serialized mark, in a
   form a reader can recompute.
2. **M5** — a witness stamp at or before `mark_date`; the current one is a name
   and a time, not a signature over content.
3. **Six dead citations** — either a live source in the mark, or a pin that
   records the replacement and the dated 404/NXDOMAIN that justified it (the
   checker accepts the second, but the pin then names both URLs).
4. **Four fact-counts** — a proof-tier read for each, or present them as what they
   are: estimates with a named method.

Until then the wing reports `GAPS`, and the honest reading of the mark is: the
mechanism is documented for one of seven pillars and asserted for six, and no
figure in it is currently supported at proof tier.

## Verdict vocabulary

Identical to `esquire/`, deliberately — one container, one vocabulary.

| verdict | exit | means |
| --- | --- | --- |
| `READY` | 0 | every machine gate holds and every figure is pinned at proof tier |
| `GAPS` | 1 | a machine gate failed, a figure is unpinned or unsupported, or the ledger is malformed |
| `INCOMPLETE` | 1 | no defect, but a pin's support was carried rather than read here |
| `BLIND` | 2 | the mark or the ledger could not be read — never a pass |

The checker never says "admissible" or "obsolete". It says what the mark asserts,
what that assertion rests on, and what it does **not** prove.

## Declared gap

**G-CAIN-1 — emotional-equivalence intensity has no evidentiary standard.** The
mark scores each wound with an intensity float and sums them as "total emotional
damage". No recognised forum receives an intensity scale as evidence of harm, so
no gate is implemented that would convert that layer into a finding. It is
recorded as a declaration at **tier C** (`X1`) and counts toward no figure. A gate
invented to fill the gap is the defect the gap exists to name.

## Running the wing

```bash
python tools/cain_obsolescence_pins.py             # check (default)
python tools/cain_obsolescence_pins.py --gates     # architecture -> evidence table
python tools/cain_obsolescence_pins.py --json logs/cain_pins.json
python tools/cain_obsolescence_pins.py --ledger ARC/cain/marks.json
python -m pytest tests/test_cain_obsolescence_pins.py -q
```

Production interpreter: `C:/Azazael/.venvs/py315t/Scripts/python.exe`.
`tests/test_cain_obsolescence_pins.py`: 70 tests, 0 failures (2026-11-04), one per
defect class plus every blinding path and every exit code.

## Known defect outside this wing's turf, recorded not fixed

`tests/test_cain_obsolescence_mark.py` fails two enum tests and
`tests/test_cain_obsolescence_cli.py` fails one argument test at HEAD
`57ad578d` — reproduced with this wing's files absent from the run
(`3 failed, 27 passed`). The mark module spells an enum member `ABDONMENT…` where
the test expects `ABANDONMENT…`, and the CLI accepts a bare invocation the test
expects to exit. Both live in another lane's landing; the checker does not read
either, so the wing's verdict is unaffected, and neither is repaired here.
