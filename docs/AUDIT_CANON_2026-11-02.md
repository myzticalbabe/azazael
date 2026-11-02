# CANON AUDIT — the instruction layer (2026-11-02)

**Scope:** `SYSTEM_INSTRUCTIONS.md`, `SOP.md`, `MANDATES.md`, `ERROR_LOG.md`, `MEMORIES.md`,
`.agents/skills/` (204 dirs + 38 loose files), `docs/agent_orders/` (9 files).
**Read-only.** No canon file was edited.

**Method and its limit.** `code_search` scoped to `C:/Azazael/azazael` works — a query for the
three mandated agent names returned **87 matches** across the tree. The same tool scoped to the
home directory returns 0 with exit 2 (it chokes on dangling paths such as `.\ollama.exe`), so a
zero from *that* scope is meaningless and is not used here. I did not read `SYSTEM_INSTRUCTIONS.md`
or `SOP.md` end to end; findings attributed to them come from the `MANDATES.md` / `MEMORIES.md` /
`ERROR_LOG.md` mirrors plus the skills that quote them, and are marked as mirrors where relevant.

---

## 1. Headline

**Six of the eight agent types the canon mandates do not exist in this client, and the gate that
mandates them offers no state in which it can be honestly passed.**

This is not a new discovery. The tree recorded it itself — `ERROR_LOG.md:831` is
*"Error #74 — [CRITICAL PROCESS VIOLATION] 10-Phase Gemini Injection Protocol:
thinker-with-files-gemini Unavailable"* — and then left the mandate standing. A gate that cannot be
satisfied is not a control; it teaches the operator to skip it, which is the same outcome as having
no gate at all.

---

## 2. Unsatisfiable mandates — 6 of 8 agent types absent

The `azazael-pre-action-gate` skill is the enforcement point and is `auto_load: true`, so it is in
context for every turn.

| Agent mandated | Where | Available here? |
|---|---|---|
| `thinker-with-files-gemini` | `.agents/skills/azazael-pre-action-gate/SKILL.md:28,31,32`; `MANDATES.md:248-257` (6 of 10 phases); `MEMORIES.md:230,293` | **No** — `ERROR_LOG.md:860` "agent type does not exist in roster" |
| `thinker-gpt` | `.agents/skills/azazael-pre-action-gate/SKILL.md:37,38`; `azazael-inference-protocol/SKILL.md:37-41` | **No** — `ERROR_LOG.md:861` "ChatGPT OAuth not connected" |
| `code-reviewer-deepseek` | `azazael-pre-action-gate/SKILL.md:35,37`; `azazael-sentinel-gate/SKILL.md:48,52`; `MEMORIES.md:249,258` | **No** |
| `code-reviewer-deepseek-flash` | `azazael-agent-utilization/SKILL.md:22,38` | **No** |
| `researcher-web` | `azazael-agent-utilization/SKILL.md:23` | **No** |
| `researcher-docs` | `azazael-agent-utilization/SKILL.md:23` | **No** |
| `basher` (diagnostic runner) | `azazael-agent-utilization/SKILL.md:22`; `MEMORIES.md:249,257` | Partly — `run_terminal_command` is the equivalent, and the skill does not say so |
| `file-picker`, `code-searcher` | `azazael-agent-utilization/SKILL.md:23` | Yes — `code-searcher` exists by name |

Absence above is established **for the client this audit ran in**, plus the independent roster
record in `ERROR_LOG.md:847` for "the Codebuff agent roster for this deployment". I cannot see the
Kilo or opencode rosters; if those lanes have the agents, the mandate is satisfiable there and this
finding is lane-scoped — but `ERROR_LOG #74` was written by a Codebuff session, so the defect is
live in at least one lane.

