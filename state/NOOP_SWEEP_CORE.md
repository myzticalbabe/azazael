# NO-OP / runtime-defect / weakened-gate sweep — `src/CORE/` (excluding `WORMS/`)

Date: 2026-10-10. Auditor 5 of 7. Read-only sweep — **no code file was edited.**

## Coverage, and what it does not cover

| measure | value |
|---|---|
| `src/CORE/*.py` listed by glob | **125** files |
| files inspected | **20** |
| of those, read in depth | 8 |
| of those, first-18-line shape scan | 12 |
| coverage | **20/125 = 16%** |
| `WORMS/` subtree | excluded (sibling worker's surface) |
| subpackages one level down (`compliance/`, `inference/`, …) | **not swept** |

**The search tooling failed, and I validated that before trusting it.** `raise
NotImplementedError` with `-g !WORMS/**` returned 0 matches; so did the control
query `def ` in the same working directory. A control that cannot match anything
cannot establish absence, so **no mechanical sweep ran** — every finding below
comes from reading, and every absence claim is marked `CANDIDATE`, never absence.
This matters for the two items in the candidates table: they are "no caller was
found by reading", not "there is no caller".

The glob itself warned that the project scan hit its 10,000-file limit, so the
deepest directories were not enumerated. The 125 figure is a floor, not a census.

## Findings, fatal-first

| # | severity | path::symbol:line | what it does instead | why it cannot affect the outcome it exists for |
|---|---|---|---|---|
| H1 | **HIGH — gate that cannot fail** | `cd4_pipeline.py::NuitkaBuildPipeline.run_stage_3_compiled_validation` (~L490–510) | `if self.dry_run or not os.path.isdir(dist_dir):` returns `passed=True` with summary `"[DRY-RUN] Stage 3 simulated"` — even when `dry_run` is **False** | In LIVE mode with no `azazael.dist` on disk, the compiled-validation stage reports PASS and mislabels itself dry-run. `run_all_stages` folds that into `all_passed`, so the pipeline can report **ALL PASSED having validated nothing**. Stage 3 exists to gate compiled artifacts; a missing artifact is exactly the case it must refuse. |
| H2 | **HIGH — silently reads the wrong database** | `cd3_exporter.py::query_trace_by_id` (~L400) | `path = db_path or str(DB_PATH)` → `memory_store.db`, then `SELECT … FROM otel_spans` | The exporter writes spans to `TELEMETRY_DB_PATH` = `telemetry_store.db` (`self.db_path = db_path or str(TELEMETRY_DB_PATH)`), and the 2026-09-28 split comment at module level says spans left `memory_store.db`. So this reader cannot return the spans its own module wrote — it raises `no such table: otel_spans`, or reports an empty trace, indistinguishably from "no such trace". Its two siblings get it right (`query_unified_trace` and `purge_old_spans` both use `TELEMETRY_DB_PATH`), which is why this reads as an oversight rather than a decision. |
| M1 | MEDIUM — declaration that is never assigned | `cd3_exporter.py` L4–19, `cd4_pipeline.py` L4–24, `safe_sql.py` L5–12 | `__all__ = [...]` sits **inside** the module docstring (`"""` opens at L2/L2/L2 and does not close until after the list) | `__all__` is therefore a string literal, not a module attribute: `from X import *` exports everything (including the `note_failure` fallback and imported names), and every `__all__`-driven check sees no public API. Three files carry the identical shape, so it is a copy-paste template defect, not three accidents. `audit_compress.py` and `enforcement_harness.py` show the correct shape — docstring closed **before** `__all__` — so the fix is mechanical. |
| M2 | MEDIUM — import-time side effect | `cd4_pipeline.py` L67–72 | `subprocess.run([sys.executable, "-m", "nuitka", "--version"], timeout=10)` at module import | Any importer pays up to a 10-second blocking subprocess at import time, and the probe uses `sys.executable` rather than the interpreter the build will actually run under. `NUITKA_AVAILABLE` is only a convenience flag; the probe's result is already recomputed per pipeline instance (`self.nuitka_available = NUITKA_AVAILABLE`). |
| L1 | LOW — deliberate interface no-op | `cd3_exporter.py::SQLiteSpanExporter.shutdown` and `::force_flush` | bodies are a docstring only (no statement at all) | Documented ("No-op for SQLite exporter", "we write synchronously") and required by the OTel `SpanExporter` interface. Recorded for completeness, not as a defect. |
| L2 | LOW — inert statement | `cd3_exporter.py::__main__` block, first statement `pass` | `pass` before the sys.path setup | Harmless; listed because it is the literal no-op shape the sweep was asked to find. |

## Checked and NOT a defect (so the class is not just asserted)

- `cd3_exporter.py::SQLiteSpanExporter.export` — `except Exception: print(...) ; return SpanExportResult.FAILURE`. Returns a **distinguishable** failure value, so the caller can see it; not a silent default. This is the class the repo's scanner exists for, and it is handled.
- `cd3_exporter.py::configure_otel_tracing` — `except Exception` around `set_tracer_provider` calls `note_failure("cd3_exporter:L332", None)` and falls through to the already-installed provider. Recorded, not swallowed.
- `cd2_verifier.py::serialize_solver_result` — the module carries a **fixed** instance of this defect class: the old bare `except` that replaced a failed model extraction with `{}` now sets `model_values_error` and calls `note_failure`. Worth naming because it shows the intended remediation shape (`output["model_values_error"] = "%s: %s"`), and because a reader finding the comment block will otherwise think it is still live.
- `forecast_baselines.py::ar1_forecast` — `den = sum((x - mx) ** 2 for x in xs) or 1e-9` is a guard, not a silent substitution: when every `x` is equal the numerator is also 0, so `b == 0.0` and the forecast degrades to the mean. Verified by algebra, not by running.
- The `def note_failure(...): pass` fallback in ~8 modules — a **function** whose body is `pass` under `except ImportError`. It is a documented stdlib-only fallback and is not the scanner's `silent_except_pass` shape (that rule matches `except` handler bodies, not function defs).

## Candidates — NOT confirmed (search tooling down, so absence is unproven)

| # | path::symbol | why it is a candidate | what would settle it |
|---|---|---|---|
| C1 | `cd3_exporter.py::_reload_paths` | Defined to recompute the cached `DB_PATH`/`TELEMETRY_DB_PATH` after `AZAZAEL_MEMORY_DIR` changes, and `_get_db_dir`'s docstring calls itself "the resolver a caller uses after redirecting `AZAZAEL_MEMORY_DIR`". If nothing calls it, the cache never refreshes and the documented redirect path is inert. | a working repo-wide search for `_reload_paths` |
| C2 | `cd4_pipeline.py::get_nuitka_incompatible_items` | Docstring: "Useful for pytest_collection_modifyitems to report how many tests will be skipped". A helper with no caller is decoration; the same module's `register_nuitka_marker` has a documented conftest call site. | check `conftest.py` for both symbols |
| C3 | `cd3_exporter.py::query_unified_trace` | `LEFT JOIN … WHERE s.trace_id = ? AND m.event_type IS NOT NULL` — the `IS NOT NULL` predicate discards exactly the rows a LEFT JOIN preserves, so a span with no matching memory row never appears. | intent: either the predicate is deliberate (only unified rows wanted) or it defeats the LEFT JOIN |

## What the coordinator should act on

H1 and H2 are the two that meet the brief's bar — they do not reach a live caller
with the behaviour they advertise. H1 is a **gate that passes without running**;
H2 is a **reader that cannot see the writer's data**. M1 is mechanical (three
files, move `__all__` below the closing `"""`). Everything labelled CANDIDATE
needs a working search before anyone acts on it, and the un-swept surface
(105 files, plus every `src/CORE/` subpackage except `WORMS/`) is where the rest
of this class will be.
