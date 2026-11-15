//! WASM Education — Cognitive & Semantic Learning Modules
//! 
//! This crate provides WebAssembly modules for interactive educational
//! visualizations covering cognitive science, semantic networks, 
//! graph theory, neural dynamics, and computational thinking.
//! 
//! Each module is designed for higher education and advanced dev learning,
//! with detailed labels, semantic annotations, and cognitive scaffolding.

#![allow(clippy::unused_async)]

use wasm_bindgen::prelude::*;
use serde::{Serialize, Deserialize};
use std::collections::{HashMap, HashSet};
use rand::prelude::*;
use web_sys::{console, CanvasRenderingContext2d, HtmlCanvasElement};
use nalgebra::{DVector, DMatrix};
use petgraph::graph::{NodeIndex, UnGraph};
use petgraph::algo::{connected_components, dijkstra, tarjan_scc};
use petgraph::visit::EdgeRef;
use fixedbitset::FixedBitSet;

// ─────────────────────────────────────────────────────────────────────────────
// PANIC HOOK & INIT
// ─────────────────────────────────────────────────────────────────────────────

#[wasm_bindgen(start)]
pub fn main() {
    #[cfg(feature = "console_error_panic_hook")]
    console_error_panic_hook::set_once();
    console::log_1(&"🧠 WASM Education loaded — cognitive modules ready".into());
}

// ─────────────────────────────────────────────────────────────────────────────
// CORE TYPES — Semantic Annotations
// ─────────────────────────────────────────────────────────────────────────────

