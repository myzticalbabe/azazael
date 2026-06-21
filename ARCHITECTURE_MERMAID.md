# Azazael Architecture — Mermaid Graphs

## System Architecture (graph TD)

```mermaid
graph TD
    User["User / CLI"] --> MC["MetaCluster Orchestrator"]
    MC --> NCM["NatureClusterManager"]
    NCM --> NC_SEC["NatureCluster: security"]
    NCM --> NC_MON["NatureCluster: monitor"]
    NCM --> NC_DIAG["NatureCluster: diagnostic"]
    NCM --> NC_ORCH["NatureCluster: orchestration"]
    NCM --> NC_LEARN["NatureCluster: learning"]
    NCM --> NC_UTIL["NatureCluster: utility"]
    NCM --> NC_ANAL["NatureCluster: analysis"]
    NCM --> NC_ML["NatureCluster: ml"]

    NC_SEC --> VS["VulnScanner p=8"]
    NC_SEC --> PA["PortAuditor p=7"]
    NC_SEC --> CM["CertMonitor p=6"]
    NC_SEC --> FA["FirewallAudit p=5"]
    NC_SEC --> PS["PermissionScanner p=5"]

    NC_MON --> SZ["SystemZ p=8"]
    NC_MON --> NZ["NetworXZ p=7"]
    NC_MON --> PZ["ProcessZ p=6"]
    NC_MON --> DK["DiskZ p=5"]
    NC_MON --> SMART["SmartDisk p=5"]
    NC_MON --> OS["OSCongruency p=6"]

    NC_ORCH --> MC2["MetaCluster p=10"]
    NC_ORCH --> NC2["NatureClusters p=9"]
    NC_ORCH --> CW["ClusterWORMZ p=7"]
    NC_ORCH --> CONC["Concurrency p=7"]
    NC_ORCH --> FLEET["WormFleet p=6"]

    NC_LEARN --> RL["RLTrainLoop p=6"]
    NC_LEARN --> DP["DataPipelineWorm p=5"]
    NC_LEARN --> MV["ModelVersioner p=5"]
    NC_LEARN --> AB["ABTestRunner p=4"]
    NC_LEARN --> FE["FeatureEngineer p=5"]
    NC_LEARN --> GRPO["GRPOTrainer NEW"]
    NC_LEARN --> PRB["PrioritizedReplayBuffer NEW"]
    NC_LEARN --> WS["WormSelectorWorm NEW"]

    NC_DIAG --> DW["DiagnosticWorm p=5"]
    NC_DIAG --> ERR["ErrorScanWorm p=4"]
    NC_DIAG --> MORPH["MorphingWorm p=4"]
    NC_DIAG --> NETD["NetworkDiag p=7"]

    NC_ML --> SML["SystemZ_ML p=6"]
    NC_ML --> WML["WormZ_ML p=5"]

    NC_ANAL --> BINA["BinaryAnalysis p=6"]
    NC_ANAL --> REVS["ReverseTools p=6"]
    NC_ANAL --> CINS["ClusterInspector p=5"]

    NC_UTIL --> WORMZ["WormZ p=5"]
    NC_UTIL --> OMNI["OmniWorm_V2 p=4"]
    NC_UTIL --> MORPH2["MorphingWorm_V2 p=4"]

    MC --> CNR["CrossNatureRoutingEngine"]
    CNR --> |"46 routes, 264 paths"| NC_SEC
    CNR --> NC_MON
    CNR --> NC_DIAG
    CNR --> NC_ORCH

    subgraph "Infrastructure"
        WR["WORM_REGISTRY (77 worms, 17 categories)"]
        LMS["LocalMemoryStore (SQLite, 1100+ entries)"]
        PAMS["PAMS Bus (51 insights, 133 memories)"]
        FTA["FreeThreadedAgent (Python 3.14t)"]
        SDE["SpawnDiversityEngine"]
        KGRAPH["Knowledge Graph (agent_patterns)"]
    end

    MC --> WR
    NC_LEARN --> LMS
    NC_LEARN --> PAMS
    FTA --> |"base class"| MC
    SDE --> |"weighted selection"| NCM
    KGRAPH --> |"cross-agent patterns"| NC_LEARN

    classDef ok fill:#1a3a1a,stroke:#00ff88,color:#00ff88
    classDef new fill:#1a1a3a,stroke:#4488ff,color:#4488ff
    classDef infra fill:#2a2a2a,stroke:#666666,color:#888888
    class GRPO,PRB,WS new
    class WR,LMS,PAMS,FTA,SDE,KGRAPH infra
```

## ML Training Pipeline (graph TD)

