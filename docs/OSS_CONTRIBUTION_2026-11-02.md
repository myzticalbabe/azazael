# Open-source contribution — determination and justification (2026-11-02)

The question was which open-source projects we should contribute to. The answer that survives
scrutiny is narrow, and the narrowness is the point: **one commitment (OpenTelemetry semantic
conventions for agent delegation), one conditional (MCP client behaviour, only after it reproduces
outside this tree), and three explicit refusals** with the reason each was refused.

## The rule used to decide

A candidate passes only if all four hold:

1. **We hit the defect ourselves, reproducibly, without this tree.** A defect that needs `azazael`
   to appear is not a defect upstream can accept.
2. **The change is small and standard-shaped** — a doc correction, a test, a schema field, a
   20-line patch. Large patches make us a maintainer.
3. **The project takes outside contributions** and has a visible process.
4. **We do not end up owning the thing we depend on.** A feature we need and upstream will not
   maintain is a fork, and a fork is a cost, not a contribution.

Every refusal below fails at least one test, and the failing test is named. That is deliberate: "we
are not contributing to X" with the test quoted is a decision someone can revisit, while "not a
priority" is a mood.

## Candidates

| project | what we actually measured | test that decides it | verdict |
| --- | --- | --- | --- |
| **OpenTelemetry semantic conventions (GenAI / agent)** | AOA already produces the data: `DelegationSpec(instruction, context, tools, model)` — selection reason, evidence snapshot, `arm_id`+`capability`, model hint — and `ArmResult` with `provenance` (`arm_declared` vs `router_observed`), `stale_after_s`, `age_s`. Nothing in the tree consumes it as telemetry, because there is no shared vocabulary for "a delegation happened, here is why, and here is whether the answer was stale". | passes 1–4: the gap is in the standard, not in our code; the artefact is a docs patch (attribute table); OTel has a public process; the schema stays theirs | **YES — draft now, PR after `jaeger-000`** |
| **`modelcontextprotocol/python-sdk`** | This tree records that its client "reads `mcpServers` but discards the MCP `initialize` instructions field, so no MCP server can push to the agent". Also pinned at `mcp 1.22.0` (v1) while v2 is in beta. | fails **1** today: never reproduced against a stock client, only observed in ours | **CONDITIONAL** — reproduce first (row 47213) |
| **pytest** | `pytest-of-clint` was **103 MB**, removed today. Docs state retention is the **last 3 runs** — documented behaviour, not a defect. The size is our fixtures writing large artefacts. | fails **1**: no defect, only our output volume. A `--basetemp-retention` flag would fail **4** — we would own it | **NO** — fix locally with `--basetemp` in a pruned path |
| **basedpyright** | Type gate of record (1.40.1). Zero reproducible false positives captured in this session. | fails **1**: nothing to report yet | **NOT YET** — a repro issue becomes high-value the moment one is captured |
| **Jaeger** | Consumed only as an OTLP ingest target; we have never run it. The only "jaeger" in the tree is the mockup label `tracing: jaeger/zipkin`. | fails **1**: no defect hit; we would be contributing to software we have not built against | **NO** |
| **graphify / archify skills** | Vendored community skills; local patches would be lost on reinstall. | provenance unverified this session | **UNKNOWN** — check whether a local patch exists before claiming anything |
| **Free-threaded CPython wheels** (`cp314`/`cp315t` rejections) | Real, recurring: the same-version GIL build had to be laid out as a sidecar because wheels were refused. | passes **1**, fails **2**: we cannot contribute wheels; the plausible artefact is per-project build-failure reports | **SECOND-ORDER** — evidence only, when it recurs |

## The one commitment, stated so it can be judged

Draft the semantic-convention fields for **agent delegation**, using AOA as the instance: selection
reason, evidence reference, tool address, model hint, result provenance, result staleness. The test of
whether it is a good contribution is not that OTel accepts it — it is that the **field set survives an
operator asking "was this delegation right?"** If a proposed attribute does not help answer that, it
does not belong in the convention, and probably does not belong in `DelegationSpec` either.

That second half is the real value. Sending our schema through an external review is a forcing
function: a field that a standards body cannot justify is a field we should not be carrying, and we
would rather learn that from a reviewer than from a dashboard nobody reads.

## Why so few

Because contribution cost is paid in a currency this box is short of — attention, and disk. A merged
docs patch costs a review cycle; a merged feature costs a maintenance commitment measured in years.
The projects we use most heavily (`pytest`, `basedpyright`, `puppeteer`) are exactly the ones where we
have hit configuration problems rather than defects, and reporting our misconfiguration upstream is
how a maintainer learns to distrust a reporter.

The direction that would change this answer: when `jaeger-003` ships an exporter, we will have a
consumer for the vocabulary and a reason for the standard to exist — at which point the same
contribution becomes far stronger, and a second one (an exporter in `opentelemetry-python-contrib`)
becomes available and passes all four tests.
