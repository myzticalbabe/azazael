# Deere & Company: what the primary record establishes

**Matter:** FTC v. Deere & Company, No. 3:25-cv-50017 (N.D. Ill., W.D.)
**Document:** ARC wing `deere/` — narrative over `claims.json`
**Captured and read:** 2026-11-05
**Sources:** 8 captures, 5 at tier A, 3 at tier B. Every digest in the provenance
table was recomputed from the bytes on disk at the time of writing.
**Claims:** 35 — 33 SUPPORTED, 1 UNSUPPORTED (D34), 1 BLOCKED (D35). Both of the
latter are declared with a reason, not silently dropped.

This document states only what a captured document says. Where a proposition is
pleaded but not found, it is labelled pleaded. Where a document is absent, the
proposition is not made at all. The distinction is the entire point: a complaint
alleges, an order commands, a press release describes, and a memorandum of
understanding promises. Four different verbs, four different weights, and the
public conversation about this matter collapses all four into one.

---

## 1. Method

1. **Capture before reading.** Every source was fetched to `raw/` and hashed
   before any sentence of it was used. A document that cannot be re-hashed cannot
   be quoted.
2. **Read at tier.** Tier A is a primary document (a filing, an order, a
   regulation, a signed agreement). Tier B is an official index or an official
   summary of a primary document (a docket page, an agency press release, a
   co-plaintiff's own release). Tier C would be credible secondary reporting;
   tier D a snippet. Nothing below tier B carries a finding here.
3. **Quote, then claim.** Each claim in `claims.json` carries a verbatim
   substring of the captured text and a locator (order section and page, or
   complaint paragraph and page). `tools/deere_claims_check.py` re-reads the
   captures and fails the ledger if any quote is not found in the text it names.
4. **Name the gaps.** A proposition that the corpus cannot support is recorded
   with its reason and its tier, and stays out of the findings. It is not
   softened into a hedge.

The check is mechanical, so it can be re-run by anyone holding the captures:

```bash
C:/Azazael/.venvs/py315t/Scripts/python.exe tools/deere_claims_check.py
# expected: verdict: READY   (exit 0)
```

---

## 2. Findings

### F1 — The order is parity with dealers, not a right to repair

The operative duty in §II.A is that Deere must make available to owners and
independent repair providers "Repair Resources equivalent to those Deere then
makes available to Deere Dealers" (D8). The comparison class is Deere's own
dealer network. The order does not create an entitlement to any particular
capability, tool or document; it creates an equality obligation measured against
what dealers get, on a rollout schedule in Appendix B.

Two consequences follow directly from the text and are routinely missed:

- The duty is **dynamic**: it tracks what dealers are given, so a new dealer-only
  tool creates a new obligation once it crosses the §II.C threshold (F2).
- Access is **a licence, not a transfer**: Deere "need not include title to or
  ownership of any of Deere['s intellectual property]" (D11). The order grants
  use, never ownership.

### F2 — The 50 percent trigger, and why it is the order's real seam

Future tools reach owners and independents "as soon as access is granted to over
50 percent of Deere Dealer locations in the United States" (D9). The Commission's
own justification is that at that point a tool is "beyond the experimental or
pilot stage" (D22, Ferguson statement).

That is a defensible line for a product-maturity question and a poor one for a
repair-access question: a capability deployed to 49 percent of dealer locations is
subject to no obligation at all, and a farmer in the uncovered half has no remedy
under this order during that period. This is a reading of the instrument, not an
allegation about Deere's conduct.

### F3 — The order runs ten years from entry, and entry had not happened at capture

§XI provides that the order "shall terminate 10 years from the date on which it is
entered" (D6). The signature block on the captured Doc 260-1 reads "SO ORDERED
this" with the date blank (D7), and the FTC's own docket page recorded the case as
"Case Status Pending", last updated 2026-07-08 (D31).

Three documents therefore agree: a stipulated order was filed for entry, and the
entry that starts the clock was not in the record at capture. Anyone dating the
ten-year term from the 2026-07-08 filing has mis-started it. The correct statement
at capture is: **the term begins on a date that does not yet exist in this
corpus.**

### F4 — Appendix B is where the deadlines actually live, and one of them is conditional on a third party

The order's general deadline is the date of entry. Appendix B then carves out
specific classes. Two matter:

- Legacy air seeders and planters, MY2004 through MY2021, carry a fixed
  **2026-08-01** deadline (D15) — a date that, on the face of the order, falls
  *before* any plausible entry of a stipulated order filed in July 2026. The
  schedule is drafted to be satisfied on entry, not to be read as a calendar the
  court sets.
- Engine-controller capabilities depend on an engine supplier's approval, and run
  "the date 90 days after Deere['s]" receipt of it (D16). An outside party that
  never approves produces a deadline that never begins. This is the one place in
  the instrument where a non-party controls Deere's compliance date, and it is
  drafted as a trigger, not as an excuse.

Five further items carry a **2026-12-31** deadline: Machine Health Insights,
non-reprogramming DTAC access, fluid sampling, predictive-failure (PIP) notices,
and offline mode. These are the last-dated obligations and they land five months
after filing.

### F5 — What the required capability list actually reaches

Appendix A is not a generic "diagnostics" list. Three entries do real work:

- **(p)** operator and service manuals must be viewable and searchable,
  "including any AI-enhanced search functions" (D14) — the obligation follows the
  manual into whatever search layer Deere builds over it.
- **(z)** emissions-inducement overrides must be performable "in connection with
  repair following an engine final inducement" (D12) — the derate/limp-mode
  recovery path, which is where a machine is immobilised and the repair value is
  highest.
- **(aa)** reprogramming and diagnostics must work "in offline mode" (D13) — the
  obligation survives a field with no connectivity.

Together these three close the most common practical gap between "the manual is
published" and "the machine can be repaired where it stands".

### F6 — The 2023 MOU was a different instrument, and its restraint ran the other way

The AFBF–Deere MOU came into force 2023-01-08 (D24), two years before the FTC
complaint. Its stated purpose is a "voluntary private sector commitment to
outcomes rather than legislative or regulatory measures" (D23) — the MOU names
legislation as the thing it substitutes for.

The consideration is visible in §III.A: AFBF undertook to encourage state Farm
Bureaus to "refrain from introducing, promoting, or supporting federal or state"
right-to-repair legislation imposing obligations beyond the MOU (D25). The exit
is narrow — fifteen days' written notice to withdraw, tied to legislation actually
being enacted (D26) — so dissatisfaction with Deere's performance was not, on the
face of the document, an exit.

Two further terms limit what the MOU ever promised: a tool "no longer available"
to the manufacturer or its authorised repair network need not be supplied (D27),
which makes availability contingent on the manufacturer's own product decisions;
and nothing in the MOU required allowing owners or independents to "override
safety features or emissions controls" (D28).

The FTC order is a different animal: it is enforceable by a court, it has a term,
it has deadlines, and its measure is dealer parity rather than a list of
commitments. The MOU's own text is why "Deere already agreed to this in 2023" is
not a defence to the 2025 complaint.

### F7 — The DMCA exemption covers the vehicle, not the business

The 2024 triennial rulemaking renewed the anti-circumvention exemption for
"computer programs that control motorized land vehicles, marine vessels, or
mechanized agricultural vehicles or vessels for purposes of diagnosis, repair, or
modification" (D29, 89 FR 85437, 2024-10-28). Mechanized agricultural vehicles are
inside the class.

The same rulemaking declined a broad commercial and industrial equipment class;
the grant reached only equipment "primarily designed for use in retail-level
commercial food preparation" (D30). So the exemption's boundary is drawn around
what the machine is, not around who is repairing it or whether a living can be
made from the repair.

The exemption is also a defence to a circumvention claim. It does not compel
anyone to publish a manual, sell a tool, or license a diagnostic. A farmer who may
lawfully circumvent a lock is not thereby given the lock's key.

### F8 — The plaintiffs are five sovereigns, and the case survived a pleadings challenge

The order's definition of Plaintiffs is "the states of Illinois, Arizona,
Minnesota, and Wisconsin, acting by and through their respective Attorneys
General, and Plaintiff Attorney General Dana Nessel, on behalf of the People of
Michigan" (D1). That is four states plus the Michigan Attorney General suing for
the People of Michigan — five sovereign plaintiffs, a count that the Wisconsin
release separately renders as "the Federal Trade Commission (FTC) and four other
states" (D32), because Wisconsin counts itself as one of the five.

At filing on 2025-01-15 the plaintiffs were the FTC plus Illinois and Minnesota
only (D2). Arizona, Wisconsin and Michigan joined later; an amended complaint
followed on 2025-02-07 with the same allegations (D3), and Deere denied them. On
2025-06-09 the court denied Deere's motion for judgment on the pleadings (D4), so
the allegations survived a pleadings challenge and were never adjudicated on the
merits — the case was stayed on 2026-05-15 for thirty days and again on 2026-06-09
before the stipulated order was filed.

### F9 — Who says what, and in what posture

Three sentences in this corpus are routinely quoted as if the Commission found
them. Each belongs to a different speaker and a different posture, and the
record keeps them apart:

- The Commission's description of its own remedy — that "by the end of this year
  Deere must provide to farmers and independent repair providers" parity with
  dealers (D21) — is the Chairman's summary in a statement accompanying the
  settlement, not an operative clause. The operative clause is §II.A (D8), and
  its schedule is Appendix B (F4). Where the statement and the appendix differ on
  timing, the appendix governs.
- The same statement records that its author "dissented for procedural reasons"
  when the Commission filed the complaint in January 2025 (D20). The enforcement
  posture of this matter is therefore not a straight line: the filing and the
  settlement were not endorsed by the same majority for the same reasons, and a
  reader citing the Commission's support should cite which act it supported.
- The proposition that Deere holds the only fully functional repair tools is
  pleaded in the complaint (§¶8, D17) and restated in the co-plaintiff's release
  in the same voice: "As alleged in the joint lawsuit, Deere makes the only
  software repair tools capable of performing all electronic repairs on Deere
  equipment" (D33). That is an allegation carried forward by a party, not a
  finding. It is the single most repeated sentence in coverage of this matter and
  the one with the least procedural weight behind it.

---

## 3. The three regimes side by side

| | **AFBF–Deere MOU** (2023-01-08) | **DMCA exemption** (89 FR 85437, 2024-10-28) | **FTC stipulated order** (filed 2026-07-08) |
|---|---|---|---|
| Legal form | private contract | regulation (rulemaking exemption) | consent order, enforceable by contempt once entered |
| Who is bound | Deere, as a promise to a trade association | nobody is compelled; it removes a prohibition | Deere, by court order |
| What it gives | a described set of commitments (D23) | a defence to §1201 circumvention for diagnosis, repair, modification of covered vehicles (D29) | repair resources equal to dealer access (D8) |
| Measure of adequacy | the MOU's own list | whether the act is circumvention of a covered program | **dealer parity**, plus Appendix A capabilities (D8, D9, D12–D14) |
| Timing | in force 2023-01-08 (D24); exit on enactment of legislation, 15 days' notice (D26) | renewed in the 2024 triennial cycle; next cycle re-opens it | deadlines from entry; 2026-08-01 for legacy seeders/planters (D15); 2026-12-31 for five items; term 10 years from entry (D6) |
| Enforcement | none stated beyond withdrawal | none; it is a defence, not a duty | court; §XI term; §II.D anti-retaliation instruction to dealers (D10) |
| Coverage boundary | tools Deere still has (D27); no safety/emissions override (D28) | vehicle class (D29), not commercial/industrial equipment (D30) | dealer-parity class, gated at >50% dealer rollout for new tools (D9) |
| Title to IP | silent | n/a | expressly not conveyed (D11) |

The table's purpose is to kill one sentence: *"Deere already agreed to this."*
Three instruments exist, and none of them is the other two. The MOU substituted
for legislation (D23). The DMCA exemption substituted for a prohibition. The order
substitutes for a trial.

---

## 4. What this record does not establish

- **That Deere violated the Sherman Act or the FTC Act.** The complaint pleads
  monopoly power in "fully functional repair tools" (D17) and in a narrower
  "restricted repairs for Deere Large Tractors and Combines" (D18), with dealers
  holding "a 100% market share" and charging supracompetitive prices (D19). Those
  are allegations. The order states it is not "an admission by Deere that it has
  violated the law or that any of the facts alleged by Plaintiffs" is true (D5).
- **That the order is in force.** Entry is blank on the face of Doc 260-1 (D7)
  and the docket page reads pending (D31). Until entry, the deadlines in F4 are a
  schedule attached to a motion.
- **That any repair outcome has improved.** Nothing in this corpus measures
  post-order availability of a tool, a manual or a diagnostic subscription. Every
  finding above is about what an instrument says, not about what a farmer can do
  today.
- **The size of any private settlement.** Reporting has described a figure in the
  range of 99 million dollars in a related private class action. No primary
  document for that case is in this corpus, so D35 is BLOCKED and the figure
  appears nowhere in the findings.
- **Paragraph 9 of the complaint.** The captured redacted PDF's text layer is
  missing the object of "Deere also fails to" (D34). The sentence cannot be quoted
  from this capture. It is recorded as UNSUPPORTED rather than reconstructed from
  the surrounding paragraph — a plausible reconstruction is exactly what a
  court-grade corpus may not do.

---

## 5. Provenance

All eight captures live in `raw/`, named `beam1_20261105_{A,B}_<slug>.<ext>`, with
a machine-readable log in `raw/FETCH_LOG.jsonl`. `sha256` is of the file on disk;
the checker recomputes it and fails as BLIND on any mismatch.

| id | tier | bytes | pages | sha256 (first 16) | source |
|---|---|---|---|---|---|
| `stipord` | A | 737,570 | 35 | `4023bd9af363224f` | `ftc.gov/system/files/ftc_gov/pdf/Deere-JointMotion-StipOrd.pdf` — Doc 260 (joint motion) + Doc 260-1 (order), filed 07/08/26 |
| `complaint` | A | 504,612 | 37 | `da1ffe28a7afb9fd` | `ftc.gov/.../DeereCoREDACTEDComplaintCaseNo325-cv-50017.pdf` — Doc 1, filed 01/15/25 |
| `ferguson` | A | 252,876 | 4 | `4e50f8668e671797` | `ftc.gov/.../deere-chairman-ferguson-statement.pdf` — 2026-07-08 |
| `mou` | A | 232,528 | 6 | `7de4d565a6260c5c` | `fb.org/files/AFBF_John_Deere_MOU.pdf` — signed 2023-01-08 |
| `dmca` | A | 111,705 | – | `64eca43ca6f8e30a` | `govinfo.gov/.../FR-2024-10-28/html/2024-24563.htm` — 89 FR 85437–85450 |
| `wi_doj` | B | 204,197 | 3 | `aedccdd3e987a920` | `wisdoj.gov/PressReleases/press-release-John-Deere.pdf` — 2026-07-08 |
| `case_page` | B | 997,981 | – | `83227293ec5f37af` | `ftc.gov/legal-library/browse/cases-proceedings/211-0191-deere-company-ftc-v` |
| `ftc_release` | B | 1,002,140 | – | `cc0be6fa280e5884` | `ftc.gov/news-events/news/press-releases/2026/07/ftc-states-secure-settlement-deere-company-advancing-farmers-right-repair` |

Capture notes worth keeping:

- The FTC's PDF endpoints returned an identical 1,301-byte "Page Not Found"
  document to a default client on all five FTC URLs. The same URLs returned the
  real documents when fetched with a browser TLS/UA fingerprint. **A 1.3 KB body
  is not a 404 and it is not an absent document**; treating it as either would
  have retired five primary sources that were available.
- The `stipord` PDF is a two-document capture: the joint motion (Doc 260, 5 pages,
  PageID #5639 onward) precedes the order (Doc 260-1). A page citation is only
  meaningful with the document named, which is why every locator in
  `claims.json` names the section and the page.
- The two tier-B HTML captures are archived with their extracted `.txt` beside
  them, so a reader can diff the quote against the text the checker read.

---

## 6. Reproduce

```bash
cd C:/Azazael/azazael

# 1. digests: every capture still the bytes that were read
C:/Azazael/.venvs/py315t/Scripts/python.exe tools/deere_claims_check.py --digests

# 2. quotes: every SUPPORTED claim is a verbatim substring of the text it names
C:/Azazael/.venvs/py315t/Scripts/python.exe tools/deere_claims_check.py

# 3. one claim, in context
grep -n -A3 -B3 "over 50 percent of Deere Dealer locations" \
  ARC/deere/raw/beam1_20261105_A_stipord.txt
```

Exit codes are the instrument's: **0 READY**, **1 GAPS or INCOMPLETE**, **2 BLIND**
(a capture or the ledger cannot be read — never a pass).

---

## 7. Ledger defects carried in the open

| id | status | what it is |
|---|---|---|
| D34 | UNSUPPORTED | Complaint ¶9's object is absent from the redacted PDF's text layer. Needs a page-image read or a cleaner copy. |
| D35 | BLOCKED | The private class settlement figure has no primary capture in this corpus. Tier C reporting alone does not reach SUPPORTED. |
