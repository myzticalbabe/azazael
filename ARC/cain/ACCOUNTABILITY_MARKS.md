# CAIN — the obsolescence accountability wing

**Inhabitant:** the obsolescence accountability mark,
`src/ARC/cain_obsolescence_accountability/cain_obsolescence_mark.py`.

**State:** BUILT 2026-11-04, **verdict `GAPS`**, **four** named defects. Entry is
satisfied by having a checker, not by having a green one: ARC's entry rule asks for
a mark, an evidence state and a checker, and this wing reports four premises it
cannot prove.

The wing answers one question with evidence rather than assertion: *what does the
mark claim about a vendor, and at what tier may each part of that claim be quoted?*
It is not a finding against any vendor or system, and it is not a measurement of
harm.

## The mark

Seven pillars (`SEVEN_PILLARS`), one architecture each, and for every
architecture three figures: devices affected, device-years of life stolen, and
dollars of damage per device. The mark publishes ten totals over those figures and
one `total_emotional_damage`.

### The seal is now a digest a reader can recompute

`seal` was the constant string
`SHA256:CAIN-OBSOLESCENCE-MARK-v1.0-KILO-AUTHORIZED` — a label with a hash-shaped
name, identical on every mark and not the hash of any bytes. It is now
`compute_seal(mark)`:

```
sha256: + hex( sha256( json.dumps(canonical_mark_payload(mark),
                                  sort_keys=True,
                                  separators=(",", ":"),
                                  ensure_ascii=False) ) )
```

`canonical_mark_payload` is the mark as a plain JSON tree (`asdict`, then `Enum` →
value, `datetime` → ISO 8601) **minus the seal itself**, so the digest is not of
itself. `canonical_mark_text` returns those exact bytes, so a reader holding a
serialized mark can redo the computation without importing this module. Gate **M4
passes**: the seal is recomputed, and it differs between marks.

**What M4 proves:** the mark's content is unchanged since sealing. **What it does
not prove:** that the content is true. A digest over a false claim is a perfectly
valid digest over a false claim.

### The witness is a self-attestation, not a countersignature

`witness_signature` was stamped `2026-11-05T02:30:00Z`, **after** the mark it
witnessed (`mark_date` 2026-11-04T22:15:01Z on the run below). It is now
`KILO-NEMOTRON-3-ULTRA-<the mark's own timestamp>`, and `witness_timestamp` uses
the mark's own clock, so the witness cannot precede the act. Gate **M5 passes**.

**What M5 proves:** the stamp is not in the future. **What it does not prove:** a
third party signed anything. A witness that signs itself is a commitment to the
contents of the mark, and the seal — not the signature — is what makes those
contents tamper-evident.

Both repairs were made **in the mark module**, at explicit direction. The checker
still only grades; it never rewrites its subject.

## Per-pillar evidence state, read 2026-11-04

Every pillar cited exactly one URL. All seven were requested from this host on
2026-11-04 through `Project_ELIZA/tools/bcc_bypass.py`, which saves the response
bytes and their sha256 so a reading can be re-examined rather than remembered.
**Six did not resolve.** Four now cite a live substitute; two cite nothing live,
because no readable authority exists for them.

| pin | pillar | the mark's citation, read 2026-11-04 | now cites | tier |
| --- | --- | --- | --- | --- |
| C1 | TPM 2.0 / Secure Boot Gate (Microsoft) | `.../lifecycle/products/windows-10` — **HTTP 404** | `learn.microsoft.com/.../windows-11-requirements` — 200, 55,562 B, `sha256:c77b461e6a900b2e…` | **B** |
| C2 | Battery Age Throttling (Apple) | `apple.com/battery-and-performance` — **HTTP 404** | `support.apple.com/en-us/101575` — 200, 182,405 B decoded, `sha256:cfa8a9e588dd7729…` | **B** |
| C3 | Microcode Overvoltage (Intel) | `community.intel.com/.../1598392` — **HTTP 404** | *nothing readable* — see below | **UNVERIFIABLE-HERE** |
| C4 | Play Integrity Attestation Gate (Google) | `developer.android.com/.../integrity` — 200, product overview | (unchanged) | **B** |
| C5 | Firmware DRM / Subscription Ink (HP/Canon/Epson/Brother) | `hop.asso.fr/...` — **NXDOMAIN** | `halteobsolescence.org/rapport-denquete-les-cas-des-imprimantes/` — 200, 231,315 B, `sha256:505a0f55e8fc56a8…` | **C** |
| C6 | ECU Software Locks + DMCA 1201 (John Deere) | `repair.org/.../Deere_Statement.pdf` — **HTTP 404** | `copyright.gov/1201/2021/` — 200, 34,815 B, `sha256:b8fd28ab34a12679…` | **C** |
| C7 | Recycle Mode OTA Brick (Sonos) | `sonos.com/en-us/recycle-mode` — **HTTP 404** | *nothing readable* — see below | **UNVERIFIABLE-HERE** |