```mermaid
graph TD
    Schedule["ScheduledTrainingWorm"] --> Extract["Stage 1: DataPipelineWorm"]
    Extract --> |"records from LocalMemoryStore"| Features["Stage 2: FeatureEngineer"]
    Features --> |"feature vectors"| RL["Stage 3: RLTrainLoop"]
    RL --> |"Q-learning + epsilon-greedy"| Replay["Stage 3b: PrioritizedReplayBuffer"]
    RL --> |"training rewards"| GRPO2["Stage 3c: GRPOTrainer"]
    GRPO2 --> |"group-normalized advantages"| Policy["Learned Worm Policy"]
    Replay --> |"prioritized experiences"| Versioner["Stage 4: ModelVersioner"]
    Versioner --> |"register model version"| Store["LocalMemoryStore"]
    Policy --> |"optimal worm selection"| Selector["WormSelectorWorm"]
    Selector --> |"DPO preferences"| AB2["ABTestRunner v2.0"]
    AB2 --> |"preference pairs"| DPO["DPO Loss Computation"]
    Selector --> |"knowledge graph queries"| KG["Cross-Agent Knowledge Graph"]

    subgraph "Learning Loop"
        RL
        GRPO2
        Replay
        AB2
        DPO
    end

    subgraph "Storage"
        Store
        KG
    end

    classDef stage fill:#1a3a1a,stroke:#00ff88,color:#00ff88
    classDef new fill:#1a1a3a,stroke:#4488ff,color:#4488ff
    classDef storage fill:#2a2a2a,stroke:#666666,color:#888888
    class Replay,GRPO2,Selector,DPO new
    class Store,KG storage
```

## Agent Hierarchy (graph TD)

```mermaid
graph TD
    FTA["FreeThreadedAgent (base class)"] --> PBB["PamsBusBridge"]
    FTA --> CWT["Custom Worm Agents"]
    FTA --> |"spawn_sub_agent()"| Child["Child Agents"]

    AgentPool["AgentPool"] --> |"manages"| FTA

    PAMS2["PAMS Server (port 5100)"] --> |"REST API"| FTA
    PAMS2 --> |"PUT /memories/:id"| LMSP["LocalMemoryStore"]
    PAMS2 --> PUTI["PUT /insights/:id"]

    MC3["MetaCluster"] --> |"orchestrates"| NC3["NatureClusters"]
    NC3 --> |"executes"| Worms["Individual Worms"]
    Worms --> |"record results"| LMSP
    LMSP --> |"train from"| RL2["RLTrainLoop"]
    RL2 --> |"optimize"| GRPO3["GRPOTrainer"]
    GRPO3 --> |"select best"| WS2["WormSelectorWorm"]
    WS2 --> |"feedback loop"| MC3

    classDef base fill:#3a1a1a,stroke:#ff4444,color:#ff4444
    classDef new fill:#1a1a3a,stroke:#4488ff,color:#4488ff
    classDef infra fill:#2a2a2a,stroke:#666666,color:#888888
    class FTA,AgentPool base
    class GRPO3,WS2 new
    class PAMS2,LMSP infra
```

## Neural Integration Architecture (graph TD)

```mermaid
graph TD
    subgraph "Training Pipeline (training-pipeline)"
        DPL["DataPipelineWorm (ETL)"]
        FEX["SchemaAwareFeatureExtractor"]
        RLT["RLTrainLoop (Q-Learning)"]
        SB3["SB3Agent (PPO/DQN/A2C)"]
        GRPO["GRPOTrainer (Group Relative)"]
        NPL["NeuralPipeline Orchestrator"]
        MVR["ModelVersioner"]
    end

    subgraph "Neural Architecture (neural-architecture)"
        MOE["MoE / SSM / NAS Patterns"]
    end

    subgraph "ML Platforms (ml-platforms)"
        ONNX["ONNX Export"]
        RAY["Ray Hyperparameter Tune"]
        LMS["LM Studio Local Server"]
        MTR["Metrics Tracker"]
    end

    subgraph "Model Compression (model-compression)"
        GPTQ["GPTQ (GPU, 4-bit, 98-99%)"]
        AWQ["AWQ (GPU, 4-bit, 99%+)"]
        GGUF["GGUF (CPU, Q4_K_M, 97-99%)"]
        DST["Distillation (optional)"]
        PRN["Pruning (optional)"]
    end

    subgraph "Inference Protocol (inference-protocol)"
        C12["12-Provider Failover Chain"]
        FAL["Auto-Fallback (thinker-gpt)"]
        DLQ["DeadLetterQueue"]
    end

    DPL --> FEX
    FEX --> RLT
    FEX --> SB3
    FEX --> GRPO
    RLT --> NPL
    SB3 --> NPL
    GRPO --> NPL
    NPL --> MVR

    MOE -.->|"3E: guides trainer choice"| SB3

    MVR -->|"3B: ONNX export"| ONNX
    MVR --> RAY
    MVR --> MTR

    ONNX -->|"3D: ONNX shared interface"| GPTQ
    ONNX --> AWQ
    ONNX -.-> DST
    ONNX -.-> PRN
    GPTQ --> GGUF
    AWQ --> GGUF

    GGUF -->|"3C: deploy target"| LMS
    GGUF -->|"3C: deploy target"| C12
    ONNX --> LMS

    NPL -.->|"3A: HIGH — reward shaping\n6 API subset"| C12

    C12 --> FAL
    C12 -.->|"capture failures"| DLQ

    classDef pipeline fill:#1a3a1a,stroke:#00ff88,color:#00ff88
    classDef arch fill:#1a1a3a,stroke:#4488ff,color:#4488ff
    classDef platform fill:#3a1a1a,stroke:#ff8844,color:#ff8844
    classDef compress fill:#2a2a2a,stroke:#aa44ff,color:#aa44ff
    classDef infer fill:#1a2a3a,stroke:#44aaff,color:#44aaff

    class DPL,FEX,NPL,MVR pipeline
    class RLT,SB3,GRPO arch
    class ONNX,RAY,LMS,MTR platform
    class GPTQ,AWQ,GGUF,DST,PRN compress
    class C12,FAL,DLQ infer
```

