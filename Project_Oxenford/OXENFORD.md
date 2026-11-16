# OXENFORD — the paradigm for evolving a tool against a world it does not own

**Origin:** Project Scribe, 2026-11-03. Scribe could fill five hand-coded forms and
nothing else. In one session it gained a discovery layer, a measured registry, a
classifier, a value guard, an honest audit, and two live forms it had never been
written for — and every one of those seven changes was bought by a failure that
only appeared when the tool was pointed at someone else's live page.

**What it is:** a repeatable order of work for tools whose job is to *act on an
interface a third party controls* — a grant portal, a ticketing API, a bank's
upload screen, a government filing page. The interface moves, refuses, hides
behind a login, and renders its form in JavaScript. A tool that hard-codes today's
interface is a transcription, not a capability.

**What it is not:** a refactor guide, a test strategy, or a general "make it
better" checklist. Every rule below is scoped to a tool that must act on a live
foreign surface. Applied elsewhere it becomes ceremony.

---

## The seven stages

Each stage has an exit condition. A stage that has not met its exit condition is
an unknown, in both directions — the tool may be better or worse than the summary
says, and the summary is wrong either way.

### O1 — INVENTORY: name the doors, not the forms

Write down every surface the tool must act on, each with an id, a URL, a category,
and **who it is for**. Category is not decoration: it is the axis a human uses to
decide whether a gap matters.

> Scribe: 15 portals, 5 categories (`academic_federal`,
> `academic_international`, `academic_private`, `individual_entrepreneur`,
> `nonprofit_oss`), in `data/grant_portals.json`. The file records who the money
> is for; it explicitly does not record what kind of form the door has, because
> that is O2's job and would be stale by morning.

**Exit:** every door has an id, a URL, a category, and an audience. No door is
described as "a form" or "not a form" yet.

### O2 — MEASURE: the live page is the schema

One probe per door, run against the live surface, recording what it actually is:
HTTP state, final URL, bytes, field list, and the error string if it failed.
Never a human's recollection of the site, never last month's HTML.

> Scribe: `tools/portal_census.py` opens all 15 on every run and writes
> `data/portal_census.json` plus a tee'd live log. `parse_form_schema` is imported
> from the application, not re-implemented — one parser, so the measurement and
> the filler cannot disagree about what a field is.

**Exit:** one record per door carrying state, field count, field metadata, and the
exact error text when there is one.

### O3 — CLASSIFY: a state is a sentence about what to do next

Six states, each mapped to an action. `FORM_STATIC→DRIVE_NOW`,
`SEARCH_ONLY→NEEDS_HOP`, `NO_FIELDS→NEEDS_HOP_OR_BROWSER`,
`AUTH_WALL→NEEDS_CREDENTIALS`, `REFUSED→NEEDS_STEALTH`, `ERROR→INVESTIGATE`.

The point is not the taxonomy; it is that **"failed" is not a state.** Collapsing
"JavaScript-rendered form" (the tool has a browser) into "failed" next to
"account-gated" (the tool is the wrong tool and a human is the right one) turns a
capability audit into a complaint nobody can act on.

**Exit:** every state in the classifier has a named action, and a control proves
each state is reachable.

### O4 — ADAPT: change the adapter, not the data

The measurement must reach the runtime, or every run re-derives it. Scribe merges
the census's measured forms into its own registry **at import**, so the next dry
run opens a form the census found.

The rule that makes this safe: **a measurement never shadows a hand-tuned entry.**
The census can read a form; it cannot read the funder's rules. Letting a measured
NLnet entry replace the hand-written one would have silently dropped
`eligible_regions=('horizon_europe',)` and filled a US applicant into a fund that
excludes them — the measurement would have deleted a guard it has no way to
re-derive.

> Evidence: `[EVOLVE] 2 measured program(s) merged` and
> `[EVOLVE] 1 measured program(s) not merged: URL already registered by hand (a
> measurement cannot inherit funder eligibility rules)`.

**Exit:** the runtime consumes the measured artifact by path, hand-tuned entries
win on collision, and the collision is printed rather than dropped.

### O5 — GUARD: the value must be usable by the receiver

Every value the adapter emits is a claim about the world. A field named "URL"
must receive an address; a text field must not receive a local attachment path;
a box asking "about yourself" must not receive the project blurb.

> Three measured wrong answers, all of which the page itself would have accepted:
> a `.mp4` path in "Multimedia URL", a `.xlsx` path in "Estimated Budget", and
> `$100,000` in "Dedicated Funding Areas" (because the word *funding* mapped to a
> sum).

**Exit:** negative controls exist for each guard, and the guard prints `[GAP]` with
the reason instead of silently emitting a plausible wrong answer.

### O6 — VERIFY: an audit that can say "blocked"

