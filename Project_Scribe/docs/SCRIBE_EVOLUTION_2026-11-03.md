# Scribe evolution — 2026-11-03

**Goal:** Scribe stops being five hand-written forms and becomes a filler that can
apply to *any* grant that is actually available to an academic institution or an
individual, across the categories they can use.

**Paradigm applied:** OXENFORD (`Project_Oxenford/OXENFORD.md`). Scribe is its
reference implementation and declares itself in `oxenford.json`.

---

## 1. What was measured (not assumed)

`python tools/portal_census.py --run --expect nlnet_propose=FORM_STATIC
--expect sloan_apply=REFUSED` — 15 portals, 5 categories, live log
`logs/portal_census_20261103_173735.log`, exit 0, both expectations held.

| state | count | doors |
| --- | --- | --- |
| `FORM_STATIC` | 3 | emergent_ventures (18 fields), awesome_foundation (14), nlnet_propose (26) |
| `SEARCH_ONLY` | 7 | grants_gov_search, nsf_funding, nih_grants, ukri_funding, wellcome, pollination_project, otf_iff |
| `NO_FIELDS` | 3 | research_gov, eu_funding_tenders, gates_grantseekers |
| `REFUSED` | 1 | sloan_apply (403) |
| `ERROR` | 1 | nsf_grfp (RemoteDisconnected) |

By category: `academic_federal` (3 search-only, 1 no-fields, 1 error),
`academic_international` (1/1), `academic_private` (1 search-only, 1 no-fields,
1 refused), `individual_entrepreneur` (2 drivable, 1 search-only),
`nonprofit_oss` (1 drivable, 1 search-only). **Every drivable form is outside
academic_federal and academic_international** — that asymmetry is L1.

`python scribe.py --dry-run-all --profile profiles/nurse_ratchet_profile.json
--country "United States"` — the adaptation loop, before and after:

| run | emergent_ventures | awesome_foundation | verdict |
| --- | --- | --- | --- |
| first dry run | filled 0/40 | filled 0/24 | forms opened, nothing filled |
| after label+synonym resolution | filled 6/40 | filled 5/24 | 13 field controls |
| after value guards + required audit | **filled 7/40** | **filled 5/24** | 15 field controls, 0 wrong values |

Final audit lines, from the live pages:

```
[AUDIT] 40 fields | filled 7 | missing_required 4 | overflow 0 | out_of_bounds 0
[AUDIT] required but empty: tfa_1118, tfa_3016, tfa_6, tfa_26
[AUDIT] 24 fields | filled 5 | missing_required 3 | overflow 0 | out_of_bounds 0
[AUDIT] required but empty: project[chapter_id], project[use_for_money], project[about_me]
```

Selftests: `scribe.py --selftest-fields` → 15/15 controls, exit 0.
`tools/portal_census.py --selftest` → all six states reached, exit 0.

Read `0 ok | … | 2 blocked` carefully: under this contract `ok` means *nothing a
human must supply is missing*, and both driven forms are `BLOCKED` because they
require applicant facts this profile does not hold (see L7). The fills above are
the measured ones — `blocked` is not `failed`, and neither is `ok`.

---

## 2. Limitations, each with the reading that establishes it

**L1 — The AOR wall. An individual cannot apply to a federal or academic grant
through the funder's own system.** research.gov, Grants.gov, NIH and the UKRI
Funding Service all require an institutional account whose Authorised
Organisational Representative submits. Measured 2026-11-03, all four are
`SEARCH_ONLY` or `NO_FIELDS` — indexes and login walls, not forms — and so are
EU Funding & Tenders and Gates Grantseekers. Scribe can prepare the content; it
cannot be the applicant of record.

**L2 — No indirect-cost (F&A) model.** Federal budgets need a negotiated rate and
a base. Scribe fills one number (`funding_amount`) and one prose breakdown. This is
the single largest gap between "fills the form" and "budget survives review".

**L3 — No deadline tracking.** Nothing in the registry carries an open/close date,
so Scribe cannot tell an applicant that a door closed, or order work by urgency.

**L4 — No letters of support or reference requests.** Every academic route needs
them; there is no mechanism to request, collect or attach one.

