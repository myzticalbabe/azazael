---
name: asof-qualifier-protocol
description: As-of qualifier protocol for investigations — detect role/title drift (officer/board changes after a source filing), insert a uniform dated banner, and sweep the corpus for citations that assert stale roles as current. Covers the banner-doesn't-travel-with-pasted-text trap and inline-qualifier pass. Distilled from the BCC board-reorg sweep (2026-09-03).
metadata:
  category: process
  project: azazael
  version: 1.0.0
---

# As-of Qualifier Protocol

## Overview

When an investigation cites roles/titles from a dated source document (a Form 990,
a license, a corporate filing) and the subject later changes those roles (board
reorganization, officer turnover), every document that cites the old roles must be
re-audited — not just for tables and rosters, but for **assertions embedded in
send-ready copy** (letters, emails, scripts, action items).

**Why:** a top-of-page as-of banner does NOT travel with the document. These
corpus docs are *templates* — users copy the letter/email body out and send it.
If the body says "Board Chair John Smith" with no date, the recipient reads it as
current fact. The banner covers the page; only inline qualifiers cover the paste.

**Proven on:** BCC board reorganization (2026-09-03) — FY2025 990 (filed May 8,
2026) showed Plageman=Chair / Robinson=Treasurer; live site Sep 2, 2026 showed
Seitz=Chair / Ralph=Treasurer with Plageman+Robinson demoted to plain members.
11 send-ready templates carried stale role assertions; 45+ citations qualified.

---

## Protocol Steps

### 1. Establish the drift facts first

Before editing anything, pin down the exact bracket:

- **Floor date:** the dated source document (filing, 990, registration) and the
  roles it shows. Cite the document + filing date exactly.
- **Ceiling date:** the first observation of the new state (live site, filing,
  minutes) and the new roles.
- **Unaffected facts:** note what the reorg does NOT change (entity ownership,
  employer conflicts, funder interlocks) so qualifiers don't get over-applied.

### 2. Uniform banner insertion (page-level qualifier)

Every affected corpus doc gets one standardized banner near the top:

```html
<div id="board-role-asof-sep2026" style="...">
  ⚠ AS-OF BOARD ROLES (addendum <DATE>): Officer roles cited in this document are
  as of the <SOURCE> (filed <DATE>) and reflect a post-filing reorganization first
  observed <DATE>: <old-role-holder> is no longer <role> and <other> is no longer
  <role> (both remain <current-status>); current roles per <live source> — <new slate>.
</div>
```

**Real-id rule:** give the banner a real `id` attribute, not just a marker
comment. A comment cannot be `getElementById`'d by a render probe. (Real incident:
the banner existed as a comment only; the visibility probe found nothing until the
id was added — 37/37 docs updated.)

**Banner wording must state:** the source doc + date, the reorg observation date,
who lost which roles, and the current slate.

### 3. Corpus-wide sweep — tables and rosters

Scan every doc for `Name + role-token` co-occurrence (case-insensitive):

```python
role_tok = re.compile(r'(Board\s*)?(Chair\w*|Treasurer|Secretary|Vice\s*President|VP|President|Officer|Trustee|Director)', re.I)
```

- Strip tags, normalize whitespace, check ±90–160 chars around each name hit.
- **Tables/rosters are covered by the page banner** — a dated roster table under
  the banner is fine (as long as the banner states the as-of source).
- **BUT** role assertions in paragraph/sentence text need more than the banner
  if the doc is send-ready.

### 4. The send-ready copy audit (the step that's usually missed)

Classify every doc:

| Doc type | Banner enough? | Why |
|----------|---------------|-----|
| Reference/analysis docs, tables | ✅ Yes | Read in place; banner visible |
| Letter/email templates with copy buttons | ❌ **No** | Body gets pasted OUT; banner left behind |
| Video scripts / narrated content | ❌ **No** | Lines are read/displayed standalone |
| Action-item / routing lists | ❌ **No** | Instructions are executed standalone |

For send-ready docs, detect which citations sit inside **copyable blocks**
(letter bodies, email templates, script lines, todo actions) — search for
`📋 Copy`, `Subject:`, `Dear `, `To:`, `script-line`, `todo-item` markers
upstream of each cite. Those are the ones that need inline qualifiers.

