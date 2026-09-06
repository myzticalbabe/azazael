# Graph Report - azazael\output\graphify_atlas\aoa_g  (2026-08-27)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 276 nodes · 366 edges · 23 communities (15 shown, 8 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 60 edges (avg confidence: 0.6)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7a6494dc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]

## God Nodes (most connected - your core abstractions)
1. `ArmRegistry` - 20 edges
2. `ArmCapability` - 18 edges
3. `BaseArm` - 17 edges
4. `CrossArmRouter` - 16 edges
5. `SessionManager` - 14 edges
6. `Armorie-of-Anubis (AOA)` - 14 edges
7. `EventBus` - 13 edges
8. `WorkflowDAG` - 13 edges
9. `session` - 10 edges
10. `perfmon` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Armorie-of-Anubis (AOA)` --implements--> `CodexArm`  [EXTRACTED]
  AOA_STRUCTURE.html → arms/codex_arm.py
- `Armorie-of-Anubis (AOA)` --implements--> `CainArm`  [EXTRACTED]
  AOA_STRUCTURE.html → arms/cain_arm.py
- `Armorie-of-Anubis (AOA)` --implements--> `ClusterArm`  [EXTRACTED]
  AOA_STRUCTURE.html → arms/cluster_arm.py
- `Armorie-of-Anubis (AOA)` --implements--> `MetaArm`  [EXTRACTED]
  AOA_STRUCTURE.html → arms/meta_arm.py
- `Armorie-of-Anubis (AOA)` --implements--> `EveArm`  [EXTRACTED]
  AOA_STRUCTURE.html → arms/eve_arm.py

## Communities (23 total, 8 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (21): ABC, AzazaelArm, Azazael Arm - Adapter for the 77-worm neural mesh system., CodexArm, _get_python(), CODEX Arm - Adapter for video generation and rendering system., EveArm, EveUnleashed Arm - Adapter for AI model selection and inferencing. (+13 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (14): AOEvent, AOEventType, EventBus, EventPipeline, EventPriority, get_event_bus(), _match_pattern(), AOA EventBus - Cross-Arm pub/sub messaging system. (+6 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (23): cmd_arms_list(), cmd_arms_status(), cmd_init(), cmd_run(), cmd_session_complete(), cmd_session_milestones(), cmd_session_start(), cmd_workflow_start() (+15 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (23): azazael, initialized, total_worms, codex, codex_studio_exists, codex_studio_path, initialized, python (+15 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (21): architecture, adapter_arms, arms, core_modules, modules, total_capabilities, total_css_animations, total_mermaid_graphs (+13 more)

### Community 5 - "Community 5"
Cohesion: 0.1
Nodes (12): ArmMetadata, get_capabilities(), initialize(), AOA Arm Registry — Registration and discovery of all neural architecture Arms., Decorator to register an Arm class in the ARM_REGISTRY.          Usage:, List all registered Arms with metadata., Initialize all Arms (optionally filtered by category).                  Returns:, Shutdown all initialized Arms. (+4 more)

### Community 6 - "Community 6"
Cohesion: 0.14
Nodes (6): Milestone, MilestoneStatus, AOA Session Manager - Milestone tracking and cross-session state., SessionManager, SessionState, Enum

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (16): session, last_session_id, milestone_count, milestones, project_scope, session_id, summary, timestamp (+8 more)

### Community 8 - "Community 8"
Cohesion: 0.14
Nodes (15): AOA Disclosure Build Pipeline, Armorie-of-Anubis (AOA), AuditArm, CainArm, ClusterArm, CodexArm, EveArm, LibraArm (+7 more)

### Community 9 - "Community 9"
Cohesion: 0.5
Nodes (3): description, name, steps

## Knowledge Gaps
- **66 isolated node(s):** `project`, `version`, `date`, `description`, `core_modules` (+61 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BaseArm` connect `Community 0` to `Community 1`, `Community 5`?**
  _High betweenness centrality (0.149) - this node is a cross-community bridge._
- **Why does `ArmRegistry` connect `Community 2` to `Community 1`, `Community 5`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `CrossArmRouter` connect `Community 1` to `Community 0`, `Community 2`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `ArmRegistry` (e.g. with `StepStatus` and `WorkflowStep`) actually correct?**
  _`ArmRegistry` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `ArmCapability` (e.g. with `AzazaelArm` and `CodexArm`) actually correct?**
  _`ArmCapability` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `BaseArm` (e.g. with `AzazaelArm` and `CodexArm`) actually correct?**
  _`BaseArm` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `CrossArmRouter` (e.g. with `ArmRegistry` and `BaseArm`) actually correct?**
  _`CrossArmRouter` has 8 INFERRED edges - model-reasoned connections that need verification._