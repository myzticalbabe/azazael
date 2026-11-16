# THE COLOSSEUM — Live Public Myth-Debunking & Fact-Checking

**A unifying public event from the comfort of your own home.**
**Native function adoption: Eve Unleashed's debunk, factcheck, and cognitive strata.**

---

## 1. What It Is

The Colosseum is a live, public event where myths are debunked and claims are
fact-checked in real time, witnessed by anyone from their own home. It is not a
show or a performance — it is a *verification arena*. Every claim enters as a
challenge. Every challenge is tested against evidence. Every verdict is receipted.

The name is deliberate: the Roman Colosseum was where the public witnessed
trials of strength. This Colosseum is where the public witnesses trials of
*truth*.

## 2. The Format: Rochambeau

Rochambeau (rock-paper-scissors) is the unifying game mechanic. Each claim
passes through three sequential gates, each gate a "throw":

| Throw | Gate | What it tests | Eve native function |
|-------|------|---------------|---------------------|
| **Rock** | Debunk | Does the claim contradict itself? Are there fallacy shapes? Is it checkable? | `eve debunk --claim "..."` |
| **Paper** | Fact-Check | Does the evidence support or refute it? Every byte receipted. | `eve factcheck --claim "..."` |
| **Scissors** | Verdict | Final ruling: REFUTED / SUSPECT / CHECKABLE / VERIFIED | `eve verify` (exit code) |

A claim must survive all three throws to be VERIFIED. If it fails at any gate,
it is REFUTED or SUSPECT, and the failure is recorded as a lesson in the
Grimoire (memory_bridge).

## 3. The Three Refusals (already in the code)

These exist because their absence produced a wrong answer once:

1. **No model, no answer.** Without a model configured, `/ask` returns 503.
   The Colosseum does not echo, summarize, or invent. It refuses.
2. **No frame, no prompt.** If the sentinel (REAPER) refuses the frame, the
   response is 422 and the prompt is *absent*. A client cannot mistake a
   refusal for a short answer.
3. **A model's text is never evidence.** `/ask` returns `verified: false`.
   Only `/verify`, carrying the acceptance command's own exit code, can mark
   a frame verified.

## 4. The Four Parts (native adoption)

| Part | Role | Native function | Where it lives |
|------|------|-----------------|----------------|
| **FLAMING SWORD** | The codebase — find, queue, fix, prove, land | `Project_FLAMING_SWORD/tools/sword.py` | `sword --run` |
| **Defender** | The user's intent — a prompt becomes a frame | `Project_FLAMING_SWORD/tools/defender.py` | `defender --frame` |
| **REAPER (sentinel)** | The frame's claims — every path stat'ed, every act from a closed vocabulary | `Project_FLAMING_SWORD/tools/sentinel.py` | `sentinel --check` |
| **GRIMOIRE (memory)** | What was learned — one line per failure, written at the moment it failed | `Project_FLAMING_SWORD/tools/memory_bridge.py` | `memory_bridge --recall` |

CRADLE launches them in order. The Colosseum is the public face of CRADLE.

## 5. Native Function Adoption

The Colosseum adopts Eve Unleashed's native functions directly:

### 5.1 Debunk (Rock)
- **Input:** A claim (text)
- **Process:** Separate checkable propositions from opinion language. Flag
  known fallacy shapes. Test self-contradiction mechanically.
- **Output:** VERDICT (REFUTED / SUSPECT / CHECKABLE) + propositions + opinions + flags
- **No network, no model, no key.** The claim is taken apart with its own words.
- **Native:** `eve debunk --claim "..."` → `cmd_debunk()` in `eve_unleashed/cli.py`

### 5.2 Fact-Check (Paper)
- **Input:** A claim + optional grievance
- **Process:** Debunk locally, corroborate live (entity existence on Wikipedia),
  cross-check against filed grievances. Every response is a receipt: URL,
  timestamp, byte count, sha256.
- **Output:** DEBUNK verdict + entity lookups + receipts + locked evidence IDs
- **Live, timeout-bounded, receipted.** A verdict without a receipt is a rumor
  with formatting.
- **Native:** `eve factcheck --claim "..."` → `cmd_factcheck()` in `eve_unleashed/cli.py`

### 5.3 Rebuttal (Scissors)
- **Input:** A claim + target + evidence
- **Process:** Fact-check then draft the correction. The rebuttal is the
  counter-myth: the same shape as the original claim, but with evidence.
- **Native:** `eve rebuttal` (counter-myth: factcheck then draft correction)