## Neural Data Flow — End-to-End Pipeline (graph TD)

```mermaid
graph TD
    LMS2["LocalMemoryStore\n(11,633+ memories)"] -->|"raw event data"| DPW["DataPipelineWorm\nETL: extract/transform/load/split/CV"]
    DPW --> SAF["SchemaAwareFeatureExtractor\ntyped via DATA_SHAPES"]

    SAF -->|"feature matrix"| QL["RLTrainLoop\nQ-Learning + epsilon-greedy"]
    SAF -->|"feature matrix"| PP["SB3Agent\nPPO / DQN / A2C"]
    SAF -->|"feature matrix"| GR["GRPOTrainer\nGroup Relative + DPO"]

    QL --> NP["NeuralPipeline\norchestrates all 3 trainers\nvia WorkStealingPool"]
    PP --> NP
    GR --> NP

    NP -->|"version + rollback"| MV2["ModelVersioner"]
    NP -.->|"reward shaping via\n6 inference APIs"| APIS2["Groq / OpenRouter /\nNIM / Mistral / GitHub / HF"]
    APIS2 -.->|"failures captured"| DLQ2["DeadLetterQueue\nreplay on next run"]

    MV2 -->|"ONNX export"| ON2["ONNX"]

    ON2 -->|"GPTQ (GPU 4-bit, 98-99%)"| GQ["Quantized Model"]
    ON2 -->|"AWQ (GPU 4-bit, 99%+)"| AQ2["Quantized Model"]
    ON2 -.->|"distillation"| DS["Student Model\nsmaller, faster"]
    ON2 -.->|"pruning"| PR["Pruned Model"]

    GQ -->|"GGUF (CPU Q4_K_M, 97-99%)"| DP2["Deployment\nLM Studio / 12-Provider Chain"]
    AQ2 --> DP2
    DS --> DP2
    PR --> DP2

    ON2 -->|"direct deploy"| DP2

    classDef storage fill:#2a2a2a,stroke:#888888,color:#888888
    classDef ingest fill:#1a3a1a,stroke:#00ff88,color:#00ff88
    classDef train fill:#1a1a3a,stroke:#4488ff,color:#4488ff
    classDef orch fill:#1a3a1a,stroke:#00ff88,color:#00ff88
    classDef export fill:#3a1a1a,stroke:#ff8844,color:#ff8844
    classDef compress fill:#2a2a2a,stroke:#aa44ff,color:#aa44ff
    classDef deploy fill:#1a2a3a,stroke:#44aaff,color:#44aaff

    class LMS2 storage
    class DPW,SAF ingest
    class QL,PP,GR train
    class NP,MV2,APIS2,DLQ2 orch
    class ON2 export
    class GQ,AQ2,DS,PR compress
    class DP2 deploy
```

## Coupling Map — Integration Points (graph TD)

```mermaid
graph TD
    TP["Training\nPipeline"] -->|"3A: HIGH — reward shaping via 6 APIs"| IP["Inference\nProtocol"]
    TP -->|"3B: MODERATE — ONNX export / Ray tune"| MP["ML\nPlatforms"]
    TP -.->|"3E: LOOSE — architecture guides trainer choice"| NA["Neural\nArchitecture"]
    MP -->|"3D: MODERATE — ONNX shared interface"| MC["Model\nCompression"]
    MC -->|"compressed model → deploy"| IP
    MP -.->|"3C: LOW — independent deployment targets"| IP

    TP -->|"Full path: 3B → 3D → 3C"| DP["Deployment\nLM Studio / Providers"]

    classDef sys fill:#1a3a1a,stroke:#00ff88,color:#00ff88
    classDef final fill:#1a2a3a,stroke:#44aaff,color:#44aaff
    class TP,NA,MP,MC,IP sys
    class DP final
```

## Key Numbers
- 5 interconnected neural systems across integration architecture
- 4 deployment scenarios: Full, Compressed, Distillation, NAS
- 5 coupling points (3A HIGH, 3B MODERATE, 3C LOW, 3D MODERATE, 3E LOOSE)
- 12-provider failover chain with auto-fallback
- 6 inference APIs used during training for reward shaping
- 2 training-to-deployment paths: compressed (3 steps) and direct (2 steps)
