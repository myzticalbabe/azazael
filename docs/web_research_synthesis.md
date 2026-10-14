# Web Research Synthesis: PyAgent Patterns & Work-Stealing Integration with Azazael
**Date**: 2026-10-11  
**Context**: Parallel integration task — synthesize web findings into Azazael's worm registry, neural mesh, and scheduler.

---

## 1. PyAgent 18 Patterns — Adoption Strategy

### Pattern Catalog (from pyagent.org)
| Tier | Pattern | Description | Azazael Mapping |
|------|---------|-------------|-----------------|
| **Orchestration** | Pipeline | Sequential stages | `CORE.WORMS.orchestration.PipelineWorm` (NEW) |
| | Supervisor | Task routing | MetaCluster dispatch (EXISTS) |
| | Fan-Out/Fan-In | Parallel analysis | `ClusterWORMZ.build_from_registry(category)` (EXISTS) |
| | Hierarchical | Multi-level workflows | NeuralPipeline 6-step (EXISTS) |
| | Swarm | Distributed consensus | `consensus` worms: RaftConsensusWorm, QuorumWorm (EXISTS) |
| | ReAct | Tool-use loops | `learning.ReActWorm` (EXISTS) |
| **Resolution** | Self-Reflection | Iterative refinement | `learning.SelfReflectionWorm` (EXISTS) |
| | Debate | Multi-agent argument | `consensus.DebateWorm` (EXISTS) |
| | Planning | Decomposition | `orchestration.PlannerWorm` (EXISTS) |
| | Verification | Output checking | `diagnostic.VerifierWorm` (EXISTS) |
| **Structural** | Blackboard | Shared knowledge store | `mesh.GossipSyncWorm` + PAMS MemoryBus (EXISTS) |
| | Layered | Presentation→Logic→Data | `neural_mesh` layers (EXISTS) |
| | Role-Based | Runtime-enforced roles | `@register_worm` category = role (EXISTS) |
| | Topology | Adjacency graph | `MeshRouterWorm` + `PartitionHealerWorm` (EXISTS) |
| **Advanced** | OrchRM | Self-supervised reward | `learning.RewardShapingWorm` (EXISTS - 6-API) |
| | CoAgent | Concurrency control | `mesh.ConcurrencyGateWorm` (NEW) |
| | STRIDE | Verifiable RL | `security.StrideVerifierWorm` (NEW) |
| | SPORK | Speculative forking | `synapse.SpeculativeForkWorm` (NEW) |

### Decision: **Cherry-pick only**
- Our 11-provider inference + retry (RULE 0D) already covers provider fallback chains
- Token budgets → `InferenceLoadBalancerWorm` (servemesh category)
- Trace/replay → DirectMemory CD1 schema + `.audit/` JSONL (EXISTS)
- **Do NOT adopt PyAgent wholesale** — adds dependency surface; our worm registry + cluster system is functionally equivalent

---

## 2. Work-Stealing Queue — Integration with Azazael Scheduler

### Current State
- `azazael-parallel` skill: `FreeThreadPool` + `WorkStealingPool` + `WorkStealingQueue` (3.14t)
- `azazael-work-stealing` skill: `WorkStealingPool` / `WorkStealingQueue` implementations
- **Gap**: No cache-aware stealing, no session affinity, no KV-cache migration

### Research Findings (BWoS, SAGA, arXiv:2607.20495)
| Technique | Paper | Azazael Integration |
|-----------|-------|---------------------|
| **Block-based Work Stealing (BWoS)** | OSDI'23 | Replace per-worm deque with block-deque in `WorkStealingQueue` |
| **Session-affinity + work stealing** | SAGA (arXiv:2605.00528) | Add `session_affinity` to `WorkStealingPool`; steal oldest pending session |
| **Workload-aware caching** | arXiv:2607.20495 | Score = `recompute_cost * dag_deps * invocation_freq` → eviction policy for PAMS |
| **KV-cache migration** | SAGA + Llumnix | `InferenceLoadBalancerWorm` migrates KV cache on steal (servemesh) |

### Implementation Plan
```python
# CORE/parallel/work_stealing.py — enhance existing WorkStealingQueue
class BlockWorkStealingQueue(WorkStealingQueue):
    """BWoS: split deque into blocks, reduce sync overhead 1.6-30x"""
    BLOCK_SIZE = 8  # 8 blocks per queue
    
    def steal_block(self) -> list:  # steal contiguous block, not single item
        ...

class SessionAffinityPool(WorkStealingPool):
    """Two-level scheduler: local affinity + global work stealing"""
    IDLE_THRESHOLD_MS = 100
    LOAD_RATIO_MAX = 2.0
    
    def steal_session(self, victim_id: int) -> Session:
        # Migrate KV cache via InferenceLoadBalancerWorm
        ...
```

---

## 3. Cache-Merging / Workload-Aware Caching — PAMS Integration

### Three Complementary Techniques (arXiv:2607.20495)
1. **Plan-level caching** → Cache compiled `AgentExecutionGraph` (Blueprint YAML → RuntimeGraph)
2. **Parallel execution** → `ClusterWORMZ` + `WorkStealingPool` (EXISTS)
3. **Workload-aware content caching** → **NEW**: PAMS cache eviction policy

