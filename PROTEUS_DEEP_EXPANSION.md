# PROTEUS — DEEP EXPANSION: OPEN-ENDED, METAMORPHIC, IMAGINED

Companion to `EVOLUTION_SOTA_EXPANSION_PLAN.md` (ANIMA, the first tier).
This document goes further: not "add stronger optimisers", but change what the
system *is* — a search whose search space, environments and optimiser all evolve.

Status: design proposal. Supersedes ANIMA phases 2-4 where they overlap.

## 0. The hardware truth, first

The GPU directive is satisfiable but **not via CUDA**:

| | |
|---|---|
| GPU | **Intel(R) Arc(TM) 140T (8 GB, integrated)** |
| `nvidia-smi` | not present |
| CUDA | **impossible** — no NVIDIA hardware |
| `torch-directml` | no wheel for Python 3.14 |
| **`torch 2.14.0+xpu`** | **available and installing** — the correct backend |
| Wheel tag | `cp314-cp314` → **GIL builds only** |

Two consequences that shape everything below:

1. **XPU is integrated and shares 16 GB of system RAM.** There is no dedicated
   VRAM budget. Every model in this design must be *small* — hundreds of
   thousands of parameters, not millions. A 768 MB torch wheel does not mean
   GPU headroom.
2. **The free-threaded interpreter cannot host torch.** Under `python3.14t.exe`
   both `torch` and `numpy` fail on ABI (`numpy._core._multiarray_umath`
   missing; torch needs `cp314t` wheels that do not exist). So the existing
   free-threaded pipeline and any GPU-accelerated component run in **different
   interpreters**. They must communicate through durable artefacts (the JSON
   state files and the `evolution_result` rows), not in-process calls.

That split is an architectural constraint, not a temporary annoyance, and the
design below treats it as such.

## 1. Why the first tier is not enough

ANIMA (Cranium, Crucible, Circulation, Hyperband) is *repair*: it fixes E4, E5,
E9, E10 by making the existing loop statistically honest. It does not change the
fact that:

- the genome is a **fixed 4-dimensional vector**;
- the optimiser is a **fixed** GA/CMA/DE mixture;
- the environments are **consumed**, never produced;
- the learner is **tabulated** (Q-table over `source:severity`).

Every one of those is a hard ceiling that no amount of better gating lifts.
PROTEUS attacks the ceilings themselves.

## 2. PROTEUS

**P**opulation-based **R**ecursive **O**pen-ended **T**ransformative
**E**volution with **U**ncertainty-aware **S**earch.

Seven organs, each replacing a specific ceiling.

### 2.1 Morph — metamorphic genomes *(removes the genome-size ceiling)*

The direct answer to "how many knobs can they have?": **unbounded, because the
genome can grow.**

- A genome is a *variable-length* typed record, not a fixed tuple. Genes carry a
  type (`float | int | bool | choice | schedule`) — `EvolutionEngine` already
  supports all four via `set_gene_specs`, so this extends existing machinery
  rather than replacing it.
- **Structural mutation operators**: `add_gene`, `drop_gene`, `rewire_gene`
  (re-point a gene at a different trainer kwarg), `nest` (turn a scalar into a
  3-point schedule). These mutate the *search space*, not a point in it.
- A **viability filter** rejects structurally invalid genomes (unparseable,
  duplicated, or referencing a kwarg the trainer does not accept), which is
  essential — most structural mutations are lethal, and that is expected.
- **Gene economics.** Every gene must pay rent: a gene whose variance collapses
  to zero across the archive is *pruned*, and the freed dimension triggers a
  re-exploration. This is how the genome stays small even though it can grow.

This is the single largest conceptual jump in the plan: from optimising a vector
to optimising a *representation*.

### 2.2 Oracle — the fitness world model *(removes the "one number" ceiling)*

A small **deep ensemble** (K=5 MLPs, ~10^5 params — sized for shared memory)
predicts `fitness(genes, era_descriptor) → (mean, variance)`.

Three uses, in ascending order of ambition:

1. **Acquisition.** Score candidates cheaply on GPU, evaluate only the
   high-uncertainty / high-mean ones. This is where GPU money is actually
   earned — not in the trainer, which is tiny.
2. **Counterfactual era imagination** — the important one. Because era is an
   *input*, the model can be queried across an **imagined distribution of
   eras** the system has never run. Promotion then requires a genome to win
   across that imagined distribution, not on one fresh pool.
3. This is what E9 demands. Today a +3.3 margin on the snapshot pool bought
   **0/4** holdout passes: the pool was overfitted. Requiring wins under
   *imagined* era variation is a far stronger test than a single fresh draw, and
   it is measurable against criterion 1 of the ANIMA plan.

`dreaming.py` already emits synthetic eval rows and mines failure patterns — the
Oracle gives those dreams a quantitative, gated use instead of being advisory.

### 2.3 Arena — co-evolved environments *(removes the "fixed world" ceiling)*

**POET-style paired open-ended co-evolution.** Environments (pool configurations:
severity mix, hard-alert ratio, era pressure) and solutions evolve *together*.

- Environments mutate toward **novelty** (a mutated environment must be solvable
  by its paired solution but nontrivial for the population).
- Solutions **transfer**: a genome that solves environment A is tested on the
  frontier of B. Transfer success is the selection pressure.
- This makes E9 structurally impossible: there is no static pool left to overfit,
  because the pool is an evolving adversary, and it makes E3 impossible in the
  same stroke — open-endedness is defined by *never converging*.