### 5.4 Cognitive Strata (the mind behind the arena)
- **Conscious:** deliberate-search, fetch-ladder, verification, goal-setting, self-model
- **Subconscious:** intuition, host-prior, inference-cache, habituation, attention
- **Unconscious:** reflex, immune-memory, dream-replay, soma, watchdog
- **Gaps (named, not hidden):** consolidation, incubation, priming,
  prospective-memory, inhibition, counterfactual-replay, salience, affect

The Colosseum's mind is the Berzerker A-I-O: 15 named processes across 3
strata, with 8 named gaps. The gaps are the roadmap.

### 5.5 Intuition (supralogical rung)
- Answers from memory before the network. Per-host answer rates. Salience
  weighting (blocked outcomes carry 2x weight). Inhibition (rungs that keep
  failing are skipped).
- **Native:** `intuition.intuit(url)` → guess or blocked, with confidence

### 5.6 Dream (recalibration)
- Pairs intuition guesses with fetch outcomes. Recomputes hit-rate per rung.
  Salience-weighted (blocked > ok). No stored weights to go stale.
- **Native:** `intuition.dream(log_path)` → pairs, hits, hit_rate, by_rung, hosts

## 6. The Endpoints (public interface)

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

## 7. The Public Event

### 7.1 Format
- **Duration:** Continuous (always on, like a public square)
- **Access:** Browser-based. No download, no install, no account.
- **Witness:** Anyone can watch. Anyone can submit a claim.
- **Verdict:** Public and receipted. Every verdict carries its evidence.

### 7.2 The Three Refusals (what the public sees)
1. A claim with no evidence → REFUTED (self-contradiction or fallacy)
2. A claim with evidence but no corroboration → SUSPECT (needs more)
3. A claim that passes all gates → CHECKABLE (ready for verification)

### 7.3 What the public witnesses
- The claim entering the arena
- Rock: the debunk (self-contradiction, fallacy flags, proposition extraction)
- Paper: the fact-check (live fetches, Wikipedia lookups, receipts)
- Scissors: the verdict (REFUTED / SUSPECT / CHECKABLE / VERIFIED)
- The lesson written (if FAILED)
- The lesson recalled (if a similar claim was debunked before)

### 7.4 Unifying element
The Rochambeau format is the unifying element. Every claim faces the same
three throws. There is no special treatment, no editorial discretion, no
"fact-checker's opinion." The process IS the verdict.

## 8. Native Function Adoption Summary

| Native function | Adopted into Colosseum as | Status |
|----------------|--------------------------|--------|
| `debunk.debunk_claim()` | Rock throw | ✅ Live |
| `factcheck.factcheck_claim()` | Paper throw | ✅ Live |
| `factcheck.fetch_url()` | Receipted evidence | ✅ Live |
| `rebuttal` (counter-myth) | Scissors throw | ✅ Live |
| `intuition.intuit()` | Supralogical rung (memory before network) | ✅ Live |
| `intuition.dream()` | Recalibration (salience-weighted) | ✅ Live |
| `intuition.inhibited_rungs()` | Inhibition (skip failing rungs) | ✅ Live (b1ecf692) |
| `cognition.audit()` | 15 processes, 3 strata, 8 gaps named | ✅ Live |
| `memory_bridge` | Grimoire (lesson write/recall) | ✅ Live |
| `sentinel` | REAPER (frame validation) | ✅ Live |
| `defender` | Frame creation | ✅ Live |
| `sword` | Queue/fix/prove/land | ✅ Live |

## 9. What It Does Not Do

- **No model required.** The Colosseum works without a model. `/ask` returns
  503 without one, but debunk and factcheck work offline.
- **No authentication.** Binds 127.0.0.1. `--host 0.0.0.0` publishes to
  your network.
- **No editorial discretion.** The process is the verdict. There is no
  "fact-checker's opinion" — only evidence and receipts.
- **No stored weights.** Dream recomputes everything from the stream. Nothing
  goes stale.

## 10. The Unifying Vision

The Colosseum is not a fact-checking website. It is a *public verification
arena* — a place where truth is tested, not asserted. Every claim enters as a
challenge. Every challenge faces the same three throws. Every verdict is
receipted. Every failure is recorded. Every lesson is recalled.

The public witnesses not just the verdict, but the *process* that produced it.
That is the unifying element: transparency, not authority.

From the comfort of their own homes, anyone can watch a myth enter the arena,
face Rock (debunk), Paper (fact-check), and Scissors (verdict), and walk out
REFUTED, SUSPECT, CHECKABLE, or VERIFIED — with receipts.

That is the Colosseum.
"