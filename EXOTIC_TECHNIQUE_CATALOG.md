# EXOTIC TECHNIQUE CATALOG

Beyond SOTA. `EVOLUTION_SOTA_EXPANSION_PLAN.md` (ANIMA) repaired the loop;
`PROTEUS_DEEP_EXPANSION.md` broke its ceilings. This document goes further out:
techniques that change what the search *is*, not just how fast it moves.

Working definition used throughout: a technique is **exotic** here if it changes
the **representation** of the search (what a solution *is*, what a world *is*,
what an optimiser *is*) rather than merely its dynamics. Tuning a CMA-ES
covariance is not exotic. Encoding the solution as a developmental program is.

Constraints that decide feasibility (verified on this machine):

| Constraint | Value |
|---|---|
| GPU | Intel Arc 140T, **8 GB shared with 16 GB system RAM** |
| torch | `2.14.0+xpu`, **GIL interpreter only** (free-threaded cannot host it) |
| Available | `scipy`, `sklearn`, `networkx`, `optuna`, `torch` |
| Missing | `jax`, `numba`, `gpytorch`, `botorch`, `ripser`/`gudhi`, `deap`, `pymoo`, `evotorch`, `nevergrad`, `cma`, `torchdiffeq`, `hyperopt` |

So: small models, no GPU-only libraries, and anything exotic is hand-rolled on
numpy/scipy/torch. That constraint is a *filter*, and it kills a few items below
honestly.

---

## Tier 1 — Indirect and developmental encodings
*Breaks: the genome-size ceiling. The correct answer to "how many knobs can they have?"*

The current genome is a fixed 4-vector, and PROTEUS's Morph makes it a variable
vector. Both are **direct** encodings: one gene, one parameter. Indirect encodings
decouple genome size from phenotype size entirely.

### 1.1 CPPN / HyperNEAT — compositional pattern-producing networks
A tiny network (the CPPN) is the genome. Its **input is a coordinate** and its
**output is the value at that coordinate**. Query it over a geometry and an
arbitrarily large phenotype is *generated* from a handful of parameters.
The CPPN's weights are the genes.

- Why exotic: the genome has ~30 numbers; the phenotype can have millions.
  Scaling the network up requires zero new genes.
- Adjacent: NEAT's historical markings and complexification solve the *topology*
  search; HyperNEAT adds the geometric substrate.
- Fit here: replaces Morph's `add_gene` with "grow the queried region", and the
  4-gene ceiling becomes a non-issue by construction.
- Cost: a CPPN forward pass per coordinate is cheap; batched on XPU it is
  trivial. **Genuinely feasible.**

### 1.2 Gene Regulatory Networks / artificial embryogeny
The genome is a set of *rules*, and the phenotype **develops** by iterating those
rules over a cell lattice. Regulation (activation thresholds, inhibition) means
one gene can have different effects in different regions.
- Why exotic: identical genes, different phenotypes — context-dependent
  expression, which is how biology escapes the direct-encoding ceiling.
- Risk: development is iterative and can be slow; needs a fixed iteration budget.

### 1.3 Reaction-diffusion / Turing morphogenesis
Two morphogens, one activator and one inhibitor, with diffusion coefficients in
the genome. Spontaneous pattern formation (spots, stripes) from a uniform start.
- Why exotic: **pattern without specification**. The genome encodes a mechanism,
  not an outcome. Of everything in this catalog this is the most literally
  "alive", and it pairs naturally with the repo's existing `dreaming` /
  morphogenesis-adjacent naming.
- Fit: a morphogen field could parameterise *where* in a neural phenotype
  capacity is allocated.

### 1.4 L-systems and cellular encoding
Rewriting grammars / cellular automata as the genotype. Growth is a derivation.
- Why exotic: the genotype *is a program*, and its length grows with the
  phenotype's complexity. Strongest structural novelty pressure available.

---

## Tier 2 — Continuous-time and "liquid" computation
*Breaks: the tabular-learner ceiling, without needing a big GPU.*

### 2.1 Liquid Time-Constant Networks (LTC)
Continuous-time RNNs whose time constants are **input-dependent**, giving
adaptive, stable dynamics with very few parameters (Hasani et al., MIT).
- Why exotic: the network's *temporal behaviour* is a learned function, not a
  fixed decay. Tiny parameter count suits an 8 GB shared iGPU exactly.
- Fit: replaces the Q-table in `Nerve`. The "liquid" framing also matches the
  enlivened theme directly.

### 2.2 Neural ODEs / SDEs
Replace discrete layers/steps with a differential equation solved by an
integrator; the *vector field* is the learned object.
- Why exotic: the model is a flow, not a stack. Adjoint gradients.
- Blocker: `torchdiffeq` is missing and would be hand-rolled. Also the existing
  horizon (`max_steps`) interacts awkwardly with continuous time.

### 2.3 Reservoir computing / Echo State Networks
Random recurrent dynamics, **only the readout is trained**. No BPTT.
- Why exotic: most of the network is never trained, and it still works. Extremely
  cheap — a real fit for the hardware.