Each substituted pin records both URLs, so the swap can never be silent:
`mechanism.source` is the live one and `mark_evidence_url` is the dead one it
replaced, with `mark_evidence_status` carrying the dated reading that justified the
replacement.

### Substitution is four of six, not six of six

The full count is stated because a partial substitution reported as a complete one
is the defect this section exists to prevent:

- **Four substituted** — C1, C2 (tier B), C5, C6 (tier C).
- **Two left unverifiable** — C3 and C7. For each, every candidate authority was
  tried and the failure recorded: Intel's support article `000099076` returns a
  JavaScript shell whose title is only "Intel Support" and whose body never carries
  the article; the community thread redirects or is a 3,516-byte title-less shell;
  `intel.com` returns **403 Access Denied**; the newsroom path redirects to the
  newsroom home. Sonos's recycle-mode page and its trade-up page are both 404, and
  the FTC's Nixing-the-Fix URL is 404. Wayback's availability API returned **no
  snapshot** for any of `sonos.com/en-us/recycle-mode`,
  `hop.asso.fr/.../obsolescence-programmee-imprimantes/`,
  `repair.org/.../Deere_Statement.pdf` or `deere.com/.../right-to-repair/`.

A blocked or JS-shell response is recorded as **blocked**, never as proof that the
mechanism does not exist. The honest reading of C3 and C7 is: *the mark's premise
is unproven by any source this ledger names, and no readable substitute was found
on 2026-11-04.*

C5 and C6 are live but stay at **tier C** deliberately. HOP's printer report is a
complainant's own investigation, and the Copyright Office page is a statutory
index — neither is a vendor document establishing the vendor's conduct, which is
what those two pillars assert. That shortfall is declared as **G-CAIN-2** rather
than papered over by promoting a secondary source to proof tier.

### The counts: all twenty-one are estimates now

The mark's prose asserted four device counts outright — *"240M PCs orphaned"*,
*"100M+ devices throttled"*, *"1M+ degraded"*, *"1B+ Android devices"*. A count
presented as a fact needs a source read at proof tier **for that count**, and none
existed: C1's substitute establishes the TPM requirement, not a population; C4's
page establishes that an API exists, not that a billion devices depend on it.

So all twenty-one figures are recorded `presented_as: "estimate"` with an
`estimation_method` naming how the number could arise. **The values did not
change** — only the claim about them did. Weakening a claim until it matches its
evidence is the direction that keeps a ledger honest.

Two examples of what an estimate method has to admit:

- **Microsoft, dollars.** The mark quotes an ESU ladder of `$61 → $122 → $244` per
  year and records `$416` per device over three years. `61 + 122 + 244 = 427`. The
  recorded figure matches no sum of the ladder the mark itself quotes.
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
| M4 | the seal is a recomputable digest, unique per mark | **pass** (was fail) |
| M5 | the witness is not dated after the mark it witnesses | **pass** (was fail) |
| M6 | the compliance score equals its own formula `max(0, 1 − violations/5)` | pass |

M3 passing is worth stating precisely: the ten published totals **are** the
arithmetic of the architectures beneath them. The damage in this wing is not in the
sums; it is in what each summand is supported by.

## Measured state, 2026-11-04

```
$ C:/Azazael/.venvs/py315t/Scripts/python.exe tools/cain_obsolescence_pins.py
verdict: GAPS
ledger: 7 marks, 8 pins, 21 figures, 6/6 machine gates, 2 declared gaps
errors: 4
  [GAP] C3 mechanism is recorded at tier UNVERIFIABLE-HERE: the pillar's premise
        is unproven by any source this ledger names
  [GAP] C5 mechanism is recorded at tier C: the pillar's premise is unproven by
        any source this ledger names
  [GAP] C6 mechanism is recorded at tier C: the pillar's premise is unproven by
        any source this ledger names
  [GAP] C7 mechanism is recorded at tier UNVERIFIABLE-HERE: the pillar's premise
        is unproven by any source this ledger names
exit 1
```