A dry run that only reports what it filled is a progress bar. It must report what
the receiver would reject.

> Measured: Scribe printed `missing_required 0` and "Form would be accepted" while
> six required fields sat empty, because the page marks required in JavaScript and
> the parser only read the `required` attribute. After the fix:
> `[AUDIT] 40 fields | filled 7 | missing_required 4` and
> `required but empty: tfa_1118, tfa_3016, tfa_6, tfa_26`.

A present element is also not an interactable element: two required inputs were in
the DOM and timed out for 5 s each. The fallback is a DOM write with the events a
framework listens for, printed as `[FILL*] … (js fallback: TimeoutError)` — never
as a plain success.

**Exit:** the audit counts come from the live page after filling; a blocked state
is distinct from an error state; the run says which fields a human must supply.

### O7 — RECORD: the next run reads the record

Per run: a live log with a timestamped filename, a machine-readable artifact, and
a document that names the limitations. The artifact is input to the next run, not
a report to a human.

> The limitation document is the deliverable as much as the code is: the AOR wall,
> the missing indirect-cost model, the absent deadline tracking, the letters of
> support, the resubmission cycle.

**Exit:** log path, artifact path, and limitation doc are all named in the run's
own output.

---

## The invariants, each bought by a measured failure

| # | Invariant | The failure that bought it |
| --- | --- | --- |
| INV-1 | A measurement tool must survive its own output | The census wrote `discovered_programs.json` as cp1252; the application failed to read it as UTF-8 at byte 370 |
| INV-2 | A cheap proxy for a property is not a test of it | A field count scored grants.gov's search panel and Wellcome's newsletter box as application forms |
| INV-3 | A third party's downtime is a reading, not a gate failure | `nsfgrfp.org` closed the connection; a gate that reddens when someone else's server is down gets switched off |
| INV-4 | Measurement never outranks hand-tuned rules | A measured NLnet entry would have dropped the Horizon Europe eligibility guard |
| INV-5 | A blank beats a plausible wrong answer | `.mp4` path into "Multimedia URL"; `.xlsx` path into "Estimated Budget" |
| INV-6 | An audit must read how the page *actually* marks the requirement | JS-required fields read as optional, producing "would be accepted" on an empty form |
| INV-7 | Presence in the DOM is not interactability | Two required inputs timed out; the run must record the fallback it used |
| INV-8 | Every state maps to an action, or it is not a state | `NO_FIELDS` and `AUTH_WALL` collapsed into "failed" |
| INV-9 | A broad word is a wrong answer waiting for a form to ask | *funding* → a sum → "$100,000" in "Dedicated Funding Areas" |
| INV-10 | Exit codes must separate "could not run" from "ran and found nothing" | 0/1/2 with the unreachable case explicitly non-fatal |

---

## The failure taxonomy (what the seven stages are for)

1. **Wrong answer** — the tool emits a value the receiver cannot use. Detected by
   O5 guards and negative controls; invisible to any check that only counts fills.
2. **False acceptance** — the tool reports readiness it did not establish.
   Detected only by O6 audits that read the page's real requirement mechanism.
3. **Self-measurement error** — the tool's own output cannot be read by the tool.
   Detected only by running the consumer against the producer.
4. **Silent shadowing** — new knowledge deletes old knowledge. Detected by O4's
   collision rule and its printed count.
5. **Unreachable treated as failure** — the gate reddens on someone else's
   outage and gets switched off. Detected by O3's state table + INV-3.
6. **Stale artifact** — a measurement answers for a tree it no longer describes.
   Detected by O7's timestamped log and by re-running O2 before quoting O2.

---

## Applying OXENFORD to a new tool

1. Declare it: `oxenford.json` at the project root naming `registry`, `tool`,
   `census`, `runtime`, `docs`.
2. Run `python tools/oxenford_lint.py --project <dir>` — it checks the seven
   stages mechanically where they can be checked, and runs the tool's own
   selftest so the declaration cannot outrun the behaviour.
3. Fill the gaps it names, **in stage order**. Adapting O4 before O2 has measured
   is writing a guess with better formatting.
4. Re-run the lint, then run the tool live and keep the log.

The lint exists because a practice that depends on remembering it is a hope. Its
own negative control is required: `--selftest` builds a conforming fixture (must
pass) and a violating one (must fail), because a lint that always passes is the
same defect it was written to catch.

**Reference implementation:** `C:/Azazael/azazael/Project_Scribe` —
`data/grant_portals.json` (O1), `tools/portal_census.py` (O2/O3),
`scribe.py:load_discovered_programs` (O4), `ProjectProfile.get_field` +
`_text_safe` (O5), `audit_submission` / `parse_form_schema` (O6),
`logs/portal_census_*.log` + `docs/SCRIBE_EVOLUTION_2026-11-03.md` (O7).