**Aggravating detail:** `RULE 0Z-A` provides a fallback — query all free models via `providers.py`
(`azazael-inference-protocol/SKILL.md:37-69`, `MANDATES.md:217-226` column "Query ALL inference
models"). The fallback is procedurally sound and needs no absent agent. But the pre-action gate's
answer set never names it: the gate asks *"Was thinker-gpt + basher + code-reviewer-deepseek spawned
for THIS task?"* and accepts only `[Yes / No - CRITICAL violation]`
(`azazael-pre-action-gate/SKILL.md:37`). **There is no third answer.** An honest agent must choose
between a false `Yes` and a self-declared CRITICAL violation.

---

## 3. The answer-set defect — why "HALT and spawn" is an infinite loop

`azazael-pre-action-gate/SKILL.md:28` instructs: *"If none: HALT and spawn"*. When the agent does
not exist, HALT-and-spawn cannot terminate. The skill is marked *"PERMANENTLY ACTIVE. CANNOT BE
DISABLED"* (`:8-9`) and `:46` makes executing an edit without it a 🔴 CRITICAL violation.

So the gate's only satisfiable outcome is to violate it, or to write `N/A` — an answer the
format does not offer, and which its own enforcement table scores as a violation. Two consequences
worth naming:

1. **RULE 0Q-A compounds it** — the gate demands citation of inference-cache filepaths
   (*"e.g. .inference_cache/20260611_120000_gemini.log"*, `:34`). If Gemini never ran, that artifact
   cannot exist; the citation requirement is unsatisfiable by construction.
2. **The fallback is invisible to the gate.** An agent that correctly executed the RULE 0Z-A
   fallback (queried `providers.py`) has *complied with the mandate's stated intent* and still must
   answer `No`.

---

## 4. Precedence — one real conflict, one already-repaired precedent

The chain declared at the top of `AGENTS.md` is `SYSTEM_INSTRUCTIONS > SOP > ERROR_LOG > MEMORIES >
SESSION_STARTUP > LESSONS_MASTER > CODEBASE_AUDIT_TODO`.

**The conflict.** `docs/agent_orders/00_session_order.md:12-15` states *"this is the precedence —
nothing else claims to go 'first'"* and *"Steps 0–2 are unconditional"* — i.e. the gate, memory load
and verdict always run. `RULE 0B` (mirrored in `AGENTS.md`) says the user's instruction is the sole
source of truth and *"Nothing competes: not my judgement, not a general rule (**including this
one**), not precedent"*. When a user says "do X now", 0B says obey, and the session order says run
the gate first. Both are canon; they cannot both be obeyed literally.

**The precedent that already solved this shape.** `00_session_order.md:13-14` reads: *"Where any
other document says 'first', it means 'first within its own step'."* That single line neutralised
every competing "first" claim in the corpus **without deleting any canon**. It is the pattern the
unsatisfiable-mandate repair should copy.

**Does any document claim authority over the user?** No — no canon document claims to outrank the
user; `RULE 0B` explicitly subordinates itself. The defect is the *reverse*: an unconditional
procedural chain that does not say how it yields to a direct instruction.

---

## 5. Host-absolute paths and the username in canon — a publish leak by generation

This matters because canon is **generated into every lane's instruction file**.

| Location | Literal |
|---|---|
| `docs/agent_orders/00_session_order.md:9` | `python C:/Azazael/azazael/tools/mcp_startup_gate.py --fix` |
| `docs/agent_orders/00_session_order.md:10` | `python C:/Azazael/azazael/tools/session_start.py "<task>"` |
| `docs/agent_orders/03_lane_queue.md:15-16` | teaches `C:/Users/clint/_board.py` to every lane |

`docs/agent_orders/*` are the **source** blocks that `tools/agent_orders_sync.py` writes into
`~/AGENTS.md`, `~/.config/kilo/AGENTS.md`, `~/.claude/CLAUDE.md` and ~30 others — the MCP gate
reports **34 targets in sync**. So one hard-coded home path here is replicated 34 times, and the
same generator is what would ship this canon publicly. Sanitising the published projects while
leaving this source untouched leaves the leak in the generator.