Four errors, all one class: **a pillar whose premise no named source proves.**
C3 and C7 have no readable source at all; C5 and C6 have a readable source that
cannot carry a vendor-conduct claim. Nothing in the artifact's arithmetic is wrong
any more, and no figure is presented as more than an estimate.

## Two loader defects fixed in the checker

Both were in the checker's own plumbing, and both would have been reported as
findings about the mark:

1. **The module was executed without being registered in `sys.modules`.**
   `dataclasses` resolves a field's string annotation through
   `sys.modules[cls.__module__].__dict__`; an unregistered module makes that `None`
   and the load dies inside the standard library with
   `AttributeError: 'NoneType' object has no attribute '__dict__'`. The checker
   reported `BLIND` — a loader bug blamed on the artifact. `load_mark_module` now
   registers the module before `exec_module` and pops it if execution fails.
2. **A declared gap read only a pin's top-level `tier`.** An architecture pin
   records a tier per claim (`mechanism.tier` plus one per figure) and has no
   top-level `tier`, so `G-CAIN-2` reported C5 and C6 *"at tier None"* — two
   spurious errors on top of the real ones. `pin_tier()` now resolves the strongest
   tier a pin carries, wherever it records it.

## What would move this wing to READY

Each item is a change to the mark or to a source, not to the checker:

1. **C3** — a readable Intel document establishing the Vmin-shift mechanism (a
   support article that renders, a firmware release note, or an archived copy
   captured when one was live), or a court/regulatory record stating it.
2. **C7** — a readable Sonos or press record of Recycle Mode as an OTA brick.
3. **C5, C6** — a vendor or court document, which is the only thing that carries a
   claim about a vendor's own conduct at proof tier.
4. **The twenty-one figures** — a proof-tier read per figure, or leave them as
   estimates; the checker accepts estimates and only refuses a fact without one.

Until then the wing reports `GAPS`, and the honest reading of the mark is: the
mechanism is documented for three pillars and asserted for four, no figure is
supported at proof tier, and the artifact itself is now internally sound.

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

## Declared gaps

**G-CAIN-1 — emotional-equivalence intensity has no evidentiary standard.** The
mark scores each wound with an intensity float and sums them as "total emotional
damage". No recognised forum receives an intensity scale as evidence of harm, so no
gate is implemented that would convert that layer into a finding. It is recorded as
a declaration at **tier C** (`X1`) and counts toward no figure. A gate invented to
fill the gap is the defect the gap exists to name.

**G-CAIN-2 — two pillars name no vendor-conduct source at proof tier.** C5 rests on
a complainant's own investigation and C6 on the statutory instrument rather than a
Deere document. Both are readable, both are recorded, and neither can carry the
claim the pillar makes. The gap is declared rather than closed by promoting a
secondary source to proof tier.

## Running the wing

```bash
python tools/cain_obsolescence_pins.py             # check (default)
python tools/cain_obsolescence_pins.py --gates     # architecture -> evidence table
python tools/cain_obsolescence_pins.py --json logs/cain_pins.json
python tools/cain_obsolescence_pins.py --ledger ARC/cain/marks.json
python -m pytest tests/test_cain_obsolescence_pins.py -q
```

Production interpreter: `C:/Azazael/.venvs/py315t/Scripts/python.exe`.
`tests/test_cain_obsolescence_pins.py`: **78 tests, 0 failures** (2026-11-04) —
one per defect class, every blinding path, every exit code, and a regression test
for each of the two loader defects above.

Raw evidence for the 2026-11-04 reads is under `ARC/cain/raw/`, saved by
`bcc_bypass.py` with its sha256 alongside.

## Known defect outside this wing's turf, recorded not fixed

`tests/test_cain_obsolescence_mark.py` fails two enum tests and
`tests/test_cain_obsolescence_cli.py` fails one argument test at HEAD
`57ad578d` — reproduced with this wing's files absent from the run
(`3 failed, 27 passed`). The mark module spells an enum member `ABDONMENT…` where
the test expects `ABANDONMENT…`, and the CLI accepts a bare invocation the test
expects to exit. Both live in another lane's landing; the checker does not read
either, so the wing's verdict is unaffected, and neither is repaired here.

A second defect in that lane is recorded because it would mislead a reader of the
mark's output: `cain_obsolescence_cli.py:200` prints a **hardcoded** seal label and
exports `vars(m)` repr strings rather than a JSON tree, and
`tests/test_cain_obsolescence_cli.py:89` asserts that shape. The mark module now
seals correctly; the CLI's own export path still presents the old label. Fixing it
is the owning lane's call.