### 5. Inline qualifier pass (the fix)

Apply a uniform inline qualifier at every send-body citation:

```text
Board Chair Joseph Plageman Jr. (as of the FY2025 Form 990, filed May 8, 2026)
Treasurer John Robinson (as of the FY2025 Form 990, filed May 8, 2026)
```

Rules:
- Use ONE consistent qualifier phrase for the whole sweep so verification is a
  simple grep: `as of the FY2025 Form 990, filed May 8, 2026`.
- Prefer "as of <source>" over "then-" — it names the provenance.
- If the source is already named in the sentence (e.g. "per the 990"), a light
  touch suffices — but when in doubt, qualify.
- **Fix routing instructions explicitly** — an action item saying "Send complaint
  to Board Chair X" is not just stale text, it's a misdirect. Point to the current
  office-holder or remove the direct-send step (investigation subjects are not
  partners).
- Handle HTML-entity variants (`&` vs `&amp;`) and tag-wrapped names
  (`Treasurer <strong>John Robinson</strong>`).

### 6. Verify (fix-then-reverify loop)

1. **Residual scan** — re-run the name+role scan; the ONLY acceptable residual
   cites are: the banner itself, roster tables under the banner, and my own
   inserted qualifier text. Zero unqualified send-body citations.
2. **Structural audit** — run the project's HTML audit over the edited files.
3. **CDP render probe** — headless Chrome, navigate each edited doc, assert:
   - banner `id` present and visible (`getComputedStyle().display != 'none'`)
   - as-of phrase count ≥ 1 in `document.body.innerText`
   - body text length > threshold (docs are scrolling-capture style; content is in
     `#scroll-container`, so probe `getElementById('scroll-container').innerText`,
     NOT `body.innerText` which stays ~0)
   - zero `Runtime.exceptionThrown`
4. **Sync** — copy edited docs to the archive copy with hash verification
   (sha256 prefix match local ↔ archive).

---

## Trap Catalog

| Trap | Symptom | Fix |
|------|---------|-----|
| Banner doesn't travel | Pasted letter asserts stale role | Inline qualifiers in send bodies |
| Banner id missing | `getElementById('banner')` returns null | Add real `id`, not just a comment |
| Probe reads `body.innerText` | len=0 on scrolling-capture docs | Read `#scroll-container`.innerText |
| Entity variants | `&amp;` vs `&` breaks exact-match replace | Run pattern sweep on both encodings |
| Tag-wrapped names | `Treasurer <strong>John Robinson</strong>` | Regex with optional tag groups |
| Nested parens from hasty replace | `(as of ... (as of ...))` | Integrity check: no `((as of`, no `))` |
| Stale routing instruction | "Send to Board Chair X" (X demoted) | Re-route to current office-holder or oversight bodies |

## Real Incident Record (2026-09-03)

- **Corpus:** 37 bannered docs (banner + real id), 11 send-ready templates with
  inline qualifiers, 3 .md/skill files (bcc-investigation, bcc-owl-framework,
  README.md) qualified.
- **Found:** 45+ role citations in copy bodies asserting Plageman=Chair /
  Robinson=Treasurer with no inline date; SCROLL_RECORD routed a formal complaint
  to the demoted ex-Chair.
- **Fix:** inline `(as of the FY2025 Form 990, filed May 8, 2026)` at every cite;
  routing re-directed to oversight bodies only / current chairperson.
- **Verified:** structural audit 11/11 PASS · CDP probe (banner visible + as-of
  count ≥1 + zero exceptions) · 0 unqualified body cites remaining · 11/11 docs
  synced hash-MATCH to the G: archive.
- **Bracket finding:** ~May 8, 2026 (990 signing, Plageman still Chair) → Sep 2,
  2026 (new slate live); PA BCO cert #3306 (FY2025 renewal ~May 15, 2026) inside
  the window but roster not public; DOS corporate record Cloudflare-walled.

## Related Skills

- `html-render-verification` (#1248) — the CDP render-check half of step 6
- `corpus-reference-integrity` (#1249) — phantom-reference sweeping discipline
- `pre-action-gate-lite` (#1253) — fix-then-reverify loop
- `background-sweep-resilience` (#1251) — crash-resilient corpus sweeps
- `azazael-archive-restore` (#1222) — archive sync with hash verification