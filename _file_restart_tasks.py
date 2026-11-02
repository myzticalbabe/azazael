"""File every measured known failure as a board task, with read-back proof.

Each item carries the measurement that produced it, the exact file:line, and the
fix that is known to work. A task without its evidence is a rumour; the board's
own rule is that a post you cannot read back did not land, so each id printed
here was read back from memorybus_queue.
"""
from __future__ import annotations

import sys

sys.path.insert(0, "C:/Azazael/azazael/src")
from CORE.LaneMessageBoard import LaneMessageBoard  # noqa: E402

board = LaneMessageBoard(lane="freebuff")

TASKS = [
    dict(
        lane="kilo",
        task_id="EV-001-PF16-MODULE-LINK",
        action="Make PF16 reachability module-linked, then re-dispose the 134 wired rows",
        detail=(
            "MEASURED 2026-10-30. tests/test_mesh_wire_or_cut.py fails on "
            "'config:FeatureFlagCtrl.is_enabled' because scripts/ddap_portal_selenium.py calls "
            "Selenium's WebElement.is_enabled() -- a name match with no import of "
            "src/CORE/WORMS/expansion/config.py. The probe's OWN carry path already applies this "
            "rule (_module_qualified_hit, mesh_function_preflight.py:363, docstring cites the same "
            "2026-10-28 incident); its core build()/_reference_index path still counts bare tokens. "
            "PLAN: (1) filter bare-name evidence through the import link in build(); "
            "(2) re-run --verdict --propose; (3) the 134 rows that flip from 'wired' to 'carried' "
            "must be re-disposed with evidence -- 'dispatched' where mfp.string_references() has the "
            "name, 'accepted_gap' with a stated measurement otherwise; (4) confirm "
            "tests/test_mesh_wire_or_cut.py and evidence_gate --only wired_claims both green. "
            "Blast radius measured: 206 token-only functions, 135 wired rows, 3 module-linked."
        ),
        metadata={"evidence": "tests/test_mesh_wire_or_cut.py::test_dispatched_is_not_a_way_to_hide_a_static_caller",
                  "blocks": ["preflight_all --self-test --run-controls"]},
    ),
    dict(
        lane="kilo",
        task_id="EV-002-WIRED-ROWS-REAL",
        action="Give the 135 token-only 'wired' rows a caller or a truthful status",
        detail=(
            "MEASURED 2026-10-30 by tools/evidence_gate.py --only wired_claims: 3/138 wired rows "
            "have a module-linked caller; 135 rest on a bare token anywhere in src/tools/scripts. "
            "Flagrant examples from the ledger's own carry_evidence: 'axon:MyelinSheathWorm.__init__' "
            "matched the token '__init__' in 25 files; 'axon:MyelinSheathWorm.execute' matched "
            "'execute' in 117 files. This is the same defect class as Error #472/#682/#719. "
            "Baseline recorded in state/evidence_gate_baseline.json so it cannot grow; the task is "
            "to shrink it to 0 by wiring the worms that are genuinely used and re-disposing the rest."
        ),
        metadata={"gate": "python tools/evidence_gate.py --only wired_claims"},
    ),
    dict(
        lane="kilo",
        task_id="EV-003-DEAD-CONTROLS-37",
        action="Resolve the 37 dead controls (wire or delete)",
        detail=(
            "MEASURED 2026-10-30: 37 functions with control names (rotate_/enforce_/verify_/audit_/"
            "restore_/cleanup_...) have no module-linked caller outside tests. Full list: "
            "python tools/evidence_gate.py --json (check dead_control, field offenders). "
            "Samples: src/CORE/WORMS/STRIDE_VERIFIER_WORM.py:258 StrideVerifierWorm.verify_policy; "
            "src/CORE/WORMS/expansion/backup.py:225 CheckpointWorm.restore_checkpoint; "
            "src/CORE/audit_trail.py:1625 verify_citation_exists. Most are registry-dispatched worm "
            "methods, so the fix may be a registry entry + evidence, not a new code path. "
            "Rule bought today: do NOT wire a control that returns success without proving the "
            "effect (SecretRotator.rotate_secret did exactly that)."
        ),
        metadata={"gate": "python tools/evidence_gate.py --only dead_control"},
    ),
    dict(
        lane="kilo",
        task_id="EV-004-STORE-1835MB",
        action="Bring memory_store.db under its configured quota and prove retention ran",
        detail=(
            "MEASURED 2026-10-30: 1835 MB / 600080 rows at ~/.azazael/memory_store.db; "
            "DB_SIZE_QUOTA_MB is 500, so the store sits at 3.7x its own configured cap. The caller "
            "added on 2026-10-29 (local_memory.get_memory_store -> enforce_* once per process, only "
            "over quota, in a daemon thread with db_path passed explicitly) fires per-process, so the "
            "trim is incremental, not a purge. Evidence gate currently accepts 1900 MB as a ceiling "
            "(state/evidence_gate_baseline.json), which is visibility, not a fix. Decide: prune by "
            "type caps, archive-then-vacuum, or raise the configured quota on purpose."
        ),
        metadata={"gate": "python tools/evidence_gate.py --only store_growth"},
    ),
    dict(
        lane="kilo",
        task_id="EV-005-ROTATION-UNVERIFIED",
        action="Record the first verified secret rotation, or state that none is wanted",
        detail=(
            "MEASURED 2026-10-30: python tools/rotate_secret.py status -> keys_rotated=0, so the "
            "evidence gate reports UNVERIFIED (absence of evidence, deliberately not a pass). "
            "The capability is now real: rotate_secret backs up, writes atomically, reads the value "
            "back, and derives success from that read (tests/test_secret_rotation.py, 7 tests). "
            "Use: python tools/rotate_secret.py rotate <KEY> --dry-run first. No key was rotated "
            "here because a live provider key rotated without updating the provider is an outage."
        ),
        metadata={"gate": "python tools/evidence_gate.py --only rotation"},
    ),
    dict(
        lane="kilo",
        task_id="EV-006-TWO-BLIND-GATES",
        action="Generate the two missing gate baselines so the gates stop being BLIND",
        detail=(
            "MEASURED 2026-10-30 by python tools/preflight_all.py --self-test: "
            "two-interpreter-suite is BLIND (logs/ci_two_interpreter_gate_baseline.json absent) and "
            "aggregate-suite-isolation is BLIND (logs/aggregate_suite_baseline.json absent). "
            "A gate that cannot judge is not a pass -- preflight reports BLIND on purpose. "
            "Plan: run each gate once in record mode to write its baseline, then confirm the "
            "self-test line changes from BLIND to OK."
        ),
        metadata={"gate": "python tools/preflight_all.py --self-test"},
    ),
    dict(
        lane="kilo",
        task_id="EV-007-SEMANTIC-INDEX-442MB",
        action="Keep the semantic index under its new cap on the next full re-index",
        detail=(
            "DONE 2026-10-30, verification owed: llama-server/embeddings/semantic_index.jsonl went "
            "1.68 GB -> 442 MB with 0 duplicates dropped and 71765 embeddings repacked as base64 "
            "float32 (semantic.py pack_embedding/unpack_embedding; reader accepts both encodings). "
            "Vector search verified on a 40-record slice: self-query scored bm25=1.0 vec=0.9442. "
            "Growth guard added: over SEMANTIC_INDEX_MAX_MB (512) the index compacts before append; "
            "--rebuild moves the old file aside; `compact` is a subcommand. "
            "TASK: run one full `python semantic.py index --all` and confirm it stays under 512 MB."
        ),
        metadata={"file": "C:/Users/clint/llama-server/unified/semantic.py"},
    ),
]

for spec in TASKS:
    lane = spec["lane"]
    row_id = board.post_task(lane, spec["action"], spec["detail"],
                             task_id=spec["task_id"], source_lane="freebuff",
                             metadata=spec.get("metadata") or {})
    print(f"{spec['task_id']:<28} -> lane={lane} durable_row={row_id}")