/// Semantic label with cognitive metadata
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct SemanticLabel {
    pub text: String,
    pub concept_type: ConceptType,
    pub difficulty: DifficultyLevel,
    pub prerequisites: Vec<String>,
    pub learning_objectives: Vec<String>,
    pub cognitive_load: f32, // 0.0 - 1.0
    pub semantic_tags: Vec<String>,
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub enum ConceptType {
    Definition,
    Theorem,
    Algorithm,
    Visualization,
    Interactive,
    Analogy,
    Proof,
    Application,
    MetaCognition,
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub enum DifficultyLevel {
    Introductory,
    Intermediate,
    Advanced,
    Research,
}

/// Cognitive scaffold for progressive disclosure
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct CognitiveScaffold {
    pub level: usize,
    pub revealed_concepts: Vec<String>,
    pub hidden_concepts: Vec<String>,
    pub guidance: String,
    pub check_questions: Vec<CheckQuestion>,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct CheckQuestion {
    pub question: String,
    pub answer_type: AnswerType,
    pub correct_answer: String,
    pub explanation: String,
    pub concept_tested: String,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub enum AnswerType {
    MultipleChoice { options: Vec<String> },
    FreeText,
    Numeric,
    Visual,
}

// ─────────────────────────────────────────────────────────────────────────────
// MODULE 1: SEMANTIC NETWORK EXPLORER
// ─────────────────────────────────────────────────────────────────────────────

/// Interactive semantic network with spreading activation
#[wasm_bindgen]
pub struct SemanticNetwork {
    graph: UnGraph<SemanticNode, SemanticEdge>,
    activation: HashMap<NodeIndex, f32>,
    labels: HashMap<NodeIndex, SemanticLabel>,
    scaffold: CognitiveScaffold,
    rng: StdRng,
}

#[derive(Clone, Debug)]
struct SemanticNode {
    id: String,
    concept: String,
    node_type: NodeType,
    weight: f32,
}

#[derive(Clone, Debug, PartialEq)]
enum NodeType {
    Concept,
    Category,
    Instance,
    Relation,
    Property,
    Process,
}

#[derive(Clone, Debug)]
struct SemanticEdge {
    relation: String,
    strength: f32,
    bidirectional: bool,
}

#[wasm_bindgen]
impl SemanticNetwork {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        let mut network = Self {
            graph: UnGraph::new_undirected(),
            activation: HashMap::new(),
            labels: HashMap::new(),
            scaffold: CognitiveScaffold::default(),
            rng: StdRng::from_entropy(),
        };
        network.initialize_core_network();
        network
    }

    fn initialize_core_network(&mut self) {
        // Core cognitive science concepts
        let concepts = vec![
            ("working_memory", "Working Memory", NodeType::Concept, vec!["cognitive_psychology", "neuroscience"]),
            ("long_term_memory", "Long-Term Memory", NodeType::Concept, vec!["cognitive_psychology", "neuroscience"]),
            ("attention", "Attention", NodeType::Process, vec!["cognitive_psychology", "neuroscience"]),
            ("spreading_activation", "Spreading Activation", NodeType::Process, vec!["semantic_memory", "connectionism"]),
            ("semantic_priming", "Semantic Priming", NodeType::Concept, vec!["semantic_memory", "psycholinguistics"]),
            ("schema", "Schema", NodeType::Category, vec!["cognitive_psychology", "knowledge_representation"]),
            ("mental_model", "Mental Model", NodeType::Concept, vec!["cognitive_science", "reasoning"]),
            ("cognitive_load", "Cognitive Load", NodeType::Concept, vec!["educational_psychology", "instructional_design"]),
            ("dual_coding", "Dual Coding Theory", NodeType::Theorem, vec!["memory", "multimedia_learning"]),
            ("elaboration", "Elaboration", NodeType::Process, vec!["memory", "learning_strategies"]),
            ("retrieval_practice", "Retrieval Practice", NodeType::Algorithm, vec!["learning", "metacognition"]),
            ("spaced_repetition", "Spaced Repetition", NodeType::Algorithm, vec!["memory", "optimization"]),
            ("interleaving", "Interleaving", NodeType::Algorithm, vec!["learning", "optimization"]),
            ("metacognition", "Metacognition", NodeType::MetaCognition, vec!["self_regulation", "learning"]),
            ("transfer", "Transfer of Learning", NodeType::Concept, vec!["educational_psychology", "application"]),
        ];

        let mut node_indices = HashMap::new();
        for (id, concept, node_type, tags) in concepts {
            let idx = self.graph.add_node(SemanticNode {
                id: id.to_string(),
                concept: concept.to_string(),
                node_type,
                weight: 1.0,
            });
            node_indices.insert(id, idx);
            
            self.labels.insert(idx, SemanticLabel {
                text: concept.to_string(),
                concept_type: match node_type {
                    NodeType::Theorem => ConceptType::Theorem,
                    NodeType::Process => ConceptType::Algorithm,
                    NodeType::Category => ConceptType::Definition,
                    _ => ConceptType::Definition,
                },
                difficulty: DifficultyLevel::Intermediate,
                prerequisites: vec![],
                learning_objectives: vec![format!("Understand {}", concept)],
                cognitive_load: 0.5,
                semantic_tags: tags.iter().map(|s| s.to_string()).collect(),
            });
            self.activation.insert(idx, 0.0);
        }

        // Semantic relations
        let relations = vec![
            ("working_memory", "long_term_memory", "consolidation", 0.8, true),
            ("working_memory", "attention", "gatekeeping", 0.9, true),
            ("attention", "spreading_activation", "modulation", 0.7, true),
            ("spreading_activation", "semantic_priming", "mechanism", 0.85, true),
            ("schema", "mental_model", "instantiation", 0.75, true),
            ("cognitive_load", "working_memory", "capacity_limit", 0.9, true),
            ("dual_coding", "working_memory", "parallel_channels", 0.8, true),
            ("elaboration", "long_term_memory", "encoding", 0.85, true),
            ("retrieval_practice", "long_term_memory", "strengthening", 0.9, true),
            ("spaced_repetition", "retrieval_practice", "scheduling", 0.8, true),
            ("interleaving", "retrieval_practice", "variation", 0.7, true),
            ("metacognition", "retrieval_practice", "monitoring", 0.75, true),
            ("transfer", "mental_model", "application", 0.8, true),
            ("schema", "transfer", "framework", 0.7, true),
        ];

        for (src, tgt, relation, strength, bidirectional) in relations {
            if let (Some(&src_idx), Some(&tgt_idx)) = (node_indices.get(src), node_indices.get(tgt)) {
                self.graph.add_edge(src_idx, tgt_idx, SemanticEdge {
                    relation: relation.to_string(),
                    strength,
                    bidirectional,
                });
            }
        }

        // Initialize scaffold
        self.scaffold = CognitiveScaffold {
            level: 1,
            revealed_concepts: vec!["working_memory".to_string(), "attention".to_string()],
            hidden_concepts: vec!["spreading_activation".to_string(), "schema".to_string(), "metacognition".to_string()],
            guidance: "Start by exploring Working Memory and Attention — the gatekeepers of cognition.".to_string(),
            check_questions: vec![
                CheckQuestion {
                    question: "What limits the capacity of working memory?".to_string(),
                    answer_type: AnswerType::FreeText,
                    correct_answer: "Cognitive load and attentional resources".to_string(),
                    explanation: "Working memory has limited capacity (~4±1 chunks) governed by cognitive load theory.".to_string(),
                    concept_tested: "working_memory".to_string(),
                },
            ],
        };
    }

    /// Activate a concept and spread activation through the network
    #[wasm_bindgen]
    pub fn activate(&mut self, concept_id: &str, initial_activation: f32) -> JsValue {
        let node_idx = self.find_node(concept_id);
        if node_idx.is_none() {
            return JsValue::NULL;
        }
        let node_idx = node_idx.unwrap();
        
        // Reset activation
        for v in self.activation.values_mut() { *v = 0.0; }
        self.activation.insert(node_idx, initial_activation);
        
        // Spreading activation (3 iterations)
        for _ in 0..3 {
            let mut new_activation = self.activation.clone();
            for edge in self.graph.edge_references() {
                let (src, tgt) = (edge.source(), edge.target());
                let src_act = *self.activation.get(&src).unwrap_or(&0.0);
                let edge_strength = edge.weight().strength;
                let spread = src_act * edge_strength * 0.3; // decay factor
                let current = *new_activation.get(&tgt).unwrap_or(&0.0);
                new_activation.insert(tgt, (current + spread).min(1.0));
                if edge.weight().bidirectional {
                    let tgt_act = *self.activation.get(&tgt).unwrap_or(&0.0);
                    let back_spread = tgt_act * edge_strength * 0.3;
                    let current_src = *new_activation.get(&src).unwrap_or(&0.0);
                    new_activation.insert(src, (current_src + back_spread).min(1.0));
                }
            }
            self.activation = new_activation;
        }
        
        // Return activation state
        let result: HashMap<String, f32> = self.activation.iter()
            .filter_map(|(idx, &act)| {
                self.graph.node_weight(*idx).map(|n| (n.id.clone(), act))
            })
            .collect();
        serde_wasm_bindgen::to_value(&result).unwrap()
    }

    /// Get current cognitive scaffold state
    #[wasm_bindgen]
    pub fn get_scaffold(&self) -> JsValue {
        serde_wasm_bindgen::to_value(&self.scaffold).unwrap()
    }

    /// Advance scaffold level (progressive disclosure)
    #[wasm_bindgen]
    pub fn advance_scaffold(&mut self) -> JsValue {
        self.scaffold.level += 1;
        match self.scaffold.level {
            2 => {
                self.scaffold.revealed_concepts.extend(vec!["spreading_activation".to_string(), "schema".to_string()]);
                self.scaffold.hidden_concepts.retain(|c| c != "spreading_activation" && c != "schema");
                self.scaffold.guidance = "Explore Spreading Activation — how concepts prime each other through semantic links.".to_string();
                self.scaffold.check_questions.push(CheckQuestion {
                    question: "How does semantic priming demonstrate spreading activation?".to_string(),
                    answer_type: AnswerType::MultipleChoice { options: vec!["Faster recognition of related words", "Slower recognition of unrelated words", "No effect on recognition", "Only affects visual processing"].to_string() },
                    correct_answer: "Faster recognition of related words".to_string(),
                    explanation: "Priming activates related concepts, reducing retrieval time for semantically linked items.".to_string(),
                    concept_tested: "semantic_priming".to_string(),
                });
            }
            3 => {
                self.scaffold.revealed_concepts.push("metacognition".to_string());
                self.scaffold.hidden_concepts.retain(|c| c != "metacognition");
                self.scaffold.guidance = "Metacognition — monitoring your own learning. Try the retrieval practice questions.".to_string();
                self.scaffold.check_questions.push(CheckQuestion {
                    question: "What is the testing effect?".to_string(),
                    answer_type: AnswerType::FreeText,
                    correct_answer: "Retrieval practice strengthens memory more than re-reading".to_string(),
                    explanation: "Active recall creates stronger memory traces than passive review (Roediger & Karpicke, 2006).".to_string(),
                    concept_tested: "retrieval_practice".to_string(),
                });
            }
            _ => {}
        }
        serde_wasm_bindgen::to_value(&self.scaffold).unwrap()
    }

    /// Get network structure for visualization
    #[wasm_bindgen]
    pub fn get_graph_data(&self) -> JsValue {
        #[derive(Serialize)]
        struct GraphData {
            nodes: Vec<NodeData>,
            edges: Vec<EdgeData>,
        }
        #[derive(Serialize)]
        struct NodeData {
            id: String,
            label: String,
            x: f32,
            y: f32,
            node_type: String,
            activation: f32,
            semantic_tags: Vec<String>,
        }
        #[derive(Serialize)]
        struct EdgeData {
            source: String,
            target: String,
            relation: String,
            strength: f32,
        }

        // Simple force-directed layout (placeholder positions)
        let mut nodes = Vec::new();
        let mut rng = StdRng::seed_from_u64(42);
        for idx in self.graph.node_indices() {
            let node = self.graph.node_weight(idx).unwrap();
            let label = self.labels.get(&idx).unwrap();
            nodes.push(NodeData {
                id: node.id.clone(),
                label: node.concept.clone(),
                x: rng.gen_range(-300.0..300.0),
                y: rng.gen_range(-300.0..300.0),
                node_type: format!("{:?}", node.node_type),
                activation: *self.activation.get(&idx).unwrap_or(&0.0),
                semantic_tags: label.semantic_tags.clone(),
            });
        }

        let mut edges = Vec::new();
        for edge in self.graph.edge_references() {
            let src = self.graph.node_weight(edge.source()).unwrap();
            let tgt = self.graph.node_weight(edge.target()).unwrap();
            edges.push(EdgeData {
                source: src.id.clone(),
                target: tgt.id.clone(),
                relation: edge.weight().relation.clone(),
                strength: edge.weight().strength,
            });
        }

        serde_wasm_bindgen::to_value(&GraphData { nodes, edges }).unwrap()
    }

    fn find_node(&self, concept_id: &str) -> Option<NodeIndex> {
        self.graph.node_indices().find(|&idx| {
            self.graph.node_weight(idx).map(|n| n.id == concept_id).unwrap_or(false)
        })
    }
}

impl Default for CognitiveScaffold {
    fn default() -> Self {
        Self {
            level: 1,
            revealed_concepts: vec![],
            hidden_concepts: vec![],
            guidance: String::new(),
            check_questions: vec![],
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// MODULE 2: NEURAL DYNAMICS SIMULATOR
// ─────────────────────────────────────────────────────────────────────────────

/// Izhikevich neuron model with cognitive annotations
#[wasm_bindgen]
pub struct NeuralDynamics {
    neurons: Vec<NeuronState>,
    connections: Vec<Connection>,
    time: f32,
    dt: f32,
    labels: HashMap<usize, SemanticLabel>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
struct NeuronState {
    v: f32, // membrane potential
    u: f32, // recovery variable
    a: f32, // time scale of recovery
    b: f32, // sensitivity to subthreshold fluctuations
    c: f32, // after-spike reset value
    d: f32, // after-spike recovery
    neuron_type: NeuronType,
    firing_history: Vec<f32>,
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
enum NeuronType {
    RegularSpiking,      // Pyramidal cells
    FastSpiking,         // Interneurons
    LowThresholdSpiking, // Thalamic
    IntrinsicallyBursting, // Cortical layer 5
    Chattering,          // Visual cortex
    Resonator,           // Subthalamic
}

#[derive(Clone, Debug, Serialize, Deserialize)]
struct Connection {
    from: usize,
    to: usize,
    weight: f32,
    delay: f32,
    synapse_type: SynapseType,
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
enum SynapseType {
    Excitatory,
    Inhibitory,
    Modulatory,
}

#[wasm_bindgen]
impl NeuralDynamics {
    #[wasm_bindgen(constructor)]
    pub fn new(num_neurons: usize) -> Self {
        let mut sim = Self {
            neurons: Vec::new(),
            connections: Vec::new(),
            time: 0.0,
            dt: 0.1,
            labels: HashMap::new(),
        };
        sim.initialize_network(num_neurons);
        sim
    }

    fn initialize_network(&mut self, num_neurons: usize) {
        let types = [
            NeuronType::RegularSpiking,
            NeuronType::FastSpiking,
            NeuronType::LowThresholdSpiking,
            NeuronType::IntrinsicallyBursting,
            NeuronType::Chattering,
            NeuronType::Resonator,
        ];

        let mut rng = StdRng::from_entropy();
        for i in 0..num_neurons {
            let ntype = types[i % types.len()];
            let (a, b, c, d) = match ntype {
                NeuronType::RegularSpiking => (0.02, 0.2, -65.0, 8.0),
                NeuronType::FastSpiking => (0.1, 0.2, -65.0, 2.0),
                NeuronType::LowThresholdSpiking => (0.02, 0.25, -65.0, 2.0),
                NeuronType::IntrinsicallyBursting => (0.02, 0.2, -55.0, 4.0),
                NeuronType::Chattering => (0.02, 0.2, -50.0, 2.0),
                NeuronType::Resonator => (0.1, 0.26, -65.0, 2.0),
            };
            self.neurons.push(NeuronState {
                v: -65.0,
                u: b * -65.0,
                a, b, c, d,
                neuron_type: ntype.clone(),
                firing_history: Vec::new(),
            });
            self.labels.insert(i, SemanticLabel {
                text: format!("{} Neuron #{}", format!("{:?}", ntype), i),
                concept_type: ConceptType::Visualization,
                difficulty: DifficultyLevel::Advanced,
                prerequisites: vec!["izhikevich_model".to_string(), "membrane_potential".to_string()],
                learning_objectives: vec!["Observe spiking dynamics", "Understand neuron types".to_string()],
                cognitive_load: 0.7,
                semantic_tags: vec!["computational_neuroscience", "spiking_networks", "izhikevich".to_string()],
            });
        }

        // Random sparse connectivity (10% connection probability)
        for i in 0..num_neurons {
            for j in 0..num_neurons {
                if i != j && rng.gen::<f32>() < 0.1 {
                    let synapse_type = if rng.gen::<f32>() < 0.8 { SynapseType::Excitatory } else { SynapseType::Inhibitory };
                    self.connections.push(Connection {
                        from: i,
                        to: j,
                        weight: rng.gen_range(0.5..5.0),
                        delay: rng.gen_range(1.0..5.0),
                        synapse_type,
                    });
                }
            }
        }
    }

    /// Run simulation step
    #[wasm_bindgen]
    pub fn step(&mut self, input_current: &JsValue) -> JsValue {
        let currents: Vec<f32> = serde_wasm_bindgen::from_value(input_current).unwrap_or_else(|_| vec![0.0; self.neurons.len()]);
        
        // Izhikevich dynamics
        for (i, neuron) in self.neurons.iter_mut().enumerate() {
            let i_syn = currents.get(i).copied().unwrap_or(0.0);
            
            // v' = 0.04*v^2 + 5*v + 140 - u + I
            // u' = a*(b*v - u)
            neuron.v += self.dt * (0.04 * neuron.v * neuron.v + 5.0 * neuron.v + 140.0 - neuron.u + i_syn);
            neuron.u += self.dt * (neuron.a * (neuron.b * neuron.v - neuron.u));
            
            // Spike detection
            if neuron.v >= 30.0 {
                neuron.firing_history.push(self.time);
                neuron.v = neuron.c;
                neuron.u += neuron.d;
                
                // Propagate to connected neurons
                for conn in &self.connections {
                    if conn.from == i {
                        let target = &mut self.neurons[conn.to];
                        let w = match conn.synapse_type {
                            SynapseType::Excitatory => conn.weight,
                            SynapseType::Inhibitory => -conn.weight,
                            SynapseType::Modulatory => conn.weight * 0.5,
                        };
                        // Delayed synaptic input (simplified)
                        target.v += w * 0.1;
                    }
                }
            }
            
            // Keep history bounded
            if neuron.firing_history.len() > 1000 {
                neuron.firing_history.drain(0..500);
            }
        }
        
        self.time += self.dt;
        
        // Return membrane potentials and spike times
        #[derive(Serialize)]
        struct StepResult {
            potentials: Vec<f32>,
            spikes: Vec<usize>,
            time: f32,
        }
        
        let result = StepResult {
            potentials: self.neurons.iter().map(|n| n.v).collect(),
            spikes: self.neurons.iter().enumerate()
                .filter(|(_, n)| n.firing_history.last() == Some(&(self.time - self.dt)))
                .map(|(i, _)| i)
                .collect(),
            time: self.time,
        };
        serde_wasm_bindgen::to_value(&result).unwrap()
    }

    /// Get neuron labels with cognitive metadata
    #[wasm_bindgen]
    pub fn get_labels(&self) -> JsValue {
        serde_wasm_bindgen::to_value(&self.labels).unwrap()
    }

    /// Set simulation time step
    #[wasm_bindgen]
    pub fn set_dt(&mut self, dt: f32) {
        self.dt = dt.clamp(0.01, 1.0);
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// MODULE 3: GRAPH ALGORITHM VISUALIZER
// ─────────────────────────────────────────────────────────────────────────────

/// Interactive graph algorithms with step-by-step execution
#[wasm_bindgen]
pub struct GraphAlgorithmVisualizer {
    graph: UnGraph<String, f32>,
    algorithm_state: AlgorithmState,
    step_history: Vec<AlgorithmStep>,
    current_step: usize,
    labels: HashMap<NodeIndex, SemanticLabel>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
enum AlgorithmState {
    Idle,
    Dijkstra { source: NodeIndex, target: Option<NodeIndex>, distances: HashMap<NodeIndex, f32>, visited: FixedBitSet, pq: Vec<(f32, NodeIndex)> },
    TarjanSCC { index: usize, stack: Vec<NodeIndex>, on_stack: FixedBitSet, indices: HashMap<NodeIndex, usize>, lowlinks: HashMap<NodeIndex, usize>, sccs: Vec<Vec<NodeIndex>> },
    ConnectedComponents { components: Vec<Vec<NodeIndex>> },
    MST { edges: Vec<(NodeIndex, NodeIndex, f32)>, mst_edges: Vec<(NodeIndex, NodeIndex, f32)>, uf: UnionFind },
}

#[derive(Clone, Debug, Serialize, Deserialize)]
struct AlgorithmStep {
    description: String,
    highlighted_nodes: Vec<NodeIndex>,
    highlighted_edges: Vec<(NodeIndex, NodeIndex)>,
    data_snapshot: serde_json::Value,
}

#[derive(Clone, Debug)]
struct UnionFind {
    parent: Vec<usize>,
    rank: Vec<usize>,
}

impl UnionFind {
    fn new(n: usize) -> Self { Self { parent: (0..n).collect(), rank: vec![0; n] } }
    fn find(&mut self, x: usize) -> usize {
        if self.parent[x] != x { self.parent[x] = self.find(self.parent[x]); }
        self.parent[x]
    }
    fn union(&mut self, x: usize, y: usize) -> bool {
        let rx = self.find(x); let ry = self.find(y);
        if rx == ry { return false; }
        if self.rank[rx] < self.rank[ry] { self.parent[rx] = ry; }
        else if self.rank[rx] > self.rank[ry] { self.parent[ry] = rx; }
        else { self.parent[ry] = rx; self.rank[rx] += 1; }
        true
    }
}

#[wasm_bindgen]
impl GraphAlgorithmVisualizer {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        let mut viz = Self {
            graph: UnGraph::new_undirected(),
            algorithm_state: AlgorithmState::Idle,
            step_history: Vec::new(),
            current_step: 0,
            labels: HashMap::new(),
        };
        viz.create_sample_graph();
        viz
    }

    fn create_sample_graph(&mut self) {
        // Create a sample graph with cognitive science concepts
        let concepts = vec![
            "Perception", "Attention", "Working Memory", "Long-Term Memory",
            "Language", "Reasoning", "Decision Making", "Problem Solving",
            "Metacognition", "Learning", "Transfer", "Expertise"
        ];
        
        let mut indices = HashMap::new();
        for c in concepts {
            let idx = self.graph.add_node(c.to_string());
            indices.insert(c, idx);
            self.labels.insert(idx, SemanticLabel {
                text: c.to_string(),
                concept_type: ConceptType::Definition,
                difficulty: DifficultyLevel::Intermediate,
                prerequisites: vec![],
                learning_objectives: vec![format!("Understand {} in cognitive architecture", c)],
                cognitive_load: 0.4,
                semantic_tags: vec!["cognitive_architecture".to_string(), "cognitive_science".to_string()],
            });
        }

        // Add edges representing cognitive process flow
        let edges = vec![
            ("Perception", "Attention", 0.9),
            ("Attention", "Working Memory", 0.95),
            ("Working Memory", "Long-Term Memory", 0.8),
            ("Working Memory", "Language", 0.7),
            ("Working Memory", "Reasoning", 0.85),
            ("Working Memory", "Decision Making", 0.75),
            ("Working Memory", "Problem Solving", 0.9),
            ("Long-Term Memory", "Reasoning", 0.7),
            ("Long-Term Memory", "Problem Solving", 0.65),
            ("Language", "Reasoning", 0.6),
            ("Reasoning", "Decision Making", 0.8),
            ("Problem Solving", "Metacognition", 0.7),
            ("Metacognition", "Learning", 0.85),
            ("Learning", "Transfer", 0.75),
            ("Transfer", "Expertise", 0.8),
            ("Expertise", "Problem Solving", 0.6), // Feedback loop
        ];

        for (src, tgt, weight) in edges {
            if let (Some(&s), Some(&t)) = (indices.get(src), indices.get(tgt)) {
                self.graph.add_edge(s, t, weight);
            }
        }
    }

    /// Run Dijkstra's algorithm step by step
    #[wasm_bindgen]
    pub fn run_dijkstra(&mut self, source_label: &str, target_label: Option<String>) -> JsValue {
        let source_idx = self.find_node(source_label);
        let target_idx = target_label.as_ref().and_then(|t| self.find_node(t));
        
        if source_idx.is_none() { return JsValue::NULL; }
        let source_idx = source_idx.unwrap();
        
        self.algorithm_state = AlgorithmState::Idle;
        self.step_history.clear();
        self.current_step = 0;
        
        let mut distances: HashMap<NodeIndex, f32> = HashMap::new();
        let mut visited = FixedBitSet::with_capacity(self.graph.node_count());
        let mut pq: Vec<(f32, NodeIndex)> = Vec::new();
        
        for idx in self.graph.node_indices() {
            distances.insert(idx, f32::INFINITY);
        }
        distances.insert(source_idx, 0.0);
        pq.push((0.0, source_idx));
        
        self.step_history.push(AlgorithmStep {
            description: format!("Initialize: Set distance to source '{}' = 0, all others = ∞", 
                self.graph.node_weight(source_idx).unwrap()),
            highlighted_nodes: vec![source_idx],
            highlighted_edges: vec![],
            data_snapshot: serde_json::json!({ "distances": distances.clone() }),
        });
        
        while let Some((dist, current)) = pq.pop() {
            if visited.contains(current.index()) { continue; }
            visited.insert(current.index());
            
            self.step_history.push(AlgorithmStep {
                description: format!("Visit '{}' (distance = {:.2})", 
                    self.graph.node_weight(current).unwrap(), dist),
                highlighted_nodes: vec![current],
                highlighted_edges: vec![],
                data_snapshot: serde_json::json!({ "distances": distances.clone(), "visited": visited.clone() }),
            });
            
            if Some(current) == target_idx { break; }
            
            for edge in self.graph.edges(current) {
                let neighbor = edge.target();
                if visited.contains(neighbor.index()) { continue; }
                
                let new_dist = dist + *edge.weight();
                if new_dist < *distances.get(&neighbor).unwrap_or(&f32::INFINITY) {
                    distances.insert(neighbor, new_dist);
                    pq.push((new_dist, neighbor));
                    pq.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
                    
                    self.step_history.push(AlgorithmStep {
                        description: format!("Relax edge {} → {}: new distance = {:.2}",
                            self.graph.node_weight(current).unwrap(),
                            self.graph.node_weight(neighbor).unwrap(),
                            new_dist),
                        highlighted_nodes: vec![current, neighbor],
                        highlighted_edges: vec![(current, neighbor)],
                        data_snapshot: serde_json::json!({ "distances": distances.clone(), "visited": visited.clone() }),
                    });
                }
            }
        }
        
        self.algorithm_state = AlgorithmState::Dijkstra {
            source: source_idx,
            target: target_idx,
            distances,
            visited,
            pq,
        };
        
        serde_wasm_bindgen::to_value(&self.step_history).unwrap()
    }

    /// Get next step in algorithm execution
    #[wasm_bindgen]
    pub fn next_step(&mut self) -> JsValue {
        if self.current_step >= self.step_history.len() {
            return JsValue::NULL;
        }
        let step = self.step_history[self.current_step].clone();
        self.current_step += 1;
        serde_wasm_bindgen::to_value(&step).unwrap()
    }

    /// Reset to beginning
    #[wasm_bindgen]
    pub fn reset(&mut self) {
        self.current_step = 0;
    }

    /// Get graph structure for visualization
    #[wasm_bindgen]
    pub fn get_graph_data(&self) -> JsValue {
        #[derive(Serialize)]
        struct GraphData {
            nodes: Vec<NodeData>,
            edges: Vec<EdgeData>,
        }
        #[derive(Serialize)]
        struct NodeData {
            id: String,
            label: String,
            x: f32,
            y: f32,
        }
        #[derive(Serialize)]
        struct EdgeData {
            source: String,
            target: String,
            weight: f32,
        }

        let mut nodes = Vec::new();
        let mut rng = StdRng::seed_from_u64(123);
        for idx in self.graph.node_indices() {
            let label = self.graph.node_weight(idx).unwrap();
            nodes.push(NodeData {
                id: format!("{:?}", idx),
                label: label.clone(),
                x: rng.gen_range(-400.0..400.0),
                y: rng.gen_range(-300.0..300.0),
            });
        }

        let mut edges = Vec::new();
        for edge in self.graph.edge_references() {
            let src = self.graph.node_weight(edge.source()).unwrap();
            let tgt = self.graph.node_weight(edge.target()).unwrap();
            edges.push(EdgeData {
                source: src.clone(),
                target: tgt.clone(),
                weight: *edge.weight(),
            });
        }

        serde_wasm_bindgen::to_value(&GraphData { nodes, edges }).unwrap()
    }

    fn find_node(&self, label: &str) -> Option<NodeIndex> {
        self.graph.node_indices().find(|&idx| {
            self.graph.node_weight(idx).map(|n| n == label).unwrap_or(false)
        })
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// MODULE 4: COGNITIVE LOAD SIMULATOR
// ─────────────────────────────────────────────────────────────────────────────

/// Simulates cognitive load during learning tasks
#[wasm_bindgen]
pub struct CognitiveLoadSimulator {
    working_memory_capacity: usize,
    current_load: f32,
    intrinsic_load: f32,
    extraneous_load: f32,
    germane_load: f32,
    schema_count: usize,
    automation_level: f32,
    time_pressure: f32,
    labels: HashMap<String, SemanticLabel>,
}

#[wasm_bindgen]
impl CognitiveLoadSimulator {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        let mut sim = Self {
            working_memory_capacity: 4, // Miller's 7±2 → modern 4±1
            current_load: 0.0,
            intrinsic_load: 0.0,
            extraneous_load: 0.0,
            germane_load: 0.0,
            schema_count: 0,
            automation_level: 0.0,
            time_pressure: 0.0,
            labels: HashMap::new(),
        };
        sim.initialize_labels();
        sim
    }

    fn initialize_labels(&mut self) {
        self.labels.insert("intrinsic_load".to_string(), SemanticLabel {
            text: "Intrinsic Cognitive Load".to_string(),
            concept_type: ConceptType::Definition,
            difficulty: DifficultyLevel::Intermediate,
            prerequisites: vec!["working_memory".to_string()],
            learning_objectives: vec!["Understand element interactivity".to_string()],
            cognitive_load: 0.3,
            semantic_tags: vec!["cognitive_load_theory", "instructional_design".to_string()],
        });
        self.labels.insert("extraneous_load".to_string(), SemanticLabel {
            text: "Extraneous Cognitive Load".to_string(),
            concept_type: ConceptType::Definition,
            difficulty: DifficultyLevel::Intermediate,
            prerequisites: vec![],
            learning_objectives: vec!["Identify poor instructional design".to_string()],
            cognitive_load: 0.3,
            semantic_tags: vec!["cognitive_load_theory", "ux_design".to_string()],
        });
        self.labels.insert("germane_load".to_string(), SemanticLabel {
            text: "Germane Cognitive Load".to_string(),
            concept_type: ConceptType::Definition,
            difficulty: DifficultyLevel::Advanced,
            prerequisites: vec!["schema_acquisition".to_string()],
            learning_objectives: vec!["Design for schema construction".to_string()],
            cognitive_load: 0.4,
            semantic_tags: vec!["cognitive_load_theory", "learning_optimization".to_string()],
        });
        self.labels.insert("schema".to_string(), SemanticLabel {
            text: "Schema".to_string(),
            concept_type: ConceptType::Definition,
            difficulty: DifficultyLevel::Introductory,
            prerequisites: vec![],
            learning_objectives: vec!["Understand chunking and automation".to_string()],
            cognitive_load: 0.2,
            semantic_tags: vec!["cognitive_psychology", "expertise".to_string()],
        });
    }

    /// Simulate a learning task
    #[wasm_bindgen]
    pub fn simulate_task(&mut self, element_count: usize, element_interactivity: f32, 
                         instructional_quality: f32, learner_expertise: f32) -> JsValue {
        // Intrinsic load: element count × interactivity / expertise
        self.intrinsic_load = (element_count as f32 * element_interactivity) / (1.0 + learner_expertise * 3.0);
        
        // Extraneous load: inverse of instructional quality
        self.extraneous_load = (1.0 - instructional_quality) * 2.0;
        
        // Germane load: what's left for schema construction
        let total_capacity = self.working_memory_capacity as f32;
        self.germane_load = (total_capacity - self.intrinsic_load - self.extraneous_load).max(0.0);
        
        // Time pressure increases all loads
        if self.time_pressure > 0.5 {
            let pressure_multiplier = 1.0 + self.time_pressure;
            self.intrinsic_load *= pressure_multiplier;
            self.extraneous_load *= pressure_multiplier;
        }
        
        self.current_load = self.intrinsic_load + self.extraneous_load + self.germane_load;
        
        // Schema automation reduces future intrinsic load
        if self.germane_load > 1.0 {
            self.schema_count += 1;
            self.automation_level = (self.schema_count as f32 * 0.1).min(0.8);
        }
        
        #[derive(Serialize)]
        struct LoadResult {
            intrinsic: f32,
            extraneous: f32,
            germane: f32,
            total: f32,
            capacity: f32,
            overloaded: bool,
            schema_count: usize,
            automation: f32,
            recommendations: Vec<String>,
        }
        
        let mut recommendations = Vec::new();
        if self.intrinsic_load > total_capacity * 0.6 {
            recommendations.push("Reduce element interactivity or provide pre-training".to_string());
        }
        if self.extraneous_load > total_capacity * 0.3 {
            recommendations.push("Improve instructional design: remove split-attention, redundancy".to_string());
        }
        if self.germane_load < 0.5 {
            recommendations.push("Increase germane load: add worked examples, self-explanation prompts".to_string());
        }
        if self.current_load > total_capacity {
            recommendations.push("⚠️ COGNITIVE OVERLOAD: Reduce complexity immediately".to_string());
        }
        
        let result = LoadResult {
            intrinsic: self.intrinsic_load,
            extraneous: self.extraneous_load,
            germane: self.germane_load,
            total: self.current_load,
            capacity: total_capacity,
            overloaded: self.current_load > total_capacity,
            schema_count: self.schema_count,
            automation: self.automation_level,
            recommendations,
        };
        
        serde_wasm_bindgen::to_value(&result).unwrap()
    }

    /// Set time pressure (0.0 - 1.0)
    #[wasm_bindgen]
    pub fn set_time_pressure(&mut self, pressure: f32) {
        self.time_pressure = pressure.clamp(0.0, 1.0);
    }

    /// Get cognitive load labels
    #[wasm_bindgen]
    pub fn get_labels(&self) -> JsValue {
        serde_wasm_bindgen::to_value(&self.labels).unwrap()
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// EXPORTS — Module Registry
// ─────────────────────────────────────────────────────────────────────────────

#[wasm_bindgen]
pub fn get_module_registry() -> JsValue {
    #[derive(Serialize)]
    struct ModuleInfo {
        name: String,
        description: String,
        cognitive_domain: String,
        difficulty: String,
        key_concepts: Vec<String>,
        learning_objectives: Vec<String>,
    }

    let modules = vec![
        ModuleInfo {
            name: "SemanticNetwork".to_string(),
            description: "Interactive semantic network with spreading activation — explore how concepts prime each other in memory".to_string(),
            cognitive_domain: "Semantic Memory / Cognitive Psychology".to_string(),
            difficulty: "Intermediate".to_string(),
            key_concepts: vec!["Spreading Activation", "Semantic Priming", "Working Memory", "Schema Theory", "Cognitive Scaffolding".to_string()],
            learning_objectives: vec![
                "Understand how activation spreads through semantic networks".to_string(),
                "Experience progressive disclosure of cognitive concepts".to_string(),
                "Learn retrieval practice and metacognitive monitoring".to_string(),
            ],
        },
        ModuleInfo {
            name: "NeuralDynamics".to_string(),
            description: "Izhikevich spiking neuron simulator with 6 biologically-plausible neuron types".to_string(),
            cognitive_domain: "Computational Neuroscience".to_string(),
            difficulty: "Advanced".to_string(),
            key_concepts: vec!["Action Potentials", "Neuron Types", "Synaptic Transmission", "Network Dynamics", "Excitatory/Inhibitory Balance".to_string()],
            learning_objectives: vec![
                "Observe different spiking patterns across neuron types".to_string(),
                "Understand excitation-inhibition balance in networks".to_string(),
                "Explore how network dynamics emerge from single-cell properties".to_string(),
            ],
        },
        ModuleInfo {
            name: "GraphAlgorithmVisualizer".to_string(),
            description: "Step-by-step execution of graph algorithms (Dijkstra, Tarjan SCC, MST) on cognitive architecture graphs".to_string(),
            cognitive_domain: "Graph Theory / Cognitive Architecture".to_string(),
            difficulty: "Intermediate".to_string(),
            key_concepts: vec!["Shortest Path", "Strongly Connected Components", "Minimum Spanning Tree", "Cognitive Process Flow".to_string()],
            learning_objectives: vec![
                "Trace algorithm execution step by step".to_string(),
                "Understand how cognitive processes form graph structures".to_string(),
                "Apply graph algorithms to cognitive architectures".to_string(),
            ],
        },
        ModuleInfo {
            name: "CognitiveLoadSimulator".to_string(),
            description: "Real-time cognitive load simulation based on Cognitive Load Theory (Sweller, 1988)".to_string(),
            cognitive_domain: "Educational Psychology / Instructional Design".to_string(),
            difficulty: "Intermediate".to_string(),
            key_concepts: vec!["Intrinsic Load", "Extraneous Load", "Germane Load", "Schema Acquisition", "Automation".to_string()],
            learning_objectives: vec![
                "Calculate cognitive load for learning tasks".to_string(),
                "Design instruction that optimizes germane load".to_string(),
                "Identify and reduce extraneous load".to_string(),
            ],
        },
    ];

    serde_wasm_bindgen::to_value(&modules).unwrap()
}