### 2.4 Nerve — neuromodulated plasticity *(removes the tabular-learner ceiling)*

The inner learner is today a Q-table keyed on `source:severity` with 4 scalar
hyperparameters. Nerve replaces the hyperparameters with a **learned plasticity
rule**: a small network emits *per-parameter* update modulations conditioned on
context (a "neuromodulator"), trained by the outer loop's success signal.

- This is learning-to-learn: the outer loop stops choosing a learning rate and
  starts choosing a *policy over learning*.
- Fits the shared-memory budget because the modulator is small and the Q-table
  is already low-dimensional.
- Note the free-threading split: Nerve trains under the GIL interpreter.

### 2.5 Loom — topological novelty drive *(removes the "one scalar" diversity problem)*

Track the **shape** of the archive, not just its coverage. Persistent homology
over the descriptor point cloud detects when the archive is collapsing into a
single blob (exactly E3's flat trajectories).

- Cheap proxy if a TDA dependency is unavailable: eigenvalue decay of the
  descriptor covariance (intrinsic dimension) plus a distance-matrix spectrum.
- When intrinsic dimension falls below a homeostatic setpoint, novelty pressure
  engages — a *drive*, not a fixed coefficient.

### 2.6 Chorus — structural proposer *(extends variation beyond sampling)*

A FunSearch-style LLM operator over the already-installed
`CORE/inference/providers.py` (16 providers, cached via `inference_cache.py`).
It proposes **structural** edits from Morph's operator set, conditioned on the
observed failure modes (holdout-failure logs, pinned-gene reports).

- CPU/network-side, so it does not compete for XPU memory.
- Must be budget-capped and fail-open; it is a *voice*, not the driver.

### 2.7 Cranium + Circulation — from ANIMA, unchanged

Hierarchical Bayesian cross-era evidence and the Thompson-sampled compute
allocator remain the statistical floor. In PROTEUS the allocator's arms become
`{GA, CMA-ES, DE, Chorus, Morph-structural, Arena-environment}`, so the
scheduler can fund *structural* moves, not just numeric ones.

## 3. How the organs close the observed failures

| Observed failure | Root cause | PROTEUS organ |
|---|---|---|
| **E3** elite freeze, 42/50 flat | fixed genome, elitist best is flat by construction | Morph (new dimensions), Loom (novelty drive), Arena (never converges) |
| **E4** 28 eras, evidence resets | era-pinned evidence | Cranium (era = random effect) |
| **E5** margins chase a drifting baseline | fixed threshold | Cranium (posterior), Oracle (era-conditioned) |
| **E9** +3.3 margin → 0/4 holdout | one frozen pool, overfit | Oracle (imagined eras), Arena (adversarial pool) |
| **E10** arm starved 50/50 | fixed `2x` gate | Circulation (bandit, no threshold) |
| **4-gene ceiling** | fixed vector | Morph (unbounded) |
| **Tabular learner** | no function approximation | Nerve (learned plasticity) |

## 4. Phasing (each phase independently falsifiable)

| Phase | Organ(s) | Measured by |
|---|---|---|
| **A** | Install XPU; add a device abstraction; batched GPU fitness path | `torch.xpu.is_available()`, batch throughput vs serial |
| **B** | Oracle (ensemble + acquisition) | proxy rank correlation; GPU utilisation |
| **C** | Oracle counterfactual era gate | **holdout pass rate > 0** (currently 0/4) |
| **D** | Circulation + Cranium | operator allocation spread; evidence spans >=3 eras |
| **E** | Morph (structural mutation + gene economics) | genome dimension grows then stabilises; new best > 4-gene best |
| **F** | Arena (POET co-evolution) | transfer success rate; novelty never zero |
| **G** | Nerve, Loom, Chorus | learner ceiling; intrinsic dimension; proposal acceptance |

Phase **A** is already in progress (install). Phase **C** is the phase that
decides whether any of this is real: if imagined-era gating does not produce
holdout passes, the Oracle is not modelling anything useful and D-G are moot.

## 5. Non-negotiable constraints

1. **Model size budget**: total XPU-resident parameters stay small; 8 GB is
   *shared with the OS*. If it does not fit in a few hundred MB, it does not ship.
2. **Two-interpreter split**: GPU components (GIL interpreter) ↔ pipeline
   (free-threaded). Communicate via JSON artefacts and the memory store. No
   in-process coupling, no shared live objects.
3. **Never gate on the pool you optimise.** Arena makes the pool adversarial;
   the gate must read the Oracle's imagined eras or a keeper set. This is the
   lesson E9 already cost us.
4. **Fail-open everything new.** Chorus, Oracle, Arena are advisory until they
   beat the incumbent on a measured criterion.
5. **One variable per batch.** Morph changes the genome; Arena changes the
   world. Landing both before measuring either reproduces the confounding we
   avoided when widening bounds before adding a gene.

## 6. The honest risk

The deepest risk is not technical. It is that **metamorphic genomes make results
incomparable**: if the genome can grow, "fitness 25.04" no longer means the same
thing across cycles, and every historical comparison in this repo — including the
50-run batches — becomes era-specific in a new way.

Mitigation: Morph must record genome *dimension* alongside fitness, and any
headline number must be reported per dimension. Without that discipline, open-
endedness buys movement we cannot interpret, which is precisely the failure mode
we just spent a 50-run batch diagnosing.
