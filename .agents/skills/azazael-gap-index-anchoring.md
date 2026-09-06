---
name: azazael-gap-index-anchoring
description: Machine-readable gap index maintenance for investigation corpora —
  canonical JSON + rendered table lockstep in the gaps doc (build_gap_index.py:
  extract / write / anchors subcommands), semantic freshness checks that never
  rewrite a healthy doc, and hub-doc anchor-line verification (<p
  class="hub-gap-anchor">Linked gaps: #N…) resolving to indexed gap ids. Proven
  2026-09-05: 45 gaps indexed, 10 hub docs × 3 anchors, zero dangling.
metadata:
  category: investigation
  audit_date: 2026-09-05
  auto_load: false
  created: 2026-09-05
---

# azazael-gap-index-anchoring

Keep the investigation corpus's gap index machine-readable and its evidence→gap
anchors honest, with a deterministic generator instead of hand-maintained HTML.

## When to use

- After INVESTIGATION_GAPS.html (or any gaps doc) is edited — re-verify the
  embedded index and every hub-doc anchor line still agree.
- When building a NEW gap-indexed corpus doc — run `extract` to bootstrap a
  standalone JSON, edit the JSON, then `write` to re-render the table.
- Before trusting a "gap #N" cross-reference in evidence docs.

## The canonical structure

The gaps doc carries BOTH a rendered table and the same data as JSON in one
block:

```html
<div id="gap-index">
  <h2>… (auto-generated; N gaps)</h2>
  <table>…<tr id="gap-N">…rows…</table>
  <script type="application/json" id="gap-index-json">{…canonical…}</script>
</div>
```

The embedded JSON is the source of truth; the table is its render.

## Commands (`python build_gap_index.py`)

| Subcommand | Purpose | Exit codes |
|---|---|---|
| `extract DOC --out f.json` | Pull canonical JSON out of the doc | 0 ok / 2 err |
| `write DOC` | Re-render the gap-index block from the embedded JSON | 0 ok |
| `write DOC --check` | Freshness check WITHOUT writing | 0 fresh / 1 stale |
| `anchors DOC --corpus DIR` | Verify every hub anchor cites an indexed id | 0 pass / 1 dangling |
| `anchors … --strict` | Also fail on indexed-but-never-cited gaps | |

Env override: `GAP_INDEX_DOC` sets the default doc path.

## Proven results (2026-09-05)

- INVESTIGATION_GAPS.html: **45 indexed gaps** (ids 1–48 minus the 3
  narrative-only gaps #5/#30/#41 — topic-based rows, not phraseable as "Gap #N").
- **10 hub docs** carry anchor lines (`AUDIT_REPORT`, `EXPANDED_EVIDENCE`,
  `HARM_EVIDENCE_MASTER`, `RECUSAL_EVIDENCE`, `DEEP_DIVE_HARM`, `LEGAL_OVERSIGHT_ANGLE`,
  `BCC_GRIEVANCE_LETTER`, `COMPLIANCE_SELF_DEALING_ANGLES`, `FEDERAL_COMPLIANCE_SWEEPS`,
  `LEGISLATIVE_COMMITTEES`) × 3 cites each → 30 anchors, all resolving, **0 dangling**.
- Anchor-check FAILED-unsafe guarantees: a doc citing `#99` fails `anchors` with
  exit 1 before any claim relying on it is trusted.

## Traps (all hit for real)

1. **Byte-compare freshness is a false positive machine.** The original doc's
   block has emoji headers, provenance strings ("auto-generated Sep-5(12)"),
   and different JSON escaping than any regenerator will emit. Comparing
   `render_block() == old_block` always reports STALE. Compare **semantics**:
   embedded JSON equality + the set of rendered `<tr id="gap-N">` rows equals
   the canonical key set (`_block_is_fresh`). A healthy doc must never be
   rewritten by a generator run.
2. **`ROW_RE.findall` returns tuples** (3 capture groups) — use `finditer` and
   `m.group(1)` when collecting row ids, or int() blows up on the tuple.
3. **Git Bash `/tmp` ≠ Python's temp dir** — native Windows Python cannot see
   bash `/tmp` paths. Test round-trips with a copy in the cwd, then delete it.
4. **The 53-gap ledger isn't phraseable as "Gap #N".** Only ~3 sections use that
   exact phrase; the rest are narrative annex rows. Build the index from a
   context-filtered sweep of bare `#N` cites, and be honest in the artifact that
   topic mapping is not exhaustive enumeration.
5. **Anchor lines are plain `<p>` tags** — an anchor cite to a gap that was later
   renumbered goes silently stale (no schema enforces it). The `anchors` check
   is the enforcement; run it in CI or after every gaps-doc edit.

## Verification discipline

After touching the gaps doc or any anchor line:

1. `build_gap_index.py write DOC --check` → must exit 0.
2. `build_gap_index.py anchors DOC --corpus .` → must exit 0.
3. Structural audit of the full corpus (88 root HTML docs, 2026-09-05) → 0 issues.
4. CDP render probe of the gaps doc + one anchor-bearing hub doc → 0 exc/err.

Related skills: `corpus-reference-integrity` (phantom-cite sweeps),
`html-render-verification` (CDP probe), `investigation-evidence-location`
(gap classification), `catalog-reconciliation` (the counting discipline that
this skill's numbering must also respect).