### PAMS Cache Scoring Function
```python
# CORE/pams/cache_policy.py
def workload_aware_score(entry: CacheEntry, dag: AgentExecutionGraph) -> float:
    """Higher = more valuable to retain"""
    recompute_cost = entry.metadata.get('compute_ms', 1.0)
    dag_deps = dag.dependency_count(entry.key)
    invoke_freq = entry.access_count / max(1, time_since_creation_hours)
    return recompute_cost * dag_deps * invoke_freq
```

### Integration Points
| Component | Change |
|-----------|--------|
| `PamsRecorder` | Add `workload_aware_evict(capacity_pct=0.5)` |
| `MemoryBus` | Publish `CacheEvictionEvent` for observability |
| `InferenceLoadBalancerWorm` | Consume eviction events → migrate KV cache proactively |

---

## 4. Neural Mesh Integration Points

### Existing Mesh Worms (27 total)
| Category | Worms | Role in Integration |
|----------|-------|---------------------|
| `mesh` (6) | EnvBeaconWorm, GossipSyncWorm, MeshRouterWorm, PartitionHealerWorm, ScoutBeeWorm, SpineMapperWorm | Core mesh topology + healing |
| `envmesh` (6) | BarePassthroughWorm, EnvBeaconV2Worm, GDriveLoomWorm, WinBridgeWorm, WslKaliWorm, WslUbuntuWorm | Cross-env sync (Windows/WSL/G:) |
| `servemesh` (3) | InferenceLoadBalancerWorm, ModelShardServerWorm, ProviderFailoverMeshWorm | **KV-cache migration target** |
| `synapse` (6) | ActivationRouterWorm, AttentionRouterWorm, HomeostatWorm, MoEDispatcherWorm, SSMSequenceWorm, SynapseWeightWorm | Neural routing + speculative fork |
| `axon` (4) | LatencyCompensatorWorm, MyelinSheathWorm, SaltatoryRouterWorm, SpikeEncoderWorm | Latency compensation for stealing |
| `dendrite` (4) | AttentionGateWorm, ContextConcatWorm, DendriteAggregatorWorm, SensoryFuseWorm | Context aggregation for blackboard |
| `glia` (4) | AstrocyteWorm, EpendymalWorm, MicrogliaWorm, OligodendrocyteWorm | Support/monitoring (telemetry) |

### New Worms Needed (4)
```python
# CORE/WORMS/mesh/ConcurrencyGateWorm.py      # CoAgent pattern
# CORE/WORMS/security/StrideVerifierWorm.py   # STRIDE pattern
# CORE/WORMS/synapse/SpeculativeForkWorm.py   # SPORK pattern
# CORE/WORMS/orchestration/PipelineWorm.py    # Pipeline pattern (explicit)
```

---

## 5. Scheduler Enhancement Roadmap

### Phase 1: BWoS Queue (Week 1)
- [ ] Implement `BlockWorkStealingQueue` in `CORE/parallel/work_stealing.py`
- [ ] Benchmark against current `WorkStealingQueue` (target: 2-5x throughput)
- [ ] Add `steal_block()` for bulk operations

### Phase 2: Session Affinity + KV Migration (Week 2)
- [ ] Add `SessionAffinityPool` with `IDLE_THRESHOLD_MS=100`, `LOAD_RATIO_MAX=2.0`
- [ ] Wire `InferenceLoadBalancerWorm.migrate_kv_cache(src, dst)` 
- [ ] Integrate with `MetaCluster` dispatch

### Phase 3: Workload-Aware PAMS Cache (Week 3)
- [ ] Add `workload_aware_score()` to `PamsRecorder`
- [ ] Build `AgentExecutionGraph` from worm registry DAG
- [ ] Connect eviction → `InferenceLoadBalancerWorm` proactive migration

### Phase 4: Pattern Composition (Week 4)
- [ ] Compose: `FanOut(ClusterWORMZ) → Pipeline → SelfReflection`
- [ ] Add `PatternAdvisor` worm: selects pattern from task description
- [ ] Export blueprint YAML for reproducibility

---

## 6. Verification Checklist

| Criterion | Status | Evidence |
|-----------|--------|----------|
| PyAgent patterns mapped | ✅ | Table in §1 |
| No wholesale adoption | ✅ | Decision in §1 |
| BWoS queue designed | ✅ | §2 implementation plan |
| Session affinity designed | ✅ | SAGA integration in §2 |
| Workload-aware cache designed | ✅ | §3 scoring function |
| Mesh worms inventoried | ✅ | §4 table (27 existing) |
| New worms identified | ✅ | §4 (4 needed) |
| Scheduler roadmap defined | ✅ | §5 (4 phases) |

---

## 7. Next Actions

1. **Immediate**: Implement `BlockWorkStealingQueue` in `CORE/parallel/work_stealing.py`
2. **Immediate**: Create 4 new worm modules (ConcurrencyGate, StrideVerifier, SpeculativeFork, Pipeline)
3. **This session**: Wire `SessionAffinityPool` → `MetaCluster` → `InferenceLoadBalancerWorm`
4. **Document**: Update `SOTA_TECHNIQUE_CODEBASE_MAP.md` with BUILT status for work-stealing + cache-merging
5. **Validate**: Run Freebuff swarm results check when complete (~150s from launch)