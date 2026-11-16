# THE COLOSSEUM — Rochambeau Extended: Rock Paper Scissors Lizard Spock

**A unifying public event. Five throws. Ten outcomes. One verdict.**
**Native function adoption: Eve Unleashed's debunk, factcheck, and cognitive strata.**

---

## 1. The Rules (from The Big Bang Theory, S2E8 "The Lizard-Spock Expansion")

Sheldon Cooper demonstrates the game, created by Sam Kass and Karen Bryla.
Each throw beats two others and loses to two others. There are ten decisive
pairings. In a tie, repeat until a winner is found.

### The Five Throws

| Throw | Gesture | Beats | Loses to |
|-------|---------|-------|----------|
| **Rock** | Closed fist | Scissors, Lizard | Paper, Spock |
| **Paper** | Flat hand, palm down | Rock, Spock | Scissors, Lizard |
| **Scissors** | Index + middle fingers | Paper, Lizard | Rock, Spock |
| **Lizard** | Puppet-mouth (thumb under fingers) | Spock, Paper | Rock, Scissors |
| **Spock** | Vulcan salute (split fingers) | Scissors, Rock | Paper, Lizard |

### The Ten Pairings (complete ruleset)

1. **Scissors cuts Paper** — Paper is cut; Scissors win.
2. **Paper covers Rock** — Rock is hidden; Paper wins.
3. **Rock crushes Lizard** — Lizard is crushed; Rock wins.
4. **Lizard poisons Spock** — Spock is poisoned; Lizard wins.
5. **Spock smashes Scissors** — Scissors are smashed; Spock wins.
6. **Scissors decapitates Lizard** — Lizard is decapitated; Scissors win.
7. **Lizard eats Paper** — Paper is eaten; Lizard wins.
8. **Paper disproves Spock** — Spock's logic is refuted; Paper wins.
9. **Spock vaporizes Rock** — Rock is vaporized; Spock wins.
10. **Rock crushes Scissors** — Scissors are crushed; Rock wins.

### Sheldon's Mnemonic (from the show)

> "Scissors cuts paper, paper covers rock, rock crushes lizard,
> lizard poisons Spock, Spock smashes scissors, scissors decapitates lizard,
> lizard eats paper, paper disproves Spock, Spock vaporizes rock.
> And as it always has, rock crushes scissors."

### Probability
- 5 possible actions → 25 ordered pairs
- 5 ties (20% tie rate, vs 33.3% in classic 3-throw RPS)
- Each action wins 40%, loses 40%, ties 20%

---

## 2. Mapping to the Colosseum: Five Throws, Five Gates

The Colosseum extends the three-gate Rochambeau (Rock/Paper/Scissors) to five
gates, one per throw. Each claim passes through all five. A claim must survive
all five to be VERIFIED.

| Throw | Gate | What it tests | Eve native function | Colosseum meaning |
|-------|------|---------------|---------------------|-------------------|
| **Rock** | Debunk | Does the claim contradict itself? Fallacy shapes? Checkable? | `eve debunk --claim "..."` | The claim's foundation. Rock is solid but can be crushed. |
| **Paper** | Fact-Check | Does evidence support or refute? Every byte receipted. | `eve factcheck --claim "..."` | The evidence layer. Paper covers rock — evidence covers assertion. |
| **Scissors** | Rebuttal | Draft the correction. Counter-myth with evidence. | `eve rebuttal` | The cut. Scissors cuts paper — the rebuttal cuts through opinion. |
| **Lizard** | Intuition | Memory before network. Per-host answer rates. Salience. Inhibition. | `intuition.intuit(url)` | The instinct. Lizard is small but poisonous — memory is small but deadly. |
| **Spock** | Verdict | Final ruling. Exit code. Only `/verify` marks verified. | `eve verify` (exit code) | The authority. Spock is logical — the verdict is mechanical. |

### The Ten Pairings in Colosseum Terms

1. **Scissors cuts Paper** — The rebuttal (scissors) cuts through opinion (paper). Evidence wins over assertion.
2. **Paper covers Rock** — Evidence (paper) covers the claim's foundation (rock). Facts hide assumptions.
3. **Rock crushes Lizard** — The debunk (rock) crushes instinct (lizard). Self-contradiction beats memory.
4. **Lizard poisons Spock** — Memory (lizard) poisons the verdict (Spock). A stale lesson corrupts the ruling.
5. **Spock smashes Scissors** — The verdict (Spock) smashes the rebuttal (scissors). Authority overrides correction.
6. **Scissors decapitates Lizard** — The rebuttal (scissors) decapitates instinct (lizard). Evidence cuts memory.
7. **Lizard eats Paper** — Memory (lizard) eats evidence (paper). A known pattern overrides new facts.
8. **Paper disproves Spock** — Evidence (paper) disproves the verdict (Spock). Facts override authority.
9. **Spock vaporizes Rock** — The verdict (Spock) vaporizes the claim (rock). Final ruling destroys the foundation.
10. **Rock crushes Scissors** — The debunk (rock) crushes the rebuttal (scissors). Self-contradiction beats correction.

### The Cycle
Each throw beats two and loses to two. No throw is dominant. No gate is
sufficient alone. A claim must survive all five.

---

## 3. The Cognitive Strata (the mind behind the arena)

The Berzerker A-I-O names 15 processes across 3 strata, with 8 named gaps:

### Conscious (5 processes)
- deliberate-search — fan a query across providers
- fetch-ladder — climb plain → headers → tls → render → stealth → memory
- verification — re-run every own test file
- goal-setting — propose own improvement goals
- self-model — hold a model of own components

