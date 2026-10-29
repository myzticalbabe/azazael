# Multi-lingual Shards Review — Skills & Tools as Shards (2026-10-29)

> SCOPE (owner-confirmed): multi-lingual = GO / RUST / PYTHON only.
> Human linguistics explicitly OUT OF SCOPE.

## 1. What exists today

### 1a. Shard pattern (arena-64n/shard_node.py)
The only true shard implementation in the repo. "Frankenstein shard node":
- `SHARDS = {shard-a, shard-b, shard-c, synthesis}` — each shard is one evolved
  candidate wired as a callable module behind a cost-aware router.
- `route(budget)` — top-1 router: fast/balanced/peak → (shard, hidden) from a
  measured scale sweep. `synthesis` (C base + B early-stopping graft + A
  discipline) is the production default.
- `run_shard(name)` returns JSON-serializable results, no weights.
- `self_test()` cold-recomputes, asserts thresholds, checks determinism.
- Rule: no result cache (a gate that passes without re-running proves nothing).

This is training-logic sharding, not multilingual — but the shape
(SHARDS dict + router + budgets + synthesis default + self-test) is directly
reusable for skills/tools.

### 1b. Human-locale systems — OUT OF SCOPE (noted, not pursued)

Per owner direction, human linguistics (archify `meta.locale`, armada 9-locale
i18n) is not part of this review. Listed here only so nobody re-investigates
it under the "multi-lingual" heading. The remainder of this document covers
GO / RUST / PYTHON exclusively.

~~Human-locale detail removed from scope.~~ Original notes (superseded):
1. **archify skill** (`.agents/skills/archify/SKILL.md:82`): `meta.locale`
   controls only renderer-owned Viewer UI (`en` / `zh-CN`); every other
   language omits `meta.locale` and the Viewer falls back to English.
   **The renderer never translates authored content.** Contract lives in
   `references/authoring-contract.md`.
2. **armada dashboard i18n** (`armada/archive/I18N.md`, shipped per CHANGELOG):
   locales `en/es/zh-Hans/zh-Hant/yue-Hant/ja/de/fr/it`; shared catalog
   `src/Armada.Server/wwwroot/i18n/armada.json` consumed by both React
   (`i18n/runtime.ts`) and legacy (`js/i18n.js`) runtimes; locale resolution
   user-selection → localStorage (`armada_locale`) → profile → navigator →
   fallback `en`; design rules (no hard-coded strings, no fragment
   concatenation, semantic payloads persisted, `lang`+`dir` always set).

### 1c. Skills & tools inventory (measured)
- Skills: **1247** entries in `.agents/skills/`; each is a `SKILL.md` package
  (frontmatter `name/description/metadata` + markdown body). All sampled
  skills are **English-only**. Logical shard groupings already exist by naming:
  `azazael-worms-{core,data,devops,monitor,security}`, `azazael-pkg*` (~800
  package skills), `azazael-pkg314t-*`, `azazael-bin-*`, `azazael-inference-*`,
  `azazael-devtools-*`, `azazael-tool-*`.
- Tools: **37** top-level `tools/*.py` plus subdirs (`cli/`, `server/`,
  `quantize/`, etc.). Each is already an importable/callable module — i.e.
  shard-shaped, but with no manifest, no router, no self-test contract.

## 2. Industry pattern (web search, Oct 2026)
Agent Skills are the standard modular capability unit: SKILL.md packages with
progressive disclosure (metadata → instructions → scripts/resources on demand).
Consensus guidance is **modular over mega-skills**: small discoverable units
beat massive system prompts; a router/lazy-loader selects the minimum set per
task. This matches the arena-64n top-1 router intuition at the knowledge layer.

## 3. Can skills & tools become shards? Yes — two orthogonal axes

### Axis A — Domain shards (recommended, cheap)
Group the 1247 skills into ~12–15 shard manifests mirroring the existing
`azazael-{worms-*,inference-*,devtools-*,tool-*,pkg,pkg314t,bin-*}` families.
Each shard gets an arena-style manifest:

```python
SHARDS = {
  "conventions": {"skills": ["azazael-conventions", "azazael-git", ...],
                  "notes": "always-on discipline pack"},
  "inference":   {"skills": ["azazael-inference*", ...]},
  ...
  "synthesis":   {"skills": [...minimal production default...]},
}
```

Router: keyword/budget top-1 (fast = 1 skill, balanced = shard pack,
peak = full family). Reuse `run_shard`/`self_test` shape: shard self-test
loads each SKILL.md, validates frontmatter, asserts no dangling
Related-Skills links.

### Axis B — Human-locale shards — REMOVED FROM SCOPE (owner: GO/RUST/PYTHON only)
Follow the armada model, constrained by the archify contract:
- Canonical content stays **English** (single source of truth).
- Locale shard = `<skill-id>.<bcp47>/SKILL.md` (e.g.
  `azazael-conventions.zh-Hans/SKILL.md`), only for piloted shards.
