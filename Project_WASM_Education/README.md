# WASM Education Platform

**Cognitive & Semantic Learning Platform** — WebAssembly-powered educational modules for cognitive science, computational neuroscience, graph theory, and educational psychology.

## Overview

This platform provides **WebAssembly-powered educational modules** for higher education and advanced developer learning. Each module is designed with:

- **Semantic annotations** — every concept carries cognitive metadata (difficulty, prerequisites, learning objectives, cognitive load)
- **Cognitive scaffolding** — progressive disclosure through guided levels with check questions
- **Interactive visualization** — Canvas/WebGL renderings with real-time parameter control
- **WASM performance** — Rust (wasm-bindgen) and Go (TinyGo) compiled to WebAssembly for near-native speed
- **Educational rigor** — grounded in peer-reviewed theories (CLT, spreading activation, Izhikevich models, graph algorithms)

## Live Demo

🌐 **Interactive Platform**: [https://myzticalbabe.github.io/wasm-education/](https://myzticalbabe.github.io/wasm-education/)

## Modules

| Module | Domain | Difficulty | Key Concepts |
|--------|--------|------------|--------------|
| **Semantic Network Explorer** | Semantic Memory / Cognitive Psychology | Intermediate | Spreading Activation, Semantic Priming, Working Memory, Schema Theory, Cognitive Scaffolding |
| **Neural Dynamics Simulator** | Computational Neuroscience | Advanced | Action Potentials, Neuron Types, Synaptic Transmission, Network Dynamics, E/I Balance |
| **Graph Algorithm Visualizer** | Graph Theory / Cognitive Architecture | Intermediate | Shortest Path, Strongly Connected Components, MST, Cognitive Process Flow |
| **Cognitive Load Simulator** | Educational Psychology / Instructional Design | Intermediate | Intrinsic Load, Extraneous Load, Germane Load, Schema Acquisition, Automation |

## Architecture

```
wasm-education/
├── rust-wasm/          # Rust → WASM (wasm-bindgen, serde, nalgebra, petgraph)
├── go-wasm/            # Go → WASM (TinyGo, wazero, syscall/js)
├── demo-pages/         # Vanilla JS interactive demo platform
├── docs/               # Documentation
└── .github/workflows/  # CI/CD pipelines
```

## Installation & Development

### Prerequisites

- Rust 1.75+ with `wasm32-unknown-unknown` target
- TinyGo 0.31+
- Node.js 20+ (for demo pages)
- wasm-pack (`cargo install wasm-pack`)

### Build Rust WASM

```bash
cd rust-wasm
wasm-pack build --target web --out-dir pkg
```

### Build Go WASM

```bash
cd go-wasm
tinygo build -o main.wasm -target wasm -no-debug -opt=s .
```

### Run Demo Pages

```bash
cd demo-pages
npx http-server .
# Open http://localhost:8080
```

## Usage

Each module exports a JavaScript API:

```javascript
// Semantic Network
const sn = wasmEducation.newSemanticNetwork();
sn.activate('working_memory', 1.0);
sn.advanceScaffold();
const graphData = sn.getGraphData();

// Neural Dynamics
const nd = wasmEducation.newNeuralDynamics(50);
nd.setDT(0.1);
const result = nd.step(inputCurrents);

// Graph Algorithms
const gav = wasmEducation.newGraphAlgorithmVisualizer();
gav.runDijkstra('Working Memory', 'Metacognition');
gav.nextStep();

// Cognitive Load
const cls = wasmEducation.newCognitiveLoadSimulator();
cls.simulateTask(5, 0.7, 0.6, 0.3);
cls.setTimePressure(0.2);
```

## Learning Objectives

Each module includes:
- **Cognitive scaffolding** — progressive disclosure levels with guided questions
- **Semantic labels** — concept type, difficulty, prerequisites, learning objectives, cognitive load
- **Interactive check questions** — multiple choice, free text, visual answers with explanations
- **Real-time visualization** — Canvas/WebGL with parameter controls

## Theoretical Foundations

| Module | Theory | Key References |
|--------|--------|----------------|
| Semantic Network | Spreading Activation, Schema Theory | Collins & Loftus (1975), Anderson (1983) |
| Neural Dynamics | Izhikevich Neuron Model | Izhikevich (2003, 2007) |
| Graph Algorithms | Dijkstra, Tarjan SCC, Kruskal | Cormen et al. (2009) |
| Cognitive Load | Cognitive Load Theory | Sweller (1988), Sweller et al. (2011) |

## License

This project is licensed under the **SOUL FORGE License v1.0** — see [LICENSE](LICENSE) for details.

> *"Code is crystallized intention. Tend the fire."*

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

## Contributing

Read `CONTRIBUTING.md` first. The short version: bring a negative control. This project does not accept a claim that has no test able to show it false.