#!/usr/bin/env python3
"""Replace the six scaffolds' copy-pasted Nurse_Ratchet metadata with their own.

Why this exists
---------------
The public-standards pass added CHANGELOG.md, HARDWARE.md, MANIFEST_NOTES.md and
certification.json to six trees by copying Project_Nurse_Ratchet's files verbatim.
The copies did not just carry a stale title: PUBLIC_MANIFEST.json declared
"project": "nurse-ratchet" and an allowlist rooted at ../src/PSYCHE, which *does*
resolve from every one of those trees. A publicize run there would have shipped the
clinical package into a WebAssembly compiler.

This script writes the replacement files from a per-tree table. Every `done: true`
criterion cites a path that exists in that tree; the percentage is computed here
rather than typed, and `--check` re-derives it so the number cannot drift from the
criteria. Nothing is claimed that was not verified in the tree on 2026-11-15.

    python tools/_fix_scaffold_metadata.py --write
    python tools/_fix_scaffold_metadata.py --check
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATE = "2026-11-15"

COMMON_NEVER_SHIP = [
    {
        "glob": ".requiem/*",
        "why": "requiem writes the last words and frames of a dying process; those records name local paths and are accountability data, not shippable content",
    },
    {
        "glob": "*/node_modules/*",
        "why": "reinstalled from package.json; shipping it would pin whatever resolution happened on one machine",
    },
    {
        "glob": "*/__pycache__/*",
        "why": "bytecode, not source",
    },
    {
        "glob": ".env*",
        "why": "credentials do not ship",
    },
]

COMMON_DENY = ["node_modules", "__pycache__", ".requiem", ".env"]


def req(rid, title, short, weight, required, criteria):
    return {
        "id": rid,
        "title": title,
        "short": short,
        "weight": weight,
        "required": required,
        "criteria": criteria,
    }


def crit(text, path=None, note=None):
    if path is None:
        return {"text": text, "done": False, "evidence": ""}
    return {"text": text, "done": True, "evidence": {"path": path, "note": note or ""}}


# --------------------------------------------------------------------------- trees
TREES = {
    "WASM_Compiler": {
        "slug": "wasm-compiler",
        "title": "Project WASM Compiler",
        "summary": (
            "The WebAssembly toolchain of the Azazael tree: a Rust crate that compiles "
            "cosine-similarity kernels to wasm, a Node bench that times them, and the "
            "measurement record that separates what SIMD bought from what removing "
            "per-element heap reads bought."
        ),
        "manifest_note": (
            "This tree publishes in place. There is no `tools/publicize.py` and no second "
            "source root, so there is nothing to materialise: the tracked tree is the "
            "artifact. That also means no file-level allowlist is enforced here, and the "
            "`ship` array is therefore empty rather than a list of paths nothing reads."
        ),
        "requirements": [
            req(
                "build_is_reproducible",
                "A build that another machine can repeat",
                "repeatable build",
                2,
                True,
                [
                    crit(
                        "A crate is declared that produces a wasm cdylib",
                        "tools/RUST_WASM/Cargo.toml",
                        'crate-type = ["cdylib"]; wasm-bindgen 0.2 + js-sys 0.3; opt-level 3, lto = true, codegen-units = 1',
                    ),
                    crit(
                        "A SIMD target feature can reach rustc",
                        "tools/RUST_WASM/.cargo/config.toml",
                        "without a .cargo/config.toml no target-feature=+simd128 reaches the compiler, which the measurement record names as one of the original defects",
                    ),
                    crit("A build from a clean checkout is recorded with its exact tool versions"),
                ],
            ),
            req(
                "claim_is_attributable",
                "A number that can be attributed to the build that produced it",
                "attributable numbers",
                3,
                True,
                [
                    crit(
                        "A benchmark harness ships with the crate",
                        "tools/RUST_WASM/bench.mjs",
                        "node bench.mjs <pkg>: timed calls over Float32Array pairs, warm-up separated from measurement",
                    ),
                    crit(
                        "Each figure is separated by the build that produced it",
                        "tools/RUST_WASM/MEASURED_2026-11-01.md",
                        "before / copy+scalar / copy+SIMD kept apart: 16.688 -> 0.892 -> 0.523 us at 1536 dim, 20,000 timed calls after 2,000 warm-up",
                    ),
                    crit("A second machine reproduces the ordering"),
                ],
            ),
            req(
                "learner_can_follow",
                "An explanation, not only a result",
                "explained",
                2,
                False,
                [
                    crit(
                        "The record says why the old name was wrong, not only what the new number is",
                        "tools/RUST_WASM/MEASURED_2026-11-01.md",
                        "names three independent reasons no vectoriser could have helped, including that FP addition is not associative",
                    ),
                    crit("A test fails when the SIMD path silently falls back to the scalar body"),
                ],
            ),
        ],
        "hardware": (
            "## What this component needs\n\n"
            "| Component | Requirement | Source |\n"
            "|---|---|---|\n"
            "| Rust | edition 2024; `wasm32-unknown-unknown` target | `tools/RUST_WASM/Cargo.toml` |\n"
            "| wasm target | `target-feature=+simd128` via `.cargo/config.toml` | `tools/RUST_WASM/.cargo/config.toml` |\n"
            "| Node | any version that runs ES modules | `tools/RUST_WASM/bench.mjs` |\n"
            "| GPU | none | the workload is a 1536-dimension `Float32Array` dot product |\n\n"
            "## What was measured, and on what\n\n"
            "`tools/RUST_WASM/MEASURED_2026-11-01.md` records Node 24.14.0, wasm-pack 0.15.1\n"
            "and rustc 1.95.0. Those are the only version claims this tree makes, and they come\n"
            "from the record rather than from this document.\n\n"
            "The record does **not** name the CPU or the memory, so it is not a citation for\n"
            "the development-machine table below — it is a citation for the toolchain only.\n"
        ),
        "changelog_note": (
            "Replaced a `certification.json`, `HARDWARE.md`, `MANIFEST_NOTES.md` and\n"
            "`CHANGELOG.md` that had been copied wholesale from `Project_Nurse_Ratchet`. The\n"
            "copied manifest declared `\"project\": \"nurse-ratchet\"` and an allowlist rooted at\n"
            "`../src/PSYCHE`, which resolves from this tree; a publicize run would have copied\n"
            "the clinical package into the wasm compiler. All four files now describe this tree\n"
            "and cite paths that exist in it."
        ),
    },
    "CODEX_VideoEngine": {
        "slug": "codex-video-engine",
        "title": "Project CODEX Video Engine",
        "summary": (
            "The video engine of the Azazael tree: HTML scene templates, a Puppeteer capture "
            "path and an FFmpeg encode step that turn a template into a rendered clip, plus the "
            "CODEX Studio desktop app that drives them."
        ),
        "manifest_note": (
            "This tree publishes in place. `tools/CODEX` is both the source and the artifact, "
            "and it carries 500+ files including rendered reports and captured artifacts, which "
            "is exactly the shape a per-file allowlist exists to make you think about. None is "
            "written yet, so `ship` is empty and the tree as a whole is the artifact."
        ),
        "requirements": [
            req(
                "render_path_exists",
                "A capture path that runs, not one that is described",
                "capture path",
                3,
                True,
                [
                    crit(
                        "A browser-capture dependency is declared",
                        "tools/CODEX/package.json",
                        "puppeteer ^19.0.0 and puppeteer-screen-recorder ^3.0.6 — capture is done by a browser, not by drawing frames in PIL",
                    ),
                    crit(
                        "A scene template exists that a session can be injected into",
                        "tools/CODEX/AZAAZEL_VIDEO.html",
                        "the template is HTML and data, so a session's content is injected rather than edited into the markup",
                    ),
                    crit("The encode step is a script in this tree rather than a step in a document"),
                ],
            ),
            req(
                "output_is_verifiable",
                "An output whose parameters are asserted",
                "verifiable output",
                3,
                True,
                [
                    crit(
                        "A test covers session injection into a template",
                        "tools/CODEX/test_inject_session_cain.py",
                        "exercises the injection path a render depends on",
                    ),
                    crit("A rendered artifact is recorded together with the encode parameters that made it"),
                    crit("Frame rate and duration are asserted rather than eyeballed"),
                ],
            ),
            req(
                "desktop_app",
                "The desktop app can be built by someone else",
                "desktop app",
                2,
                False,
                [
                    crit(
                        "A packaging configuration for the desktop app exists",
                        "tools/CODEX/TESTING/pyproject.toml",
                        "declares the Python side of the app",
                    ),
                    crit("A built binary exists in the tree"),
                ],
            ),
        ],
        "hardware": (
            "## What this component needs\n\n"
            "| Component | Requirement | Source |\n"
            "|---|---|---|\n"
            "| Node | any LTS; ES modules | capture dependencies in `tools/CODEX/package.json` |\n"
            "| Chromium | downloaded/managed by Puppeteer | `puppeteer` ^19 |\n"
            "| Python | the version in `tools/CODEX/TESTING/pyproject.toml` | that file |\n"
            "| RAM | must hold whole video frames; capture is memory-bound, not CPU-bound | inferred from the capture model |\n"
            "| GPU | not required; there is no hardware-encode step in this tree | — |\n\n"
            "## What was validated\n\n"
            "Nothing in this file was measured for this document. No render exists in the tree\n"
            "with its parameters recorded, so there is no frame rate, duration or encode setting\n"
            "to quote. The table above states dependencies, not performance.\n"
        ),
        "changelog_note": (
            "Replaced a `certification.json`, `HARDWARE.md`, `MANIFEST_NOTES.md` and\n"
            "`CHANGELOG.md` copied wholesale from `Project_Nurse_Ratchet`. The copied manifest\n"
            "declared `\"project\": \"nurse-ratchet\"` and an allowlist rooted at `../src/PSYCHE`,\n"
            "which resolves from this tree; a publicize run would have copied the clinical\n"
            "package into a video engine. All four files now describe this tree."
        ),
    },
    "EcosystemOrchestrator": {
        "slug": "ecosystem-orchestrator",
        "title": "Project Ecosystem Orchestrator",
        "summary": (
            "The orchestration layer of the Azazael tree: ML platform install and lifecycle, "
            "dependency resolution and health monitoring, plus the ADLP fusion and orchestrator "
            "modules and the assistant log protocol they publish through."
        ),
        "manifest_note": (
            "This tree publishes in place. The payload is `tools/ORCHESTRATION`, which is both "
            "source and artifact. No `tools/publicize.py` exists, so no allowlist is enforced\n"
            "and `ship` is empty rather than a list of paths nothing reads."
        ),
        "requirements": [
            req(
                "service_lifecycle",
                "A lifecycle that is managed rather than assumed",
                "lifecycle",
                3,
                True,
                [
                    crit(
                        "An orchestrator entry point exists",
                        "tools/ORCHESTRATION/ADLP_MLOrchestrator.py",
                        "the module that starts and stops managed ML platforms; this is the entry point itself, not a plan for one",
                    ),
                    crit(
                        "A fusion core exists",
                        "tools/ORCHESTRATION/ADLP_FusionCore.py",
                        "combines platform signals into a single scheduling decision instead of leaving it to each caller",
                    ),
                    crit("Every managed service has a health check wired to the orchestrator"),
                ],
            ),
            req(
                "changes_are_tested",
                "A change that is checked before it is deployed",
                "tested",
                3,
                True,
                [
                    crit(
                        "A test script exists",
                        "tools/ORCHESTRATION/scripts/test_enhancements.py",
                        "exercises the enhancement path and is run by hand; the open criterion below is the CI one",
                    ),
                    crit("The test runs in CI on every push"),
                ],
            ),
            req(
                "protocol_is_specified",
                "A protocol that is a contract, not a convention",
                "protocol",
                2,
                False,
                [
                    crit(
                        "The assistant log protocol is implemented",
                        "tools/ORCHESTRATION/AssistantLogProtocol.py",
                        "assistant records go through one protocol module rather than ad-hoc logging at each call site",
                    ),
                    crit("The record format is written down as a schema an outsider can validate against"),
                ],
            ),
        ],
        "hardware": (
            "## What this component needs\n\n"
            "| Component | Requirement | Source |\n"
            "|---|---|---|\n"
            "| Python | 3.10+ | f-strings and `from __future__` usage across `tools/ORCHESTRATION` |\n"
            "| ML platforms | whatever the orchestrator is told to manage; none is bundled | `tools/ORCHESTRATION` |\n"
            "| Network | required at run time: install and health checks talk to the platforms | — |\n"
            "| GPU | not needed by the orchestrator itself | it schedules work, it does not run it |\n\n"
            "## What was validated\n\n"
            "Nothing here was measured. No dependency manifest (no `requirements.txt`, no\n"
            "`pyproject.toml`) exists in this tree, so the Python version above is read from the\n"
            "source's syntax rather than declared. That is a gap, not a specification.\n"
        ),
        "changelog_note": (
            "Replaced metadata copied wholesale from `Project_Nurse_Ratchet` — including a\n"
            "manifest declaring `\"project\": \"nurse-ratchet\"` with an allowlist rooted at\n"
            "`../src/PSYCHE`, a path that resolves from this tree. All four files now describe\n"
            "this tree."
        ),
    },
    "HYDRA_MLCluster": {
        "slug": "hydra-mlcluster",
        "title": "Project HYDRA MLCluster",
        "summary": (
            "The adaptive ML cluster of the Azazael tree: a launcher, a protocol module and an "
            "`ml_platforms` package that starts model platforms, runs harnesses and watches "
            "their health across heterogeneous compute."
        ),
        "manifest_note": (
            "This tree publishes in place: `tools/HYDRA` is both source and artifact, and no\n"
            "`tools/publicize.py` exists to copy anything elsewhere. `ship` is empty because no\n"
            "allowlist is enforced; `ml_config.ini` and `datasets.json` are the files that decide\n"
            "what a run touches, and they are the first thing an allowlist would have to pin."
        ),
        "requirements": [
            req(
                "cluster_can_start",
                "A cluster that starts from configuration",
                "cold start",
                3,
                True,
                [
                    crit(
                        "A launcher exists",
                        "tools/HYDRA/hydra_launcher.py",
                        "starts the platform set named in ml_config.ini",
                    ),
                    crit(
                        "Cluster configuration is data rather than code",
                        "tools/HYDRA/ml_config.ini",
                        "the platform set and its settings live in an ini file, so changing clusters does not mean changing code",
                    ),
                    crit("A cold start is recorded, naming the platforms it brought up"),
                ],
            ),
            req(
                "work_is_measured",
                "A run whose result can be attributed",
                "measured run",
                3,
                True,
                [
                    crit(
                        "A test harness exists",
                        "tools/HYDRA/ml_test.py",
                        "drives a run and records what happened, which is what produced the stored result below",
                    ),
                    crit(
                        "A run result is stored in the tree",
                        "tools/HYDRA/10min_test_results.json",
                        "a ten-minute run's results, kept as data next to the code that produced them",
                    ),
                    crit("The stored result names the configuration it was produced under"),
                ],
            ),
            req(
                "platform_health",
                "Unhealthy platforms handled rather than ignored",
                "health",
                2,
                False,
                [
                    crit(
                        "A health monitor exists",
                        "tools/HYDRA/ml_platforms/health_monitor.py",
                        "watches platform health from inside the ml_platforms package; the open criterion is what it does with a bad answer",
                    ),
                    crit("An unhealthy platform is drained mid-run instead of dropped"),
                ],
            ),
        ],
        "hardware": (
            "## What this component needs\n\n"
            "| Component | Requirement | Source |\n"
            "|---|---|---|\n"
            "| Python | 3.10+ | `tools/HYDRA/*.py` |\n"
            "| ML runtimes | TensorFlow and others, discovered at run time | `tools/HYDRA/find_python_with_tensorflow.bat` |\n"
            "| GPU | optional; the cluster is meant to span heterogeneous compute | README |\n"
            "| Disk | must hold datasets named by `datasets.json` | `tools/HYDRA/datasets.json` |\n\n"
            "## What was validated\n\n"
            "`tools/HYDRA/10min_test_results.json` is a stored run result, but this document did\n"
            "not read it to extract a figure, and the run it came from is not described in the\n"
            "tree with enough detail to repeat it. Treat the stored result as evidence that a run\n"
            "happened, not as a benchmark.\n"
        ),
        "changelog_note": (
            "Replaced metadata copied wholesale from `Project_Nurse_Ratchet`, including a\n"
            "manifest declaring `\"project\": \"nurse-ratchet\"` and an allowlist rooted at\n"
            "`../src/PSYCHE` — a path that resolves from this tree. All four files now describe\n"
            "this tree."
        ),
    },
    "PERSEPHONE_Sync": {
        "slug": "persephone-sync",
        "title": "Project PERSEPHONE Sync",
        "summary": (
            "Cross-platform environment synchronization for the Azazael tree: one library that "
            "resolves paths on Windows and WSL2, a sync manager that moves code and configs "
            "between environments, and a CLI that drives both."
        ),
        "manifest_note": (
            "This tree publishes in place: `tools/PERSEPHONE` is both source and artifact, and\n"
            "no `tools/publicize.py` exists here. `ship` is empty because no allowlist is\n"
            "enforced. The sync topology is the thing an allowlist would have to pin, and it is\n"
            "described in `tools/PERSEPHONE/README.md` rather than in data."
        ),
        "requirements": [
            req(
                "path_resolution",
                "Path translation that is implemented, not shelled out",
                "paths",
                3,
                True,
                [
                    crit(
                        "Windows and WSL path translation lives in the library",
                        "tools/PERSEPHONE/lib/path_manager.py",
                        "converts a Windows path to its WSL mount and back inside the library, so no caller has to shell out to do it",
                    ),
                    crit(
                        "Environment detection exists",
                        "tools/PERSEPHONE/lib/environment.py",
                        "answers which environment it is running in; every sync decision downstream depends on that answer",
                    ),
                    crit("A round-trip test covers a path that exists on only one side"),
                ],
            ),
            req(
                "sync_is_safe",
                "A sync that cannot destroy the thing it is syncing",
                "safe sync",
                4,
                True,
                [
                    crit(
                        "A sync manager exists",
                        "tools/PERSEPHONE/lib/sync_manager.py",
                        "moves code and configs between environments; the open criteria are what it refuses to do",
                    ),
                    crit("A delete is refused unless the operator asked for it by name"),
                    crit("An interrupted sync leaves a state that can be resumed"),
                    crit("The sync is exercised against a dry run in CI"),
                ],
            ),
            req(
                "operator_can_drive_it",
                "An operator interface that is tested",
                "operator CLI",
                2,
                False,
                [
                    crit(
                        "A CLI exists",
                        "tools/PERSEPHONE/bin/persephone_cli.py",
                        "the operator entry point and the only supported way to drive a sync",
                    ),
                    crit(
                        "The declared requirements file is parseable by pip",
                        "tools/PERSEPHONE/requirements_wsl.txt",
                        "ten lines of Python source were filed inside the requirement list, so pip could not parse the file at all; they are commented out as of 2026-11-15. pip now parses it and fails later, on socketio>=0.8.0, which is not a PyPI distribution name (the package is python-socketio). That is a second, open defect.",
                    ),
                ],
            ),
        ],
        "hardware": (
            "## What this component needs\n\n"
            "| Component | Requirement | Source |\n"
            "|---|---|---|\n"
            "| Python | 3.10+ | `tools/PERSEPHONE/lib/*.py` |\n"
            "| OS | Windows and/or WSL2 Ubuntu; the library exists to bridge them | `tools/PERSEPHONE/lib/path_manager.py` |\n"
            "| `rsync`, `ssh` | for the transfer paths | `tools/PERSEPHONE/sync_azazael_wsl.sh` |\n"
            "| GPU | none | this component moves files |\n\n"
            "Note that `tools/PERSEPHONE/requirements_wsl.txt` declares a very wide dependency\n"
            "set — ML, web, database and cloud SDKs — because it was written as an environment\n"
            "manifest for the whole tree, not as this component's own requirements. It is not a\n"
            "statement of what the sync library needs.\n\n"
            "## What was validated\n\n"
            "Nothing was measured. No test file exists in this tree, so the safety criteria above\n"
            "are open by construction rather than by oversight.\n"
        ),
        "changelog_note": (
            "**Fixed** `tools/PERSEPHONE/requirements_wsl.txt`: ten lines of Python source\n"
            "(`wsl_to_windows`, `windows_to_wsl`) were filed inside the requirement list, which\n"
            "made `pip install -r` fail to parse the file outright. They are commented out; the\n"
            "behaviour they described belongs in the library, not in a requirements file.\n\n"
            "**Known, not fixed**: the same file still fails to resolve. `socketio>=0.8.0` is not\n"
            "a PyPI distribution name — the package is `python-socketio` — and several other pins\n"
            "(`argparse`, `pathlib2`, `jsoncomment`, `pyvbox`, `rsync`) were never verified.\n"
            "Renaming them means deciding what was meant, which is not a one-line fix. The file\n"
            "also declares roughly 150 dependencies this component does not use, because it was\n"
            "written as an environment manifest for the whole tree.\n\n"
            "Replaced metadata copied wholesale from `Project_Nurse_Ratchet`, including a\n"
            "manifest declaring `\"project\": \"nurse-ratchet\"` and an allowlist rooted at\n"
            "`../src/PSYCHE` — a path that resolves from this tree."
        ),
    },
    "Scribe": {
        "slug": "scribe",
        "title": "Project Scribe",
        "summary": (
            "Documentation generation for the Azazael tree, and the funding-portal census it "
            "grew into: profile generation from source, Markdown, HTML and diagram output, and "
            "a portal census tool with the evidence it cites."
        ),
        "manifest_note": (
            "This tree publishes in place and has no `tools/publicize.py`, so `ship` is empty.\n"
            "Scribe is the one tree here where an allowlist is not a formality: `evidence/`\n"
            "holds page captures taken for an internal audit that quote third-party pages, and\n"
            "`profiles/` holds grant proposals written for named funders. Both are recorded in\n"
            "`never_ship` below, and neither should leave the machine without a per-file review."
        ),
        "never_ship_extra": [
            {
                "glob": "evidence/*",
                "why": "page captures taken for an internal audit; they quote third-party pages and are not relicensed by this tree's LICENSE",
            },
            {
                "glob": "profiles/*",
                "why": "grant proposals addressed to named funders; publishing them by accident is a comms decision, not a build step",
            },
        ],
        "requirements": [
            req(
                "docs_are_generated",
                "Documentation that is generated, not typed twice",
                "generated docs",
                3,
                True,
                [
                    crit(
                        "A documentation generator exists",
                        "scribe.py",
                        "generates documentation from source rather than from a second hand-written copy",
                    ),
                    crit(
                        "A doc entry point exists",
                        "gen_doc.py",
                        "the command that produces the document set",
                    ),
                    crit("Generated output is diffed in CI so it cannot drift from its source"),
                ],
            ),
            req(
                "census_claims_are_cited",
                "A census whose every count has a capture behind it",
                "cited census",
                3,
                True,
                [
                    crit(
                        "A census tool exists",
                        "tools/portal_census.py",
                        "walks funding portals and records what it found",
                    ),
                    crit(
                        "Census output is stored as data",
                        "data/portal_census.json",
                        "the census result kept as data beside the tool that produced it",
                    ),
                    crit(
                        "A country-eligibility dataset is stored next to the census",
                        "data/eligible_countries.json",
                        "the eligibility table the census is read against",
                    ),
                    crit("Every portal counted in the census has a stored capture behind it"),
                    crit("The census records the date it was taken"),
                ],
            ),
            req(
                "profiles_are_reproducible",
                "A profile set that one script can rebuild",
                "profiles",
                2,
                False,
                [
                    crit(
                        "Profiles are generated from one script",
                        "update_profiles.py",
                        "one script writes the profile set, so a profile is not hand-edited per funder",
                    ),
                    crit("Every file in `profiles/` can be regenerated from that script"),
                ],
            ),
        ],
        "hardware": (
            "## What this component needs\n\n"
            "| Component | Requirement | Source |\n"
            "|---|---|---|\n"
            "| Python | 3.10+ | `scribe.py`, `tools/*.py` |\n"
            "| Network | required: the census fetches portal pages | `tools/portal_census.py` |\n"
            "| Disk | must hold the page captures under `evidence/` | `evidence/` |\n"
            "| GPU | none | this component writes documents |\n\n"
            "## What was validated\n\n"
            "Nothing was measured. The census is a claim about the world, not a performance\n"
            "number, and the open criterion above is the one that matters: counts without stored\n"
            "captures are assertions.\n"
        ),
        "changelog_note": (
            "Replaced metadata copied wholesale from `Project_Nurse_Ratchet`, including a\n"
            "manifest declaring `\"project\": \"nurse-ratchet\"` and an allowlist rooted at\n"
            "`../src/PSYCHE` — a path that resolves from this tree. All four files now describe\n"
            "this tree, and `evidence/` and `profiles/` are named in `never_ship` because they\n"
            "quote third parties and named funders.\n\n"
            "Fixed `profiles/cradle_proposal.md`, which cited a licence document that no longer\n"
            "exists."
        ),
    },
}


def compute_bar(tree: dict) -> dict:
    done = total = 0
    met = 0
    for r in tree["requirements"]:
        rd = rt = 0
        for c in r["criteria"]:
            rt += 1
            if c["done"]:
                rd += 1
        done += rd
        total += rt
        if r["required"] and rd == rt:
            met += 1
    required = sum(1 for r in tree["requirements"] if r["required"])
    return {
        "criteria_done": done,
        "criteria_total": total,
        "percent": round(100.0 * done / total, 1) if total else 0.0,
        "required_requirements": required,
        "required_requirements_met": met,
        "deployable": met == required,
    }


def certification(tree: dict) -> dict:
    return {
        "schema": f"{tree['slug']}/certification@1",
        "updated": DATE,
        "note": (
            "There is no tools/certification_bar.py in this tree, so no gate computes these "
            "numbers: `bar` below is derived from the criteria by "
            "tools/_fix_scaffold_metadata.py, and `--check` re-derives it so it cannot drift. "
            "Treat each `done` as a claim that names a path you can open. `deployable` stays "
            "false until every required requirement is fully met; a partial requirement is not "
            "a partial licence to ship."
        ),
        "computed_by": None,
        "held": [],
        "bar": compute_bar(tree),
        "requirements": tree["requirements"],
    }


def public_manifest(tree: dict, dirname: str) -> dict:
    return {
        "project": tree["slug"],
        "version": "0.1.0",
        "license": "Soul Forge License v1.0",
        "status": "PRE-PUBLICATION",
        "summary": tree["summary"],
        "ship_roots": [dirname],
        "allowlist_status": "NOT_WRITTEN",
        "why_empty": tree["manifest_note"],
        "ship": [],
        "never_ship": COMMON_NEVER_SHIP + tree.get("never_ship_extra", []),
        "deny_substrings": COMMON_DENY,
        "rationale": {
            "why_allowlist": (
                "A deny-list fails open: a directory added after the list was written ships by "
                "default, and the failure is silent. An allowlist fails closed."
            ),
            "why_not_written_here": (
                "An allowlist is only worth having when a gate reads it. No publicize step "
                "exists in this tree, so a list of paths here would be a claim with no check "
                "behind it. The honest state is 'not written', not an invented list."
            ),
        },
        "install": {
            "layout": "in place: the tracked tree is the artifact, there is no materialisation step",
            "command": "git clone <this tree>",
        },
    }


def hardare_md(tree: dict) -> str:
    return (
        f"# Hardware Requirements — {tree['title']}\n\n"
        "## Reference platform (the machine the work was done on)\n\n"
        "| Component | Specification |\n"
        "|-----------|---------------|\n"
        "| **CPU** | Intel Core Ultra 9 285H (16 cores, 22 threads) |\n"
        "| **iGPU** | Intel Arc 140T (8 GB shared VRAM) |\n"
        "| **RAM** | 32 GB LPDDR5x-8533 (dual channel) |\n"
        "| **OS** | Windows 11 Pro 24H2 (build 26100) |\n"
        "| **Python** | 3.14.7 (free-threaded) / 3.15.0rc3 (free-threaded) |\n\n"
        "This table describes where the code was written. It is **not** a validated\n"
        "configuration, and nothing in this tree was benchmarked for this document.\n\n"
        + tree["hardware"]
        + "\n## Development machine caveat\n\n"
        "The same box appears in every tree's `HARDWARE.md`, because it is one machine. Its\n"
        "presence here says nothing about whether this component runs on it.\n"
    )


def manifest_notes(tree: dict) -> str:
    return (
        "# Manifest notes\n\n"
        "`PUBLIC_MANIFEST.json` is meant to be an allowlist: nothing ships that it does not\n"
        "name. In this tree it is **not yet an allowlist**, and the manifest says so in\n"
        "`allowlist_status` rather than pretending otherwise.\n\n"
        "## The state of this tree\n\n"
        + tree["manifest_note"]
        + "\n\n## Why an allowlist instead of a deny-list\n\n"
        "A deny-list fails open. A directory added after the list was written ships by\n"
        "default, the push succeeds, the artifact is public, and nobody looks again. An\n"
        "allowlist fails closed, and the failure is a red gate before anything leaves the\n"
        "machine.\n\n"
        "## What is deliberately excluded\n\n"
        "`never_ship` is enforceable today, because it names globs that nothing needs to\n"
        "maintain: requiem's grave records, `node_modules`, `__pycache__`, and `.env` files.\n"
        + (
            "It also names `evidence/` and `profiles/`, which quote third-party pages and named\n"
            "funders respectively.\n"
            if tree["slug"] == "scribe"
            else ""
        )
        + "\n## Correcting the record\n\n"
        "Until 2026-11-15 this file, `certification.json`, `HARDWARE.md` and `CHANGELOG.md`\n"
        "were verbatim copies of `Project_Nurse_Ratchet`'s. The copied manifest declared\n"
        "`\"project\": \"nurse-ratchet\"` and an allowlist rooted at `../src/PSYCHE`, which\n"
        "resolves from this tree. A publicize run would have copied the clinical package into\n"
        "this component.\n"
    )


def changelog(tree: dict) -> str:
    return (
        "# Changelog\n\n"
        "All notable changes to this project will be documented in this file.\n\n"
        "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),\n"
        "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).\n\n"
        "## [Unreleased]\n\n"
        "### Changed\n\n"
        "- **One licence in the tree: the Soul Forge License v1.0.** Every other licence\n"
        "  reference in this project was removed on 2026-11-15. Third-party material keeps its\n"
        "  own terms and is named in `NOTICE`.\n"
        "- **This changelog has no history before 2026-11-15, and that loss is recorded rather\n"
        "  than hidden.** The file that stood here belonged to another project, so it was not\n"
        "  this component's history to keep. Nothing real was discarded.\n\n"
        "### Fixed\n\n"
        "- " + tree["changelog_note"].replace("\n", "\n  ") + "\n\n"
        "### Added\n\n"
        "- `certification.json` written for this component, with every `done` criterion citing\n"
        "  a path that exists in this tree.\n"
        "- `HARDWARE.md` stating this component's actual toolchain dependencies instead of a\n"
        "  clinical deployment's.\n"
        "- `MANIFEST_NOTES.md` stating plainly that `PUBLIC_MANIFEST.json` is not yet an\n"
        "  allowlist.\n"
    )


def targets() -> dict[Path, str]:
    out: dict[Path, str] = {}
    for name, tree in TREES.items():
        base = ROOT / f"Project_{name}"
        out[base / "PUBLIC_MANIFEST.json"] = json.dumps(public_manifest(tree, base.name), indent=1, ensure_ascii=False) + "\n"
        out[base / "certification.json"] = json.dumps(certification(tree), indent=1, ensure_ascii=False) + "\n"
        out[base / "HARDWARE.md"] = hardare_md(tree)
        out[base / "MANIFEST_NOTES.md"] = manifest_notes(tree)
        out[base / "CHANGELOG.md"] = changelog(tree)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if not (args.write or args.check):
        ap.error("choose --write or --check")

    problems: list[str] = []

    # every done criterion must cite a path that exists in that tree
    for name, tree in TREES.items():
        base = ROOT / f"Project_{name}"
        for sr in tree.get("_ship_roots", [base.name]):
            if not (ROOT / sr).is_dir():
                problems.append(f"{name}: ship_root is not a directory: {sr}")
        for r in tree["requirements"]:
            for c in r["criteria"]:
                if not c["done"]:
                    continue
                p = base / c["evidence"]["path"]
                if not p.exists():
                    problems.append(f"{name}: evidence path does not exist: {c['evidence']['path']}")
                if not c["evidence"]["note"]:
                    problems.append(f"{name}: done criterion has no note: {c['text'][:60]}")

    files = targets()

    # ship_roots must name a directory that exists, or the manifest points at nothing
    for path, text in files.items():
        if path.name != "PUBLIC_MANIFEST.json":
            continue
        for sr in json.loads(text)["ship_roots"]:
            if not (ROOT / sr).is_dir():
                problems.append(f"{path.relative_to(ROOT)}: ship_root is not a directory: {sr}")

    if args.check:
        for path, text in files.items():
            if not path.exists():
                problems.append(f"missing: {path.relative_to(ROOT)}")
                continue
            cur = path.read_text(encoding="utf-8")
            if path.name == "certification.json":
                try:
                    got = json.loads(cur)
                except json.JSONDecodeError as exc:
                    problems.append(f"{path.relative_to(ROOT)}: invalid JSON ({exc})")
                    continue
                want = json.loads(text)
                if got.get("bar") != want.get("bar"):
                    problems.append(
                        f"{path.relative_to(ROOT)}: bar drifted: file={got.get('bar')} derived={want.get('bar')}"
                    )
            if cur != text:
                problems.append(f"differs from generator: {path.relative_to(ROOT)}")

    if args.write:
        for path, text in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\r\n") as fh:
                fh.write(text)
        print(f"wrote {len(files)} file(s) across {len(TREES)} tree(s)")
        for name, tree in TREES.items():
            b = compute_bar(tree)
            print(
                f"  {name:24} {b['percent']:5.1f}%  criteria {b['criteria_done']}/{b['criteria_total']}"
                f"  required met {b['required_requirements_met']}/{b['required_requirements']}"
                f"  deployable={b['deployable']}"
            )

    if problems:
        print("\nPROBLEMS:", file=sys.stderr)
        for p in problems:
            print("  -", p, file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
