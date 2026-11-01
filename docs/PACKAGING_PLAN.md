# What ships with the tree — the packaging plan

**Status: proposal, 2026-11-01.** Every state in this document was measured in
this tree on this date; nothing here is a roadmap dressed as an inventory. Where
a thing does not exist, the count is `0` and it stays `0` until a file lands.

## The claim being packaged

The tree already contains the four things a decentralized AI stack needs, and it
is worth naming them as one stack, because they were built separately:

1. a **node** that measures itself (`tools/box_profile.py`) and can run on the box
   it measures,
2. a **person model** that lives on that node and nowhere else
   (`Project_Nurse_Ratchet/` — traits, affect, constructs, realtime loop),
3. a **seam** that carries state between nodes without a server
   (`src/CORE/mesh_transport.py` + `spine_registry.py` + the federated worm),
4. **instruments** that make a node's output falsifiable (`tools/`), because a
   decentralized system has no central reviewer to catch a wrong answer.

"Decentralized" is not a property of the code being stdlib-only. It is a property
of *where the person's data lives and who can read it*. That distinction is the
whole of the gap section below.

## The layer table

| layer | package | state today (measured) | to ship it needs |
|---|---|---|---|
| **L0 node** | `tools/box_profile.py` + `docs/platforms/` + `scripts/box/` | 3-state profiler (`available`/`unavailable`/`unknown`), 10 tests, writes `box_profile.json`, `--check` catches drift | nothing — this is the most finished thing here |
| **L0 node** | PAMS/PMB local store | in use every session; `~/.pmb/workspaces/<ws>/events.sqlite`, local-only, Apache-2.0 | a documented export/import so a person's memory is portable off the tool |
| **L0 node** | DirectMemory + audit trail + failure ledger | `src/CORE/direct_memory.py`, `audit_trail.py`, `failure_ledger.py` | a single "what is on this node" listing a user can read |
| **L1 person** | `Project_Nurse_Ratchet` 0.1.0 | the **packaging template for everything else**: `pyproject.toml`, CHANGELOG, CITATION, SECURITY, `PUBLIC_MANIFEST.json`, and `tools/publicize.py` — an allowlist copy tool that refuses any path the manifest does not name and re-imports the result in a fresh subprocess before calling it published. Recall floor **0.83 / 0.83 / 0.18** across its own three holdouts; and `certification.json` + `tools/certification_bar.py`, which publish a computed certifiability percentage and refuse a criterion marked done without evidence | real construct data; the 0.18 holdout is the honest one |
| **L1 person** | `Project_ELIZA` | **declared only** — there is no `Project_ELIZA/` directory in this tree yet, and its sources (`.bcc_audit/`, `behavior_lint.py`, `behavior_trace.py`) are in the `G:/AZAZAEL*` archives | source restoration, then its own allowlist gate built on the Nurse Ratchet pattern |
| **L2 seam** | `src/CORE/mesh_transport.py` | 352 lines, stdlib-only, length-prefixed JSON envelopes over TCP, delivery receipts, size caps, auth required for non-loopback, inbox spills to disk | **does not cross hosts as deployed** — binds 127.0.0.1 |
| **L2 seam** | `src/CORE/spine_registry.py` | 4,121 lines; 24 mesh/spine test modules | a peer table that is discovered, not hardcoded |
| **L2 seam** | identity | Ed25519 in 11 modules (mesh_transport, audit_trail, compliance/governance, sentinel_gate, request_auth) | one node-key lifecycle: create, rotate, revoke, attest |
| **L2 seam** | federation | `src/CORE/WORMS/expansion/federated.py`, `fabric_state.py`, `spine.py` (12 modules mention federation) | a spec: what state is allowed to leave a node, in what form |
| **L3 cognition** | `src/CORE/inference/` | 9,132 lines; **local providers are already first-class** — `OllamaNativeFrameworkProvider`, `LlamaCppDirectProvider`, HuggingFace native; 48 modules reference local runtimes | a rule that local is tried before cloud, enforced, not preferred |
| **L3 cognition** | `graphifyy` 0.9.72 | installed; turns a codebase or corpus into a persistent graph | per-person graph as the *only* artifact that leaves a node — it is smaller than the corpus and already stripped |
| **L3 cognition** | AOA (`src/AOA/`) | stdlib-only orchestrator, 8 arms, 6 AOA tests, zero third-party imports | an arm per package, so a node can supervise its own bundles |
| **L4 instruments** | gates | `.githooks/pre-commit`, `anti_pattern_gate.py`, `preflight_all.py`, `wire_or_cut`, PMB floor proxy (`0.89` query / `0.70` row) | each new bundle gets its own gate, not the trunk's |

## The gap that decides whether the claim is true

The mesh is the strongest idea here and the weakest artefact. Measured:

- **peer discovery: `0` modules.** Peers come from a static `ENV_PORTS` dict
  (`windows: 18210`, `wsl2-ubuntu: 18211`, …). A node cannot find another node it
  was not compiled to know.
- **cross-host delivery: impossible as deployed.** The module says so itself:
  the default bind is loopback, and a non-loopback `bind_addr` without
  `require_auth` is *refused at listen() by design*, because the wire is otherwise
  trust-by-port. That refusal is correct; what is missing is the authenticated
  path it is refusing for.
- **residency: `0` modules.** Nothing states which bytes may leave a node. For a
  product whose data is a person's psyche, that is not a detail.
- **consent: 2 files, both CODEX video renderers.** Consent does not exist in the
  data path at all.

So: today, "decentralized" means several environments on **one** machine (or a
WSL2 loopback seam) sharing a fabric. It does not yet mean two people on two
devices. Packaging the mesh before those four gaps are closed would ship a
demo of decentralization, which is worse than an honest single-node product.

## Packaging order

Five bundles, in this order, each with the shape Nurse Ratchet already has —
version, CHANGELOG, manifest, tests, its own gate:

1. **`node`** — box profiler, platform docs, bootstraps, a printed inventory of
   what is on the box. Ships today.
2. **`person`** — the psyche kernel plus its memory, wrapped so the model and its
   store are one unit and can be exported whole. Blocks on: export/import.
3. **`seam`** — mesh transport, keys, federation spec. Blocks on: discovery, the
   authenticated non-loopback path, a written residency rule. Do not ship before
   all three: a mesh that ships without them teaches the user to trust a wire that
   cannot be trusted.
4. **`instruments`** — gates and ledgers, because a decentralized node has no
   central reviewer. This is the bundle that makes 2 and 3 safe to run.
5. **`cognition`** — local-first providers, graphify per-person graph, AOA arms.
   Cheap to package, and it is what makes a node usable offline.

Bundles 1, 4 and 5 can ship now. Bundle 2 needs one small piece (portable
memory). Bundle 3 needs engineering, not packaging.

## What must never be packaged

- **ELIZA case data.** Methodology ships, records do not. The mechanism already
  exists and is proven: `Project_Nurse_Ratchet/tools/publicize.py` reads
  `PUBLIC_MANIFEST.json`, copies only named paths, and fails if the published tree
  cannot be imported. ELIZA inherits that gate, not a `cp -r`.
- **Keys and tokens.** Node identity is generated per node, never shipped.
- **The counselor claim.** Nurse Ratchet ships with its 0.18 holdout published in
  the README, not with the 0.83 average alone.

## See also

- `docs/AZAZAEL_TREE_OF_LIFE.md` — which project is which, and the rule keeping
  the forensic suite and the behavioural package apart
- `docs/platforms/README.md` — fitting a node to a box
- `src/CORE/mesh_transport.py` — the topology limit, in the module's own words