---

## 6. Rules enforced only by prose

| Rule | Enforcement | Verdict |
|---|---|---|
| RULE 0J — pre-action gate banner | The agent prints it; nothing reads it | prose-only |
| RULE 0Z — spawn thinker-gpt + basher + reviewer per sub-task | no validator | prose-only |
| RULE 0W — minimum agents per task type (`agent-utilization/SKILL.md:22-23`) | no validator | prose-only |
| RULE 0M — concurrent inference spawns | no validator | prose-only |
| RULE 0B-C — negative controls for oracles | **implemented** — ~20 tools carry executable controls (`tools/boundary_policy.py:135`, `tools/metthew_families.py:253`, `tools/mcp_eight_verify.py:641`) | real control |

RULE 0B-C is the counter-example that proves the corpus *can* enforce rather than instruct, which
makes the prose-only set a choice rather than a limitation. Note also `tools/receipt_guard.py` now
exists as an unwired G2 receipt check and `tools/claim_guard.py` was previously described as
existing-and-working while *"NOTHING EVER RAN IT"* for months (`tools/../.githooks`
`prepare-commit-msg:5-8` per the tools audit) — a tool in `tools/` is not a control until something
calls it.

---

## 7. Two gates, unclear which governs

`.agents/skills/pre-action-gate-lite.md:15` opens *"The heavy version lives in the Azazael compliance
stack; this is the lite gate"* and proceeds to define Gates 1–3 as **verify-before-done** — a
different subject from the 13-check assertion. `:34-36` then routes agent spawns explicitly back to
the permanent gate's RULE 0I/0W/0Z, with no lite alternative. So a reader who finds the lite gate
first has no way to learn that the 13-check banner is still mandatory for file edits. Two documents,
same name-stem, different obligations, no cross-reference in the lite file to the 13 checks
themselves.

---

## 8. Remediation, ordered

1. **Give the gate an honest third answer.** Add `N/A — AGENT ABSENT (fallback: queried providers.py)`
   to the RULE 0Z / 0Z-A / 0V / 0G / 0M checks in
   `.agents/skills/azazael-pre-action-gate/SKILL.md:28-38` and the mirror at
   `azazael-sentinel-gate/SKILL.md:37-53`. This is the single change that makes the gate passable
   without a lie, and it makes the existing RULE 0Z-A fallback load-bearing instead of decorative.
2. **Scope the mandate by roster, not by intent.** `MANDATES.md:217-226` lists the 10 phases as
   unconditional. Add the roster precondition the same way `00_session_order.md:13-14` added the
   "within its own step" qualifier — amend the table, do not delete the phases.
3. **Resolve the 0B/session-order conflict in one line**, in `00_session_order.md`: state that a
   direct user instruction outranks steps 0–2, and that running them anyway requires saying so in
   the first response. Today the canon answers this by silence.
4. **Sanitise `docs/agent_orders/*` before publish, not just the projects.** These are the 34-target
   generator sources; the projects are downstream of them.
5. **Wire one prose-only rule to a validator** — RULE 0J is the natural first: a pre-commit step that
   greps the commit body for the banner costs a few lines and turns the most-violated rule into a
   checked one.
6. **Make `pre-action-gate-lite.md` name the 13-check gate** at `:15` so the two cannot be mistaken.

---

## 9. Not verified

- `SYSTEM_INSTRUCTIONS.md` and `SOP.md` unread in full — findings cite the `MANDATES.md` /
  `MEMORIES.md` / `ERROR_LOG.md` mirrors and the quoting skills. Line references to those two files
  are therefore absent rather than zero.
- Kilo and opencode agent rosters not observable from here.
- The 87-match `code_search` output was truncated at the tool limit; the count is a floor, not a
  total.
- No canon was edited and nothing was executed.

*Prepared 2026-11-02 as auditor 16 of an 18-way full audit.*
