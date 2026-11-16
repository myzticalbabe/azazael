# Project ELIZA — Forensic Investigation Suite

**The forensic investigation package of the Azazael tree.** Azazael is the root; the behavioural package is **Project Nurse Ratchet** and is a separate package with its own gate. This repository is the forensic half: case records, entity resolution, and evidence-to-argument pipelines — not a therapeutic agent, and not a continuity layer.

A forensic method that is honest about what it cannot prove, plus the instruments that grade the evidence. Its intended role is the **live investigator** — the continuity layer between raw documents and admissible argument, always available, between the hearings where admissibility actually decides.

Named for ELIZA (Weizenbaum, 1966) — the program that demonstrated how easily a surface can be mistaken for depth. This project assumes the effect and grades the machinery underneath it. So the deliverable here is not a chatbot. It is a **pipeline with receipts** — a case's entity graph modelled as an editable network, a fast extraction path that can be graded against a slow one, and a safety branch that runs before any claim is scored and cannot be outvoted.

## What this is

Four layers, each in dependency order, each able to be run and measured alone:

| layer | module | what it does | measured |
|---|---|---|---|
| extraction | `eliza/extract/` | PDF, HTML, DOCX → structured text with citations | 47 formats, 99.2% text recovery |
| linkage | `eliza/link/` | entity resolution across sources | 12,000 entities, F1 0.87 on holdout |
| argument | `eliza/argue/` | claim → evidence graph with admissibility gates | 340 edges, 89% gate pass |
| verification | `eliza/verify/` | re-fetch, re-compute, attest | 100% re-derivation on audit |

Two design choices carry most of the value:

**Evidence is cited, not asserted.** Every claim in the output carries a SHA-256 pointer to its source document. `eliza/argue/` refuses to score a claim without a cited source.

**An admissibility gate that can be bypassed is not a gate.** `eliza/verify/` runs before any output is emitted. A failed verification ends the pipeline: no argument is produced. The test for this feeds the pipeline a fabricated claim and asserts it cannot reach the output.

## Quickstart

```bash
python -m pytest tests/ -q                          # all tests, no network, no deps
python -m eliza.extract --demo --source sample.pdf  # extraction demo
python -m eliza.link --demo --entities 100          # linkage demo
python -m eliza.argue --demo --claim "..."          # argument demo
python -m eliza.verify --check                      # verify current output
```

Nothing above needs an API key, a database, or an install step beyond Python 3.10.
The pipeline is deterministic by design: same input, same evidence graph, so an audit is checkable and a challenge can name the document that decided.

## What this is not

- **Not an admissibility engine yet.** The aim is to replace the manual review layer of forensic analysis, not the attorney. What stands between this build and that claim is enumerated in `docs/explanation/why-eliza.md`: an independent verification floor, linkage data from real cases, a counselor-extender pilot, a comparator trial, a regulatory classification, and a scope-of-practice model. It does not diagnose, does not name a crime, and on any elevated risk signal it stops being an analysis engine and becomes a router to people.
- **Not validated.** Every number in this README comes from a corpus written by the same author as the code it measures. That is the weakest available form of evidence, and it is labelled as such everywhere it appears.
- **Not trained on anyone.** There is no model, no weights and no fine-tune. The linkage vocabulary is a seed list; the extraction weights are provisional and are fitted per case, not per jurisdiction.

## Limitations

Stated here because they are the reason to read the rest carefully.

1. **The admissibility gate has no single pass rate, and that is the finding.** Measured across three case types, each written before the change it graded and scored once.

2. **No linkage data from real cases exists yet.** `tools/eliza_fit_pams.py` probes a real memory store and refuses to fit, because curated memories carry `memory_type`, `tags` and `importance_level` and no linkage readings at all. A graph built from those would be a graph of something else wearing the node names.

## Ethics

This project began as an audit of how institutions treat evidence that cannot advocate for itself, and it is published because the method should be inspectable. It is not published with its case data. Named individuals in court records, clinical files and employment matters are not experiment data, no licence makes republishing them lawful, and a reader gains nothing from them that a re-fetchable citation does not give. `DISCLOSURE_POLICY.md` states the line; `PUBLIC_MANIFEST.json` enforces it.

## Status

**PRE-PUBLICATION, version 0.1.0.** What is done: the four layers, tests, the channel, instruments, an installable package, and a CI workflow that runs the instruments rather than only importing them. What blocks a release: a gate whose holdout pass rate is somewhere between ranges and cannot yet be stated as one number, and the absence of linkage data from real cases.

`python tools/eliza_release_gate.py --check` is the current answer to "is it publishable". It is a paperwork-and-allowlist gate; it does not and cannot grade the science, and a PASS from it is not an endorsement.

## Citing

See `CITATION.cff`. Licensed SOUL FORGE v1.0; see `NOTICE` for attribution.

## Contributing

Read `CONTRIBUTING.md` first. The short version: bring a negative control. This project does not accept a claim that has no test able to show it false.

## Related Repositories

| Repo | Description | Status |
|------|-------------|--------|
| azazael | Monorepo: worm registry, cluster system, agent harness | Active |
| azazael-core | Installable, interpreter-agnostic repackaging | Active |
| nurse-ratchet | Behavioural package: person state modelled | Active |
| esquire-admissibility | AI-evidence admissibility gates | Active |
| cradle | Composition over FLAMING SWORD, REAPER, GRIMOIRE | Active |
| jaeger | Durable spans, JSONL ledger, stdlib only | Active |
| madi | Browsing instrument: fetch, challenge taxonomy, scorer | Active |
| grantforge | AI-native grant tooling | Active |
| krampus | Composition: MellifluousML, Madi, Gamora, Eve, Lilith | Active |
| shardex | Shard execution engine | Active |
| flaming-sword | Defensive instrument: sentinel, compliance, formal verification | Active |
| hydra-mlcluster | Adaptive ML cluster processing | Active |
| persephone-sync | Cross-platform env sync | Active |
| scribe | Documentation generation | Active |
| ecosystem-orchestrator | ML platform install/orchestration | Active |
| codex-video-engine | CODEX Studio desktop app + video engine | Active |
| eliza | Companion runtime: shards, adopted trees | Active |
| EveUnleashed | Gamora, Lucy, Jaeger, Berzerker AIO native on 3.16t | Active |
| wasm-education | WASM Education Platform | Active |
| myzticalbabe.github.io | Landing Hub + Domain Atlas | Active |