**L5 — No resubmission cycle.** Panels return comments and funders accept a
revision. Scribe has no notion of a prior submission, so it cannot answer "what did
the reviewer object to and what changed".

**L6 — No document upload.** The live run prints
`[UPLOAD] Document upload not yet implemented for census_emergent_ventures`.
Required attachments are counted as gaps, never sent.

**L7 — Some required fields need facts the profile does not hold.** Measured:
phone, city, state, and "Affected Region" on the Mercatus form; the chapter select,
"How will you use the money?", and the bio line on Awesome Foundation. Scribe
leaves them blank and says so (`BLOCKED`), which is the correct behaviour and also
the honest limit: it is an assistant to an applicant, not a substitute for one.

**L8 — Required-ness is inferred, not authoritative.** The Mercatus form sets no
`required` attribute; Scribe now reads `aria-required`, `data-required` and
`class="required"` as well. A page that marks required only through a submit-time
handler will still read as optional. This is the weakest link in the audit.

**L9 — Two hosts are unreachable or refuse this network.** `nsfgrfp.org` closes the
connection; `sloan.org` and `mercatus.org` return 403 to the census (the TFA form
host itself serves fine). Recorded as readings, not as failures.

**L10 — Eligibility rules exist for one region only.** The Horizon Europe country
list is the only region encoded, so NLnet is skipped for a US applicant (`2
skipped` in every dry run, and both are NLnet). Every other funder's geographic
rule is unchecked, and an unchecked rule is not a permissive one.

**L11 — Three hand-tuned programs remain unexercised**: `epic_megagrants`
(manual), `github_secure_oss` (github_issue), `herodevs` (manual). Each prints
`UNEXERCISED … no form page to dry-run` — there is no page to measure, so the
census cannot find them and Scribe cannot rehearse them.

---

## 3. What Scribe needs to close them

| limitation | what it needs |
| --- | --- |
| L1 | a partner-of-record mode: prepare the package, hand the submission to an institution's AOR |
| L2 | a budget model with F&A rate, base, and cost-share lines |
| L3 | `deadline`/`opens` fields in the registry, and an ordered queue |
| L4 | a request/collect/attach flow for letters |
| L5 | submissions history keyed by program + cycle |
| L6 | upload support driven by the same measured field schema (`type=file`) |
| L7 | an applicant-facts block in the profile (address, phone, chapter) |
| L8 | an audit that also probes submit-time validation, not only attributes |
| L9 | a retry/stealth policy per host, recorded per attempt |
| L10 | per-funder region rules, published beside the portal |
| L11 | no code: a human runs those two |

---

## 4. Opportunities this opened

1. **Any portal measured as `FORM_STATIC` becomes drivable without code.** Two of
   the three measured forms were never written for: Scribe filled both because it
   resolves fields by their own words and the page's labels, not by a hard-coded map.
2. **Framework-named forms are no longer opaque.** `tfa_3019` means nothing to a
   profile; "Estimated Budget" does. Label resolution is what made a TFA-hosted
   form fillable at all.
3. **The applicant's country reaches the form.** `--country` now seeds the profile,
   so a required Country select fills (tfa_22 left the required-but-empty list).
4. **Wrong answers are refused before submission.** Three measured cases (a `.mp4`
   path in a URL field, an `.xlsx` path in a budget, a sum in "Funding Areas") are
   now blanks with a `[GAP]` reason.
5. **The audit can say BLOCKED**, so a dry run reports what the receiver would
   reject instead of what the filler managed to type.
6. **The paradigm is checkable.** `Project_Oxenford/tools/oxenford_lint.py
   --project .` scores this project against the seven stages and runs its
   selftest; it has a conforming and a violating fixture, so it cannot pass by
   default.

---

## 5. How to reproduce

```bash
cd C:/Azazael/azazael/Project_Scribe
python tools/portal_census.py --selftest
python tools/portal_census.py --run --expect nlnet_propose=FORM_STATIC
python scribe.py --selftest-fields
python scribe.py --dry-run-all --profile profiles/nurse_ratchet_profile.json --country "United States"
python ../Project_Oxenford/tools/oxenford_lint.py --project .
```

Expiry: the census numbers above are a reading of 2026-11-03. Re-measure before
quoting them; portals change their forms and their hosts without notice.
