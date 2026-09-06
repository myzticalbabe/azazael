# AOA Generation Evolution — 7 evolved files (Desktop superset vs G: gen 1)

_Comparison method: `diff` Desktop/AOA (newest, canonical) vs `G:\AZAZAEL\AOA` (gen 1) on the 7 files that differ. Verified Sep 2, 2026. All other 23 .py files are byte-identical across repo↔Desktop; g1↔g2↔restored are identical to each other._

## Summary: what each file's evolution ADDED

| File | Δ Desktop-only lines | What the newer generation adds |
|---|---|---|
| `arms/libra_arm.py` | +123 / −10 | **5 NEW capabilities (6 → 11)**: the entire Berks County BCC layer — `check_berks_rules`, `calculate_berks_fees`, `generate_berks_ifp`, `prepare_berks_filing`, `get_berks_calendar` — wiring `jurisdictions.pa.berks.*` (BerksCourtRules, BerksProthonotary, BerksIFPAssistant, PaperFilingSubmitter, BerksCourtCalendar). Plus: **`_METHOD_MAP` template→method router** (15 templates incl. 9 `bcc_*` Berks-specific ones), **`_METHOD_DEFAULTS`** per-method token defaults, `datetime` import, and a REGULATORY NOTICE (licensed-attorney-review disclaimer). **This is THE capability-bearing change.**
| `cli/__init__.py` | +6 / −1 | Makes the CLI **importable as a package**: `from .aoa_cli import main` + `__all__ = ["main"]`. g1's `__init__` was a bare docstring — programmatic `main` entry didn't exist. |
| `rebuild_html.py` | +17 / −1 | Adds a **stats table row + "Generation Notes" section** (azazael/run_cluster), a `data-generated` DOM marker, and writes `AOA_STRUCTURE_REBUILT.html` instead of overwriting. Minor. |
| `build.py` | +26 / −2 | **Mermaid graph restructure only**: reorganizes the disclosure Mermaid into explicit `QUARTET` / `SUPPORT INFRASTRUCTURE` subgraphs + styled `classDef`s (orchestrator/quartet/support colors). Same arms, same content — presentation, not capability. ("101 Worms" label still present in both.) |
| `build_disclosure.py` | +93 / −43 | **Rewrite of the disclosure builder**: added a `system` block (python_version, cpu_count, node) + `value()` HTML-escape helper; per-field fallback handling (`bm.get` instead of subscript). More robust + injection-safe; no new runtime capability. |
| `gen_html.py` | +115 / −203 | **Full rewrite**: g1's compact single-letter locals + `DIAGRAMS` template tuples → Desktop's `perf/aza/system` named access + `text()` escape helper + `diagrams` list with full inline Mermaid (Neural System Architecture, etc.). Net *smaller* generator, HTML-escaping added, diagrams expanded. |
| `inject.py` | +96 / −196 | **Section-based injection engine rewrite**: g1 procedural HTML → Desktop `diagram(title, body)` helper + `sections` list, `html.escape` on all injected content, appends 5 panels: Quartet Neural Core topology, Neural Data Pathways cross-arm routing, Session Lifecycle sequence, Memory Architecture (DirectMemory+PAMS), Worm Cluster Topology. XSS-safe + more diagrams. |

## Capability accounting (the important part)

- **Runtime capabilities added: exactly 6** — 5 Libra Berks capabilities + 1 importable CLI `main`. All other diffs are presentation/robustness (HTML generation rewrites, escaping, Mermaid layout).
- **No capability was removed.** The −10/−43/−196 g1-only lines are superseded implementations, not lost functionality (g1's `tg.generate`, `fee_schedule`, `deadline_calculator` calls remain in Desktop's libra_arm paths; the builder rewrites preserve their outputs).
- **Confirmed against the map:** the 11 Libra capabilities in the Sep 2 audit (`aoa_audit_2026-09-02.json`) exactly equal g1's 6 + these 5 Berks additions.

## Why this matters for the historical-archive directive

The 7 evolved files are the canonical example of "old versions hold original functionality": g1's libra_arm only knew the 6 generic legal caps; the Desktop/current generation knows the full Berks BCC layer (11 caps). Anyone reading g1's libra_arm would conclude AOA can't do Berks filings — it can, since the Desktop era. The archived gen-1 copies remain byte-faithful (restored + g1 + g2 identical), so both generations' functionality is findable — which is exactly what `archive/restored/` is for.