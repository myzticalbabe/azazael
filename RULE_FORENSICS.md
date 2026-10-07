# RULE_FORENSICS.md — archaeological analysis of the 39 canonical rules

> *Created 2026-09-30 in response to: "WE HAVE TO ANALYZE AND REWRITE THING
> AFTER RESTART. FORENSICALLY INVESTIGATE THE RULES ARCHEOLOGICALLY TO DETERMINE
> THEIR BIRTH AND PURPOSE. SUGGEST."*
> *Status: ANALYSIS AND PROPOSAL ONLY. Nothing here has been changed. The
> rewrite is post-restart work.*

---

## 1. The archaeology — four birth waves

| wave | dates | n | character |
|---|---|---|---|
| **I. Founding** | Jun 7–8 2026 | 13 | Core safety: don't claim done, don't reinterpret, don't guess |
| **II. Expansion** | Jun 10–14 2026 | 16 | Governance: agents, VLP, compliance infrastructure |
| **III. Reactive patch** | Jun 12–17 2026 | 7 | Rules written *after* a specific incident |
| **IV. Verification** | Sep 30 2026 | 3 | `0B-B`, `0B-C`, `0B-D` — predicates and negative controls |

**Wave I (Jun 7–8)** — `0A` `0B` `0C` `0D` `0E` `0F` `0G` `0H` `0I` `0J`
`0K` `0P` `0B-A`. Thirteen rules in two days. These are the *load-bearing* ones:
don't claim completion, follow the user literally, read the canon, don't guess.
They are also, almost without exception, the ones violated hardest.

**Wave II (Jun 10–14)** — `0J-A` `0L` `0M` `0N` `0Q` `0R` `0R-A` `0T` `0U`
`0V` `0W` `0X` `0Y` `0Z` `0Z-B` `0Z-C` `0Z-F`. Sixteen rules in five days. This
is the **harness expansion** — the period when the multi-agent and VLP
infrastructure was being built. Notice the character shift: wave I is about
*truthfulness to the user*, wave II is about *process discipline across agents*.

**Wave III (Jun 12–17)** — `0Z-B` `0Z-C` `0R-A` `0Z-F` `0Z-G` `0Z-I` `0S`.
These are patch-layer rules, each born from a specific incident. They are the
most valuable by purpose (a rule that exists because of a real failure) and the
least enforceable by nature (a numeric or behavioural demand).

**Wave IV (Sep 30, today)** — `0B-B` `0B-C` `0B-D`. All three are *meta* rules
about verification rather than about the work itself. They are the first rules
in the set that carry their own enforcement mechanism.

### Duplicates and undated rules
- `0E` and `0E-1` — both mandate the 10-phase multi-tier protocol. `0J` and
  `0S` — both are the pre-action assertion banner. Measured: **no token-overlap
  threshold separates the true pair `0J`/`0S` (0.308) from the false pair
  `0C`/`0J` (0.308)**, so semantic duplicate detection cannot find these; they
  were found by hand.
- `0B`, `0E-1` and `0S` carry **no date in their own heading**. `0B` was
  re-edicted today and lost its date. The others were never dated.

---

## 2. The provenance gap — the archaeology is weak, and that matters

| evidence source | what it actually holds |
|---|---|
| `git log MANDATES.md` | **2 commits total.** First is 2026-06-21, *"snapshot ALL project files"*. |
| `ERROR_LOG.md` | **164 entries, only 35 carry a date** in the heading. **129 undated.** |
| rule headings | birth dates are **self-reported prose**, never machine-verified |

**Consequence:** the canon was never version-controlled before 2026-06-21, and
has had two commits since. There is **no git archaeology** for how the rules
evolved — no diffs, no dates of change, no attribution. Every birth date above
is a claim the file makes about itself.

The `0A ← errors 72, 75, 76, 77, 78, 144, 147, 152` reverse-provenance map
(which rules cite which errors) was computed from the text, and it is the only
*derived* provenance that exists. It shows waves I and II rules accumulating
errors for **three months** — `0A` eight errors, `0K` eight, `0H` eight, `0J`
eight — which is the strongest available evidence that wave I/II rules are
**failing persistently rather than occasionally**.