- Shared per-shard catalog (armada.json shape:
  `{defaultLocale, supportedLocales[], locales:{code:{terms,phrases}}}`).
- Fallback chain identical to armada; renderer never translates (archify rule).
- CI: missing-key + dead-key checks (armada Workstream 12), plus
  pseudo-locale expansion pass (`en-XA` 30–50% expansion, RTL `ar-XB`).

### Why not all 1247 × 9 locales
Full matrix ≈ 11k files. Translation, review, and drift cost dominate.
Pilot 2–3 high-traffic shards (conventions, testing, tool-dynamic-logger),
prove the fallback + CI loop, then expand by measured usage.

## 4. Concrete proposal
1. `shards/skill_shards.py` — SHARDS manifest over existing skill ids
   (no skill moves), `route(task)` keyword router, `--list/--self-test/--run`.
2. `shards/locale_registry.py` — port armada's registry shape
   (code, native label, dir, fallback, font hints) for skills.
3. ~~Pilot locale shards~~ REMOVED — human linguistics out of scope.
4. CI gates: frontmatter validity, missing/dead keys, hard-coded-string lint
   for piloted locales, pseudo-locale render check.
5. Tools: wrap the 37 `tools/*.py` in the same manifest with
   `execute()` entry points and per-tool self-tests (cold recompute,
   JSON-serializable results — arena rules).

## 5. Open questions for owner
- Is `synthesis` (minimal production skill pack) a wanted default, or is
  lazy per-skill loading sufficient?
- Which 3–5 hot-path tools justify Go/Rust shard implementations first
  (gateway pair already done — what is next: benchmarks, parsers, runners)?

## 6. Polyglot dimension: GO / RUST / PYTHON (added per owner note)

"Multi-lingual" here = programming languages, not human locales — and the
repo already proves the pattern works:

- **Python** (host/orchestration): 1247 `SKILL.md` packages + 37 `tools/*.py`
  + `azazael/src/INTERPRETERS/{go_runner,rust_runner}.py`. Python is the
  shard host: it owns the manifest, the router, and the self-test harness.
- **Go** (`gateway-go/main.go`, stdlib only): OpenAI-compatible front end —
  route-by-model-substring, round-robin, failover, SSE relay, 15s health
  probes. `GoRunner` (15 methods + CLI: run/code/build/test/vet/init/fmt,
  cross-compile GOOS/GOARCH, go.mod detection) compiles and runs Go shards
  from Python via subprocess with structured `GoResult` (success/stdout/
  stderr/duration_ms/binary_path/parsed errors).
- **Rust** (`gateway/src/main.rs`, axum+tokio+reqwest): byte-identical
  behavior contract to the Go gateway (same routes, same pick/probe/forward
  semantics, same 15s loop). `RustRunner` (12 methods + CLI: run/code/check/
  build/test/new/fmt, cargo detection, rustc editions 2015–2024) with
  structured `RustResult`.

The two gateways are the existence proof that **one shard contract can have
Go, Rust, and Python implementations behind a shared interface** — exactly
the arena-64n `SHARDS = {name: {train fn, source, notes}}` shape, with the
"train fn" generalized to an `execute()` entry point per language.

### Shard-per-language layout (proposal)

```text
shards/<shard-name>/
  shard.py   # Python implementation (default; always present)
  shard.go   # Go implementation (optional; via GoRunner.run_file)
  shard.rs   # Rust implementation (optional; via RustRunner.run_file)
  SHARD.md   # contract: inputs/outputs/JSON schema + which lang is canonical
```

- Router prefers the canonical lang per shard (perf-critical → Rust/Go via
  runners; orchestration/glue → Python in-process), falls back to Python.
- `run_shard(name, lang="auto")` returns JSON-serializable results
  (arena rule: no weights/blobs across the boundary — `GoResult`/`RustResult`
  already serialize this way).
- `self_test()` cold-recomputes per language and asserts cross-language
  output agreement on a golden fixture (the gateway pair is the template:
  same inputs → same routes → same status codes).
- Toolchain absence (`has_go`/`has_rustc` False) is a clean skip with a
  structured toolchain error, not a crash — keep that behavior in the router.

### What this changes in §4
Step 5 becomes: tools get per-language `execute()` entry points where it
pays (gateway already done ×2); everything else stays Python-behind-manifest.
Do NOT rewrite 37 tools × 3 languages — shard the 3–5 hot paths
(gateway, benchmarks, parsers) and leave the long tail Python-only.

## Sources
- `arena-64n/shard_node.py` (SHARDS/router/budgets/synthesis/self-test)
- `.agents/skills/archify/SKILL.md:82,94` (meta.locale, authoring-contract)
- `armada/archive/I18N.md` + `armada/CHANGELOG.md` + `i18n/armada.json`
- Web: awesome-agent-skills, Agent Skills Claude docs, Spring AI agent-skills,
  mega-vs-modular skills, multilingual backend/i18n guides (Oct 2026)