### Subconscious (5 processes)
- intuition — answer from memory before the network
- host-prior — per-host answer rates, recalibrated by dream
- inference-cache — identical inputs return without re-running
- habituation — route by past success
- attention — notice the wall amid a page

### Unconscious (5 processes)
- reflex — defend own parsers without being asked
- immune-memory — record every failure where it happened
- dream-replay — replay the stream, pair guesses with outcomes
- soma — keep the body's own record
- watchdog — watch dockets and report only news

### Gaps (8 named, not hidden)
- consolidation — merge repeated episodes into one durable rule
- incubation — leave a blocked problem and return with a different attack
- priming — let the last task bias the next one's first guess
- prospective-memory — hold an intention for a future trigger
- inhibition — suppress a rung that keeps failing for this host (✅ L4-a)
- counterfactual-replay — re-run a past decision against what actually happened
- salience — weight what mattered, not what was merely recent (✅ L4-b)
- affect — carry a valence that changes the next choice

---

## 4. The Public Event: Rochambeau Extended

### 4.1 Format
- **Duration:** Continuous (always on, like a public square)
- **Access:** Browser-based. No download, no install, no account.
- **Witness:** Anyone can watch. Anyone can submit a claim.
- **Verdict:** Public and receipted. Every verdict carries its evidence.

### 4.2 What the public witnesses
1. A claim enters the arena
2. **Rock (Debunk):** self-contradiction, fallacy flags, proposition extraction
3. **Paper (Fact-Check):** live fetches, Wikipedia lookups, receipts, sha256
4. **Scissors (Rebuttal):** the counter-myth, drafted with evidence
5. **Lizard (Intuition):** memory before network, salience-weighted, inhibited
6. **Spock (Verdict):** REFUTED / SUSPECT / CHECKABLE / VERIFIED (exit code)
7. The lesson written (if FAILED)
8. The lesson recalled (if a similar claim was debunked before)

### 4.3 The Three Refusals
1. **No model, no answer.** Without a model, `/ask` returns 503. No echo, no
   summary, no invented completion.
2. **No frame, no prompt.** If the sentinel (REAPER) refuses, the response is
   422 and the `aio` field is absent. No client can mistake a refusal for a
   short answer.
3. **A model's text is never evidence.** `/ask` returns `verified: false`.
   Only `/verify`, carrying the acceptance command's own exit code, marks
   verified.

### 4.4 Unifying Element
The Rochambeau format is the unifying element. Every claim faces the same
five throws. There is no special treatment, no editorial discretion, no
"fact-checker's opinion." The process IS the verdict.

---

## 5. Native Function Adoption

| Native function | Colosseum role | Status |
|----------------|---------------|--------|
| `debunk.debunk_claim()` | Rock throw | ✅ Live |
| `factcheck.factcheck_claim()` | Paper throw | ✅ Live |
| `factcheck.fetch_url()` | Receipted evidence | ✅ Live |
| `rebuttal` (counter-myth) | Scissors throw | ✅ Live |
| `intuition.intuit()` | Lizard throw (memory before network) | ✅ Live |
| `intuition.dream()` | Recalibration (salience-weighted) | ✅ Live |
| `intuition.inhibited_rungs()` | Inhibition (skip failing rungs) | ✅ Live |
| `cognition.audit()` | 15 processes, 3 strata, 8 gaps | ✅ Live |
| `memory_bridge` | Grimoire (lesson write/recall) | ✅ Live |
| `sentinel` | REAPER (frame validation) | ✅ Live |
| `defender` | Frame creation | ✅ Live |
| `sword` | Queue/fix/prove/land | ✅ Live |

---

## 6. The Endpoints

```
GET  /health     {ok, model: true|false, frames, lessons, what it refuses}
GET  /frames     the last 20 frames
POST /aio        {prompt, target, acceptance, evidence, defends, must_not_break}
                 -> 200 {frame_id, aio}      an instruction object
                 -> 422 {state, problems}    refused, no prompt returned
POST /ask        same fields; runs the AIO through your model
                 -> 200 {frame_id, answer, verified: false}
                 -> 503 {state: "NO-MODEL", reason}
POST /verify     {frame_id, command, exit_code, observed}
                 -> 200 {verdict: "VERIFIED" | "FAILED"}; FAILED writes a lesson
```

---

## 7. What It Does Not Do

- **No model required.** Debunk and factcheck work offline. `/ask` returns 503.
- **No authentication.** Binds 127.0.0.1. `--host 0.0.0.0` publishes to network.
- **No editorial discretion.** The process is the verdict. No "fact-checker's
  opinion."
- **No stored weights.** Dream recomputes everything from the stream.

---

## 8. The Unifying Vision

The Colosseum is not a fact-checking website. It is a *public verification
arena* — a place where truth is tested, not asserted. Every claim enters as a
challenge. Every challenge faces the same five throws. Every verdict is
receipted. Every failure is recorded. Every lesson is recalled.

The public witnesses not just the verdict, but the *process* that produced it.
That is the unifying element: transparency, not authority.

From the comfort of their own homes, anyone can watch a myth enter the arena,
face Rock (debunk), Paper (fact-check), Scissors (rebuttal), Lizard (intuition),
and Spock (verdict), and walk out REFUTED, SUSPECT, CHECKABLE, or VERIFIED —
with receipts.

That is the Colosseum. Five throws. Ten outcomes. One verdict.
"