---

## 3. The dependency graph — five chains

```
AUTHORITY      user ──> 0B ──> 0P (priority chain) ──> 0B-A
                              (0B-B, 0B-C, 0D added 2026-09-30)

VERIFICATION   0A (don't claim done) ──> 0T (VLP) ──> 0T-A / 0T-B
                                                    └──> 0B-B, 0B-C, 0B-D

ENFORCEMENT    0K (read the canon) ──> 0J (pre-action gate)
               ──> 0J-A (MECHANICAL gate: unlock 644 / re-lock 444)
               ──> 0C (sentinel audit) ──> 0X (compliance infra) / 0Y (governance)

AGENTS         0G (spawn gemini) ──> 0M (concurrent) ──> 0V (code reviewer)
               ──> 0W (100% utilization) ──> 0Z / 0Z-A / 0Z-F (parallel)

REACTIVITY     0H (record anti-patterns) ──> 0H-A (verify) ──> 0Z-G (no busy work)
```

---

## 4. The two structural findings

### Finding A — the ENFORCEMENT chain is severed at its last link

`0K` says *read the canon*. `0J` says *print an assertion block*. `0J-A` says the
gate must be **mechanical**: canon files are `444`, unlocked to `644` by an
authorised gate, re-locked after. `0C` audits it.

**The mechanical half never shipped.** Measured 2026-09-30:

- All seven canon files were found **writable** — the `444` regime `0J-A`
  describes was never applied.
- `sentinel_gate.py` has **no pre-action trigger point**. TERENCE's
  `gate_timing` oracle (ast-based, so a docstring does not count) reports
  **"no file in `scripts/` or `src/` INVOKES the pre-action gate"**. Its only
  trigger points are git hooks and CI — both *post*-work.

So the chain reads `0K → 0J → 0J-A`, and the link that would have made `0K`
binding was never built. **That is the root cause of today's violations.** Every
breach of `0K`, `0B` and `0A` traces to one missing mechanism, not to 39
independent failures.

**Status today:** `prepare_guard.py` implements the mechanical half — canon is
read-only, a permit requires a fresh `prepare()` receipt, and it was verified to
block `Add-Content`, `open(...,'a')`, **and this agent's own Edit tool**.

### Finding B — the AGENTS chain is unsatisfiable in this client

`0G`, `0M`, `0V`, `0W`, `0Z`, `0Z-A`, `0Z-F`, `0Z-I` all mandate spawning
specific agents. The tool roster available here is **`explore`** and
**`general`** only. The mandated agents — `thinker-with-files-gemini`
(referenced 25× in ERROR_LOG), `code-reviewer-deepseek` (14×), `thinker-gpt`
(3×) — **do not exist as agent types in this client.**

`providers.py` **does** exist (`src/CORE/inference/providers.py`), so `0D` and
`0Z-I`'s provider layer is satisfiable even though their agent layer is not.

**Consequence: eight rules cannot be complied with as written, and their
compliance has never been possible.** A rule that cannot be satisfied does not
constrain behaviour; it only adds reading cost and produces a permanent, invisible
failure.

---

## 5. SUGGESTED DISPOSITION — per chain

The test I applied: **what happens if this rule is broken, and does anything
notice?** Default is RETIRE, because a rule that cannot be checked is a rule
that costs reading and buys nothing.

### AUTHORITY — consolidate, do not delete
| rule | suggestion |
|---|---|
| `0B` + `0P` + `0B-A` | **MERGE into one.** Three rules say the user's directive is absolute. `0B-A` is the strongest text. Keep `0B-A`, retire `0P` (duplicates it), keep `0B` as the short form. Leave a tombstone at each retired ID. |
| `0B-B` `0B-C` `0B-D` | **KEEP — highest value in the set.** These three carry their own enforcement (the `0B-A` hook, negative controls, exercised-or-unknown). They are the template for everything else. |
| `0D` | **KEEP, but verify satisfiable.** `providers.py` exists. Needs a real probe: does it return 6 providers *now*? If not, it is a wave-I rule that aged out. |