- Fit: an excellent *cheap surrogate* for the Oracle's inner model.

### 2.4 Predictive coding / Forward-Forward
Inference by iterative local energy minimisation; learning with **no
backpropagation** at all (Rao & Ballard; Hinton's Forward-Forward).
- Why exotic: it discards the entire backprop paradigm — the single most
  entrenched assumption in the stack.
- Fit: biologically plausible, layer-local, and it sidesteps the fact that XPU
  autograd on an integrated GPU is the bottleneck.

### 2.5 Spiking neural networks / neuromorphic encodings
Computation as event timing rather than activations.
- Why exotic: temporal codes, STDP local learning rules.
- Blocker: no neuromorphic hardware here; simulated SNNs on an iGPU lose the
  efficiency argument that justifies them.

---

## Tier 3 — Exotic optimisation dynamics
*Breaks: the "fixed optimiser" assumption.*

### 3.1 Stein Variational Gradient Descent (SVGD)
A **population of particles** that flow deterministically to a posterior under a
kernelised gradient. Not MCMC, not GD — an interacting particle system.
- Why exotic: it gives a *distribution* over solutions, not one solution, in a
  single deterministic pass. That is exactly what Cranium's posterior needs.
- Fit: **the strongest single upgrade to Cranium.** Implementable with
  `scipy`/`torch` kernels.

### 3.2 Natural Evolution Strategies / natural gradient
Optimise in the space of distributions using the **Fisher information metric**
(xNES, sNES), plus second-order natural-gradient methods (K-FAC).
- Why exotic: gradient in a *statistical manifold* rather than Euclidean space.
- Fit: better-conditioned than CMA-ES's covariance heuristics.

### 3.3 CMA-MAE / CMA-ME (Quality-Diversity)
CMA-ES driving a MAP-Elites archive, with an **archive-learning-rate** that
turns the improvement criterion from a hard threshold into a continuous
annealing signal. State of the art in QD, and it is what should replace the
4x4 grid (PROTEUS's Cortex).
- Why exotic: it is EA + QD unified, and the MAE relaxation is a subtle, strong
  trick. **High value, fully feasible.**

### 3.4 Differentiable Quality-Diversity
Differentiable QD / DQD — approximate expected QD gradients to make archive
improvement differentiable.
- Why exotic: it merges gradient learning with QD, usually considered opposites.
- Blocker: needs a differentiable fitness; our fitness is a black-box trainer.

### 3.5 Memetic and cultural algorithms
GA plus per-individual local search, with **culture**: an explicit belief space
that individuals both draw from and contribute to, transmitted across
generations independent of the genotype.
- Why exotic: inheritable *learned* information that is not in the genome — a
  second inheritance channel.
- Fit: directly serves E4. The belief space is exactly the cross-era memory that
  era-pinning destroys.

### 3.6 Lévy-flight and slime-mould foraging
Heavy-tailed step distributions (Lévy) rather than Gaussian; slime-mould and
ant-colony stigmergic optimisation.
- Why exotic: heavy-tailed mutation escapes local optima where Gaussian cannot —
  and E3's flat trajectories are precisely a local-optimum signature.
- Cost: essentially free to implement. **Cheap exoticism with a real target.**

### 3.7 Thermal / Ising and Boltzmann machinery
Map the search onto a spin system and use simulated or quantum annealing;
Boltzmann machines for the surrogate.
- Why exotic: statistical-physics framing, temperature as an explicit resource.
- Blocker: real quantum annealing needs hardware.

---

## Tier 4 — Information, drive and cybernetic theory
*Breaks: the "one scalar reward" assumption. This is where "enlivened" lives.*

### 4.1 Empowerment
Maximise the **channel capacity** between the agent's actions and its future
states — the agent seeks *influence over its own future*, with no task reward.
- Why exotic: intrinsic motivation defined information-theoretically; the drive
  is not a hand-tuned bonus term.
- Fit: a principled replacement for ad-hoc novelty bonuses when Loom detects
  archive collapse.

### 4.2 DIAYN / variational skill discovery
Learn skills that maximise mutual information with the state, so diversity is
*emergent and unsupervised* rather than a penalty term.
- Why exotic: skills without a task. Diversity becomes a first-class product.

### 4.3 Free-energy principle / active inference
The system minimises **variational free energy** — a single objective that
unifies exploration, exploitation, uncertainty reduction and model learning.
- Why exotic: one principle replaces the entire stack of separate losses and
  gates we have been hand-building.
- Fit: the Cranium + Oracle + Crucible stack *is* an ad-hoc approximation of
  active inference. Stating it properly would unify them.

### 4.4 MDL / rate-distortion genome economics
Charge the genome rent via description length. A gene must earn back its
bits of description.
- Why exotic: complexity control as an information-theoretic price, not a
  regularisation coefficient.
- Fit: **exactly** the principled version of PROTEUS's "gene economics".

### 4.5 Viability theory / Ashby's law / autopoiesis and Beer's Viable System Model
Regulate to stay inside a *viable set* rather than optimising a scalar;
self-producing organisation as the system's defining property.
- Why exotic: homeostatic survival instead of maximisation; VSM gives a
  ready-made 5-system architecture (operations, coordination, control,
  intelligence, identity) that maps onto Cranium/Circulation/Crucible/Anima.
- Fit: the most philosophically apt frame for "truly enlivened", and it is a
  *governance* structure, so it can be layered on without new numerics.

---

## Tier 5 — Representation exotica
*Breaks: the "weights are floats in a tensor" assumption.*

### 5.1 Hyperdimensional computing / Vector Symbolic Architectures
Represent everything as high-dimensional bipolar/holographic vectors; *bind*
with circular convolution and *bundle* with addition.
- Why exotic: computation by algebra on irreducible distributed codes; famously
  robust and extremely cheap. Fits the hardware budget well.
- Fit: a natural substrate for the Curator/Crucible pool algebra.

### 5.2 Hypernetworks
A network that **outputs the weights** of another network.
- Why exotic: the thing being learned is a generator of learners.
- Fit: the cleanest way to make `Nerve`'s plasticity rule task-conditioned.

### 5.3 Kolmogorov-Arnold Networks (KAN)
Learnable activation functions on edges rather than fixed activations on nodes.
- Why exotic: a direct challenge to the MLP's core architectural assumption.
- Cost: heavier per parameter than an MLP; questionable on an iGPU.

### 5.4 Fast weights / Hebbian test-time plasticity
Weights that update during inference from the activations themselves.
- Why exotic: memory *in* the weights, no separate store.

---

## Tier 6 — Self-referential and open-ended
*Breaks: the separation between the searcher and the searched.*

### 6.1 Self-Taught Optimizer (STOP) / AI Generating Algorithms
An LLM improves its own scaffolding by proposing changes to the code that
produced it, then keeping what scores better. "Recursive self-improvement" as a
concrete, bounded loop.
- Why exotic: the optimiser edits the optimiser.
- Blocker: needs a sandbox and a reliable scorer before it is safe. High risk of
  the system confidently degrading itself.

### 6.2 DreamCoder / library learning (Stitch, Babble)
Wake-sleep program induction where the system **invents reusable abstractions**
and adds them to its own library, so later problems are solved with a richer
language.
- Why exotic: the system grows its own vocabulary. This is the strongest
  principled form of open-endedness short of ALIFE.
- Fit: the honest version of PROTEUS's Morph — new genes *should* be invented
  abstractions, not random extra slots.

### 6.3 Minimal-criterion ALIFE / self-replicating programs
Selection only requires passing a viability threshold; self-replication and
self-modification are permitted.
- Why exotic: life-like rather than benchmark-like. Unbounded by any task.

### 6.4 Gödel machines / AIXI approximations
Optimal self-referential search with provable optimality; Solomonoff induction.
- Why exotic: incomputable / unprovable in practice.
- Verdict: **included for completeness only — do not attempt.** It would absorb
  unlimited effort and produce nothing runnable.

---

## Shortlist: the five actually worth pursuing

| # | Technique | Breaks | Feasible? |
|---|---|---|---|
| 1 | **CPPN / HyperNEAT** indirect encoding | genome-size ceiling, properly | Yes — batched on XPU |
| 2 | **SVGD** particle posterior for Cranium | single-point evidence | Yes — scipy/torch kernels |
| 3 | **CMA-MAE** for the archive | 16-cell QD grid | Yes — pure numpy |
| 4 | **Lévy-flight mutation** | E3 local optima | Yes — near-free |
| 5 | **Memetic / cultural belief space** | E4 evidence resets | Yes — a second store |

Runners-up: **LTC** if the tabular learner is ever replaced; **MDL gene
economics** when Morph lands; **free-energy / active inference** as the unifying
frame once the components exist to unify.

## Explicitly rejected, with reasons

- **Gödel machine / AIXI** — incomputable. Aspirational, not implementable.
- **Spiking neuromorphic** — the efficiency argument requires neuromorphic
  silicon; simulated SNNs on an iGPU are strictly worse than the MLP.
- **Neural ODEs / differentiable QD** — both need differentiability our fitness
  does not provide, and `torchdiffeq` is absent.
- **STOP / recursive self-improvement** — the failure mode (confident
  self-degradation) is worse than the payoff, and it needs a sandbox we do not
  have.

## The discipline that makes this usable

Two rules, both learned the hard way in the 2026-09-11 investigation:

1. **Exoticism is not progress.** Every technique above must beat the incumbent
   on a fixed criterion before it replaces anything. E9 already showed a +3.3
   margin that bought 0/4 holdout passes — impressive-looking movement that
   transferred to nothing.
2. **Report the representation alongside the score.** If the encoding changes,
   fitness is no longer comparable across cycles; a headline number without its
   dimension and encoding is not a result.