### VERIFICATION — keep the spine, re-anchor the rest
| rule | suggestion |
|---|---|
| `0A` | **ENFORCE FIRST.** Highest priority in the set. Violated today, and it is the rule that would have caught it. Needs a verifier, not a reminder — the natural one is a delivery-time check that the claimed output exists. |
| `0T` `0T-A` | **KEEP.** VLP works: `verify_head_hash()` → True, three trails anchored today. |
| `0T-B` | **AUDIT.** The 15-layer stack — no oracle references it and no test covers it. Either demonstrate a layer or reduce the claim. |
| `0Q` | **MERGE into `0T`** (post-phase check is a verification act). Today 0Q and 0Q-A are separate and 0Q-A is gated while 0Q is not. |

### ENFORCEMENT — the priority chain
| rule | suggestion |
|---|---|
| `0K` | **KEEP, now enforceable.** The rule that matters most, and `prepare_guard` makes it binding for the first time. |
| `0J` | **REWRITE.** `0J` and `0S` are the same rule. Keep one, and **strike the "permanent / cannot be skipped" language** — the gate did not run, so that sentence was false for its entire life. Replace with what is actually wired. |
| `0J-A` | **KEEP — now actually implemented** by `prepare_guard.py`. It was correct all along and simply never applied. |
| `0C` `0X` `0Y` | **AUDIT.** 0X has 8 components and 0Y has 5. Establish how many are live; a component list that is mostly inert should be reduced to the live set. |

### AGENTS — retire the unsatisfiable, keep the achievable
| rule | suggestion |
|---|---|
| `0G` `0M` `0V` `0W` `0Z` `0Z-A` `0Z-F` | **RETIRE or REWRITE as capability-conditional.** All eight mandate agents that do not exist here. A better form: *"spawn `general` in parallel when the work decomposes into ≥2 independent units"* — which is satisfiable and expresses the same intent. |
| `0Z-B` (exactly eleven followups) | **RETIRE.** A cosmetic quota. It was violated today, it enforces nothing, and it costs a number in every single response. |
| `0Z-I` | **SPLIT.** The provider half (`providers.py`) is satisfiable; the agent half is not. Keep the satisfiable half. |
| `0Z-C` (destructive basher gate) | **KEEP and ENFORCE.** Real blast radius, mechanically checkable, and `prepare_guard` already does exactly this for canon. Extend the pattern. |

### REACTIVITY — keep
| rule | suggestion |
|---|---|
| `0H` `0H-A` `0Z-G` | **KEEP.** Record the failure, verify the fix, no busy work. These are the rules that produced `ERROR_LOG.md`, which is the only derived provenance in the entire system. |

---

## 6. The post-restart work, in order

1. **Establish provenance before rewriting.** 129 of 164 errors are undated and
   canon has 2 commits. Fix that *first* — a rewrite of an undated canon
   destroys the last evidence of why anything exists.
2. **Date and attribute every rule**, and start versioning canon properly so the
   next rewrite has an archaeology.
3. **Apply the Finding A disposition to the ENFORCEMENT chain first.** It is
   the chain whose severing caused today's failures, and `prepare_guard` already
   implements the missing half.
4. **Retire the eight unsatisfiable AGENTS rules** — or rewrite them
   capability-conditionally against the roster that actually exists.
5. **Merge the two duplicate pairs**, leaving tombstones.
6. **Then** the VERIFICATION and AUTHORITY chains, which are the highest-value
   text but largely sound already.

---

## 7. The honest caveat

This is analysis of **text, dates and self-reported headings**, plus two things
I measured today (the gate's trigger points, the canon's permissions). I have
**not** read all 39 rule bodies in full, I have not read 129 undated errors, and
I have no version-control history to check any of it against. The dispositions
above are reasoned from structure and from today's evidence. Before the rewrite,
the rules should be read in full — because the pattern that produced today's
failures is exactly a conclusion drawn from a sample instead of the whole.
