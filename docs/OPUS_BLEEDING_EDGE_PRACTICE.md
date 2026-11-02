# THE OPUS — bleeding-edge practice, learned at the cost of the thing it was learned on

**For whom.** Whoever inherits this tree and is about to be confident.

**Method.** Every claim below is attached to an incident: a file, a number, a date, or a
command that can be run to check it. Nothing here is here because it sounds wise. Where a
figure was secondhand it says so, and where a figure was wrong it says *what it was wrong
about* — because a treatise that only remembers its correct claims teaches nothing about
how the wrong ones got in.

**Provenance convention.** A claim tagged *(measured)* was re-derived while writing this
document — the command and its output are in Appendix C. **Everything untagged is
*canon-recorded***: quoted from `AGENTS.md`, `MANDATES.md` or a source's own printed output,
and *not* re-derived here. That distinction is not legalism. Two of the canon-recorded
claims checked for this pass turned out to be **wrong in their identifiers while right in
their substance** (§I), which is exactly the class of error a convention like this one exists
to make visible.

**The standing warning.** These are not principles. Principles are what you write before
you know. These are **receipts**: the residue of doing it wrong, in production, for long
enough that the error could be measured. A receipt read as a principle becomes liturgy, and
liturgy is the failure mode this document exists to prevent — see §XII.

---

## I. The instrument is the first thing to suspect, not the system

**Rule.** Before acting on an oracle's verdict, name the exact predicate it evaluated and
ask whether that predicate is the thing you care about. An oracle that fires is making a
claim about a *condition*, not about the world.

**What it cost.** In one session, five separate false claims all had this single shape:

- *(measured)* `scripts/chain_controller.py:161` declares
  `_SKIP_RC: dict[str, tuple[int, ...]] = {"train": (1,), "tensor": (3,), …}` under a comment
  reading *"Honest-skip exit codes per job: a by-design skip is ok."* A nonzero return code on
  `train` is a **designed skip**, reported as `ok=true`. It was reported as a bug.
  **And the canon copy of this very fact is corrupted:** `AGENTS.md` §0B-B records it as
  `_KIP_RC` at `chain_controller.py:107`. The name is `_SKIP_RC`, the line is 161, and only
  opening the file catches it. The substance survived; the citation did not — which is the
  difference between a fact and a reference to one.
- One timestamp on one process was generalised into "PID 6192 is wedged". It was not.
- An instrument that dropped a leading zero produced "**39 of 39 rules have NO
  validator**". The real figure was not 39.
- Four CRITICAL findings came from probes that were **prose strings sitting in the
  validators' N/A branches** — the instrument was reading its own documentation as if it
  were a test.
- `gate_timing` counted a **docstring** as the integration it was supposedly measuring.

None of these raised an exception. Each one produced a confident number.

**Site evidence, measured.** The same class of error in a scoring oracle: with a `0.62`
recall floor in place (2026-10-30), a random nonce scored **0.644** and passed, and in the
same era **one nonce in fifteen scored 0.836** while noise averaged `0.645` and real
queries bottomed out at `0.949`. A threshold-shaped assertion therefore false-fails a
healthy stack. The repair was not a better threshold; it was a **differential** — the same
noise query asked of the daemon and of the proxy, where the proxy must return strictly
fewer rows. See `tools/pmb_floor_proxy.py`.

**What enforces it now.** MANDATES 0B-B (verify the predicate) and 0B-C (every oracle ships
a **negative control**: a known-healthy fixture it must not fire on). An oracle whose
control fails is **UNVALIDATED** — its findings may be reported, and are barred from
licensing a destructive remedy.

**The tell.** You are about to delete capability because a number said so, and you cannot
state the condition that produced the number in one sentence.

---

## II. A control is not installed until it has been exercised *here*, and measured twice

**Rule.** "In place" is not a state a file can be in. A control exists when it has been
run, its output explained, and its failure mode observed at least once. All four
conditions, or the honest label is *unknown*.

**Site evidence, fresh (2026-11-02).** A requester asked whether a local model could drive
the agent harness. The configuration answered *yes* — three OpenAI-compatible providers
declared, five models listed, `tool_call: true` on every one. The configuration was data.
The probes said:

| probe | result |
|---|---|
| `127.0.0.1:8087/v1/models` | connection refused |
| `127.0.0.1:11435/v1/models` | connection refused |
| ollama `:11434` | up, 4 models |
| models declared in config but absent from the store | **4 of 5** (`qwopus-9b`, `ornith-9b`, `qwythos-9b`, `qwythos-9b-lenient`) |
| `eve-v2u:latest` + chat | `HTTP 400 · "does not support chat"` |
| `olmoe-1b-7b` + tools | `HTTP 400 · "does not support tools"` |

A config naming a model is not the model being installed; `tool_call: true` is a claim, not
a capability. **The right answer to "can this be accomplished?" was yes — and the answer to
"does it work?" was no, on two independent axes, discoverable in four HTTP calls.**

**Site evidence, older, same shape.** "A lane config is data, not proof: the gate checks
behaviour first" (`AGENTS.md`). Six floor proxies were double-bound on `:8766` while every
config on disk said one.

**Site evidence, and the reason this chapter exists.** The platform matrix carried
"Model 2: ~62 MB total memory, secondhand" — a plausible figure, correctly flagged as
secondhand, and therefore *trusted* for weeks. It was a **category error**: it counted ROM
boards and undecoded address space as RAM. The driver decodes **1 MiB work + 4 MiB texture
+ 128 KiB buffer**. The number was withdrawn on 2026-11-02 and kept in
`docs/shardex_platforms.json` under `withdrawn`, because deleting it quietly would destroy
the evidence that plausible numbers get in.

**What enforces it now.** MANDATES 0B-D: EXERCISED, MEASURED (a number *derived and
explained* — "it returned 0" is a reading, a diagnosis needs its own evidence), HONEST
STATE, NO INHERITED TRUST. The test is one question: *when did I last run X, what did it
print, and what does that output establish?*

---

## III. Timestamps are not liveness; a child outlives the file that defines it

**Rule.** A long-running process is not running *your* code. Compare the child's start time
to the mtime of the script it was started from, every session, before trusting any answer
it gives.

**What it cost (2026-10-30).** Supervisor children had run since **10:34**. The script that
defines them, `supervisor_mcp.py`, was edited at **13:19**. For hours the supervisor
answered queries with rows scoring **0.28** — nonsense, returned confidently, with no
exception anywhere. The stack was green. The answers were wrong.

**The related trap.** `pams` and `supervisor` are the *client's* stdio children. Killing
one to "refresh" it breaks the live session; there is no refresh that is not a restart.
Measured consequence: a stale stdio child serving old code is a `[BLOCKED]` state whose only
remedy is a client restart, and it must be said plainly in the first response rather than
papered over with a repair attempt.

**What enforces it now.** `supervisor-fresh` and `pams-running` in
`tools/mcp_startup_gate.py`: child start time vs script mtime. Not a promise in a doc — a
comparison of two filesystem timestamps, run before the first substantive action.

**The tell.** You are quoting an answer from a service whose source you know changed since
the service started.

---

## IV. Cold start is a deadline, not a bootstrap detail

**Rule.** Startup order is a *latency contract with a third party you do not control*, and
the deadline is the shortest one in the chain — usually not yours.

**Measured (2026-10-31).** opencode's remote MCP client gives an unreachable endpoint
**three attempts in 1.65 s**: 0.39 s, 0.65 s, 1.65 s. Then it marks the server failed **for
the whole session**. Meanwhile `pams` was spawned at the same millisecond and reached its
floor-proxy spawn site at roughly **2.5 s**. Daemon up at 2.5 s, `:8766` at 3.0 s, client
already decided. Every cold start lost the race, and **the gate was green throughout**,
because the gate started checking after the loss.

Two rules follow, both enforced rather than documented:

1. **`:8766` must exist before the client.** `Startup\pmb-floor-proxy.vbs` starts it hidden
   at logon with `PMB_FLOOR_ORIGIN=logon`. pams still spawns its own when the port is free,
   and declares `origin=pams` — which is a `floor-origin` **FAIL**, because a proxy started
   by a session dies at the next reboot and takes the session with it.
2. **The proxy waits for its own upstream.** A request during a cold start waits up to
   `PMB_UPSTREAM_WAIT` (default 30 s) instead of returning 502. A 502 during a cold start is
   indistinguishable, to the client, from a dead stack.

**Generalisation that transfers.** Any retry budget you did not write is a deadline you
must discover by stopping the clock on your own service and watching. A 3-attempt/1.65 s
client and a 2.5 s dependency is not "a bit slow" — it is a permanent failure that looks
like a healthy system.

---

## V. Shared resources fail kindly: the double-bind and the double-claim

**Rule.** Anything two processes can take without an error is not protected. You do not have
a lock because a config says one holder; you have a lock when a second holder is *refused*.

**Evidence 1 — the port.** **Six** proxies were double-bound on `:8766` because Windows
`SO_REUSEADDR` lets a second instance bind a live port **with no error**. No exception, no
log line, six silent writers. The gate's answer is `proxy-singleton`: exactly one
*instance*, counting the re-exec'd interpreter correctly (one healthy instance is two
processes).

**Evidence 2 — the queue.** The board carried **743 open rows**, the oldest **nine days**
old, with `mcp_config_fix` posted **75 times**, because `status` lived inside each row's
JSON — so a poller re-read its entire backlog every pass, and nothing recorded that any row
had ever been *picked up*. A "batch loop" built on that board gets **slower** every
iteration. The repair was `claim`/`done`/`block`: compare-and-set inside `BEGIN IMMEDIATE`,
oldest first, a 30-minute lease (`CLAIM_LEASE_SECONDS`) so a dead lane cannot strand work,
and retirement so retired rows leave the query.

**The footgun the repair introduced, recorded rather than hidden.** `release` *deletes* the
claim row — which also erases `attempts`. A row claimed and released four times still reads
`attempts=1`, and the release leaves no record. Measured the same day: roughly twenty rows
were released as surplus and returned to `available`, which is why `stats` read 5 and then
27 within the hour. **A fix that makes a queue healthy can destroy the forensic trail of how
often it was unhealthy.**

**Evidence 3 — the module with a smoke test for a main.** `src/CORE/LaneMessageBoard.py`
has a `main()` that posts a kilo task, a freebuff task and an announcement **on every run**.
It was run **72 times**: 75 rows of `task_id=1039`, 78 of `mcp-001`, 72 announcements — and
`#1039` is marked SUPERSEDED / never execute as written. The rule is now in canon: use the
CLI, never the module's `__main__`.

**Evidence 4 — the store that was not the store.** The Kali lane's
`/root/.azazael/telemetry_store.db` was a **real 32 KB file with 0 rows** instead of the
symlink canon described. Every post from that lane went into a void, and `stats` printed
`{'open': 0}` — which reads as *"no work"*, not as *"wrong file"*. Two lanes on two stores is
the one failure mode that makes every other part of the protocol silently useless. Repair is
one line (`ln -sf ...`), verified by writing a row on one side and reading it on the other.

**The tell.** A "quiet" queue, a "clean" log, or a single-holder invariant you have never
tried to violate.

---

## VI. Thresholds are properties of the corpus, and the corpus moves

**Rule.** A magic number belongs to a dataset at a moment. Write the *measurement* next to
the number, and re-measure when the data changes — especially after a purge.

**Site evidence.** `PMB_RECALL_MIN_BEST=0.89` and `PMB_RECALL_FLOOR=0.70` in
`pmb_floor_proxy.py` and `supervisor_mcp.py`. Measured 2026-10-30 on this corpus after
contaminated records were purged: **noise best 0.836 max / 0.645 mean, real best 0.949
min** — a **0.113 gap**, and the thresholds sit inside it. The canon carries its own expiry:
*"Re-measure after a large purge; the numbers move with the corpus."*

**Why this is a best practice and not a footnote.** The earlier thresholds (0.62) were not
*wrong* when written. They were correct for a corpus that then changed. A threshold without
its measurement lineage is a decision nobody can audit and nobody will revisit.

---

## VII. Cost is a correctness property: context, disk, and wall clock

**Rule.** Budget the three resources that fail silently. A system that is correct and
unaffordable is a system that gets bypassed, and a bypassed gate is worse than no gate
because it is believed.

**Context (measured).** **1,042** package skills were archived on 2026-10-30
(`skills.pkg-archive/`) because their *descriptions alone* cost **~34.7k tokens on every
request**. Nothing was wrong with them individually. The catalogue was the bug. *(measured:
`find skills.pkg-archive -name SKILL.md | wc -l` → **1042**; the directory list alone shows
only `load/` and `source/`, so a shallow `ls` reads this archive as two items.)*

**Wall clock (measured).** **5,380 tests exist and nothing gates them.** Before concluding
"the suite is slow", check that it is not *stuck*: two tests wedged an entire run for
months because the compliance gate under test read a **5.4 GB** store on every `check_all()`.
After the fix: **0.09 s**, measured. The lesson is not "write faster tests" — it is *an
unbounded read inside a gate converts a fast suite into an infinite one, and the report
looks like "tests are slow" forever*.

**Interpreter (measured).** The production interpreter is **3.15t free-threaded**
(`C:/Azazael/.venvs/py315t/Scripts/python.exe`, `sys._is_gil_enabled()` is False). `python`
on PATH is 3.14.7 **with** the GIL. A "hang" measured under 3.14 is not evidence about
production. Two years can be spent diagnosing an interpreter you do not ship.

**Disk (measured).** This disk runs at **98%**. The memory backup path
(`tools/memory_backup.py`) copies through SQLite's **online backup API** and **refuses** a
copy that fails `integrity_check` — and excludes the 5.4 GB DirectMemory store unless
`--include-large`, because a backup that fills the disk is a data-loss event wearing a
safety label.

---

## VIII. Write the refusal into the control, or the control is decoration

**Rule.** A check that cannot say *no* is a logger. Design the refusal first, name the exact
condition that produces it, and make refusal the default when the condition is unknown.

**Site evidence — four primitives, each bought by a failure** (the mesh resilience work of
2026-09-16): **fencing tokens** (a stale writer must be *rejected*, not merely detected),
the **silent-failure ledger** (failures that raise nothing must still increment something),
**liveness obligations** (a component must prove it is alive on a schedule, not merely have
been started), and **store tombstones** (a deleted or moved store must leave a marker, or
the next reader invents the empty file — see §V, Kali). The audit's decisive finding was
that these were needed on **write paths, not just merge paths**.

**Site evidence — a task is a program.** Running `tools/task_shape_check.py --check` against
a task text written by the agent produced **six real defects in the agent's own work**: two
controls that named no refusal, two acceptance criteria with no command behind them, one
unknown shape marker, and one piece of evidence that read "not written yet". All six were
fixed in the change rather than overridden. **An acceptance criterion without a command is a
no-op that reads as done.**

**Site evidence — the gate that must not be silent.** `.githooks/pre-push` **refreshes** the
injected canon block and then **aborts the push** if it had to change anything: injecting
during a push would ship an uncommitted file that no reviewer saw. It also has a declared
bypass (`BIBLE_PUSH_BYPASS=1 git push ...`), because an undeclared bypass is just a bug with
better PR.

**And the language half.** "This passes / is good enough / is done" are **acceptance claims**.
Only the user accepts. Describe, never accept. This is not politeness — acceptance language
is how a system's owner loses the ability to disagree with it.

---

## IX. The agent is inside the blast radius

**Rule.** Every gate you write for the codebase must be run against the agent's own output,
in the same session, or it is a gate for other people.

**Site evidence, this session, unfiltered.** The commit pipeline ran 25 checks and among
them `[AP5]`, which scans persisted assistant prose. It found **2 violations in the agent's
own messages**: `[want_me_to]` — *"Want me to mint the two scope/re-derivation gates, or
call it and move to shipping?"* and *"Step 1 is small… Want me to mint it for Kilo"*. The
gate's own printed reasoning is the important part:

> Mandated actions are NOT requests (`SYSTEM_INSTRUCTIONS.md:2046`). This gate runs AFTER
> emission: it cannot prevent a violation, only make it visible. Prevention is not
> available — no assistant-output hook exists in the plugin API.

Three things follow, and they are the model for every "we will catch it later" control:

1. **A post-hoc gate is honest about being post-hoc.** It says so in its output. A gate that
   implies prevention it does not have is worse than none.
2. **The repair is not the phrasing.** Deleting "Want me to" from a sentence does not fix a
   mandated action that was left pending; it hides it. Fixing the pending action is the fix.
3. **Visibility is a real deliverable.** Where prevention is architecturally unavailable,
   *measured* visibility — with the file and line that forbids it — is the correct bar.

---

## X. Provenance: cite the artefact, not the narration

**Rule.** A claim is worth the document it can be re-derived from. Generated text must be
generated *from a source that can be checked*, and drift between copy and source must fail a
gate rather than be discovered by a human later.

**Site evidence — generated canon.** The instruction blocks in every lane's `AGENTS.md` are
generated by `tools/agent_orders_sync.py` from `docs/agent_orders/*.md`, and the
**`orders-in-sync`** check fails when any generated block is not byte-identical to its
source. The ordering rule itself lives in one file (step 0 GATE → 1 MEMORY → 2 VERDICT →
3 SKILLS **on trigger**), and every other document that says "first" is defined to mean
"first within its own step". **One source, many copies, a gate that compares bytes.**

**Site evidence — a domain is a declaration, not a fork.** `tools/domain_trees.py` holds
`DOMAINS`; a new domain is an entry, and the renderer draws it through a descriptor with
**no code change** — verified 2026-10-31: **300/300 frames, 0 misses**. The stated rule is
the useful part: *"if you find yourself editing the renderer to draw a domain, you have
taken the wrong route."* A generalisation that requires touching the general machinery is
not a generalisation.

**Site evidence — read the artefact, not the code that made it.** Three defects survived
source review and died only in the rendered output: a scanline pass compositing black
through a ~255 mask; a dead middle 40% of a figure; a figure printing `—` instead of its
number. The house rule followed: **a readout must not hide its number when the reading is
bad** — `27/77 dead stores` beats a dash, because a dash is indistinguishable from "no
problem" and from "not measured".

**Site evidence — two sources, never blended.** The platform matrix now takes arcade clocks
from **MAME driver declarations** and polygon rates from prose (Wikipedia/Horowitz), and
says which is which, because MAME is *stronger than a wiki for clocks* (a driver that is 2×
wrong does not run the game at the right speed) and *weaker for marketing* (no driver
declares a polygon rate). The failure to avoid is a single table cell that silently mixes
the two and inherits the weaker one's authority.

**Site evidence — the process narrative is not the process.** The frame-index rule in
`C:\Users\clint\YGGDRASIL_RENDER_PLAYBOOK_2026-10-30.md`: index frames **from the URL, never
from the clock**, one browser profile per frame, absolute output paths, never edit a running
script; then verify **frame count + three distinct hashes + decoded frames**. "It rendered"
is a feeling; three distinct hashes are a fact.

---

## XI. Memory must be able to say no, and must be able to say "I don't know" differently

**Rule.** A store that only accretes becomes noise, and a retrieval loop nobody closes
becomes theatre. Both failure modes look identical from the outside: confident output.

**The abstraction ladder (META-LEVELS-CANON, user-decreed 2026-10-27).** L0 **instance** (a
trajectory; no generality claimed) → L1 **sweet spot** (exactly once removed: falsifiable,
evidence-linked, ≥3 trajectories, non-duplicate, bounded — would change a **class** of
decisions) → L2 **scope** (the only legitimate second step: the applicability boundary) →
**L3+ HEAVEN EXCLUDED**. Heaven is the rule that is *true everywhere and decides nowhere* —
"always verify ownership". It passes plausibility and fails materiality.

Enforced mechanically, not morally: **ledger cap 200**, prune **by retrieval count, never by
age**. Heaven-rules match everything, discriminate nothing, are retrieved never, and die of
disuse. Two tests kill them early — the **class test** (name the decision-class and three
trajectories, or drop it) and the **diary test** (senseless without its incident = L0 diary;
sensible in *every* incident = Heaven).

**The honest-empty distinction.** `cradle.py --grimoire` separates three states that used to
look identical: *no book yet* (nothing has failed here — fine), *an empty book* (**a writer
that never wrote — a finding**), and *an unreadable line* (exit 1, named by line, never
skipped). Most memory bugs live in the first two being merged.

**And the mirror-image error, which is subtler.** `prepare()` returning **0 lessons means the
message matched nothing — not a dead control.** Concluding otherwise from one reading, and
writing it into canon as BROKEN, was the error a paragraph now exists to prevent. A wrong
BROKEN marking costs the next session a *working* control; the same damage as a dead control
described as live, from the opposite direction.

**Write timing, resolved in canon rather than left ambiguous.** Errors, near-misses,
falsifications and retracted claims are written **at encounter time** — immediately, one
small batch. Outcomes are written as **one atomic batch at turn end**. "One batch per turn"
means one batch of *outcomes*, not one item, and not a prohibition on logging an error the
moment it appears. The contradiction between the two rules was found, resolved in a
paragraph, and recorded — the resolution is itself the artefact.

---

## XII. The standing diagnosis: how all of this decays

Everything above can be true and the system still rot, in three specific ways. These are the
tells to check when the estate feels healthy.

**1. A control whose last exercise nobody can name.** The gate exists, the config says so,
the dashboard is green — and `probe` has not been run since the machine was rebuilt. This is
§II and it is the most common failure in this document's history, in every generation:
six silent proxies, a config with five declared models and four absent, a lane whose "store"
was an empty file.

**2. A number with no unit, no source, or no date.** "62 MB". "39 of 39". "It returned 0."
Each one was true in some sense and wrong in the sense that mattered. The countermeasure is
mechanical: every figure carries *where it came from* and *when it was measured*, and every
threshold carries the gap it was placed inside.

**3. A fix that made the output quieter rather than the system safer.** Suppressing a
finding, widening an acceptance, rebaselining a scan, or teaching the report not to mention
a thing is not repair. Founder's rule, written where the gates can see it: **a scanner
finding is fixed, not rebaselined** — and a deliberate bulk override is *declared in the
commit message*, so the bypass is part of the record.

**The antidote, and the reason this document is shaped the way it is.** Every section above
ends in a command or a comparison of two artefacts. Not because commands are superior to
prose, but because **prose survives its own falsification and commands do not**. When the
next reader doubts §IV, they stop the upstream and watch the client give up in 1.65 s. When
they doubt §II, they call `/v1/chat/completions` with a tools array and read the 400.

That is the whole practice: **prefer the claim that can be killed.**

---

## Appendix A — the checks, and the one command that exercises each

| § | claim | command |
|---|---|---|
| 0 | the stack is what canon says | `python tools/mcp_startup_gate.py --fix` |
| I | the floor actually filters | differential: same noise query of `:8765` and `:8766`, proxy must return fewer rows |
| II | a control is exercised | run the tool, quote its output and *what that output establishes* |
| III | the child is not stale | `supervisor-fresh` / `pams-running` — child start time vs script mtime |
| IV | `:8766` precedes the client | `PMB_FLOOR_ORIGIN=logon` in the proxy's own env; `floor-origin` check |
| V | one holder, provably | `proxy-singleton`; `python C:/Users/clint/_board.py store` (path, symlink, rows) |
| VI | thresholds still sit in the gap | re-measure noise max/mean vs real min after any purge |
| VII | the suite is not stuck | time `check_all()`; it should be 0.09 s, not 5.4 GB of I/O |
| VIII | the refusal exists | `python tools/task_shape_check.py --check` on the task text |
| IX | the gate sees the agent | `[AP5]` in the commit output — read the findings, do not skim them |
| X | copies match sources | `orders-in-sync`; `bible_ship.py --check`; `bible_check.py --check` |
| XI | the ledger can say no | `cradle.py --grimoire` — distinguish absent / empty / unreadable |
| XII | you are not quieting a finding | `git log -1` — was the override declared? |

## Appendix B — the withdrawn claims ledger

Kept because a treatise that only lists its correct claims teaches the wrong lesson. Each of
these was believed, quoted, and acted on.

| claim | what was wrong | disposition |
|---|---|---|
| "Model 2 has ~62 MB total memory" | counted ROM boards + undecoded address space as RAM | withdrawn 2026-11-02; driver-decoded figures substituted; original kept under `withdrawn` |
| "39 of 39 rules have NO validator" | instrument dropped a leading zero | retracted; figure not 39 |
| "PID 6192 is wedged" | one timestamp generalised into a diagnosis | withdrawn |
| "`gate_timing` measures the integration" | it counted a docstring | withdrawn |
| "nonzero rc with `ok=true` is a bug" | `_KIP_RC` declares a designed skip | withdrawn; the skip is honest |
| "a nonce passing the floor means the floor is broken" | one nonce in 15 scored 0.836; the assertion shape was wrong, not the floor | replaced by a differential |
| "`prepare()` returning 0 lessons = dead control" | 0 means the message matched nothing | canon paragraph added to prevent recurrence |
| "the local model harness works" | config declared 5 models, 4 absent; 2 endpoints refused; the present one could not chat | measured 2026-11-02, verdict: inventory missing, not capability |

## Appendix C — what this pass re-derived, with output

The point of the convention in *Method*: a reader can see which claims have a receipt from
today and which are inherited.

| claim | command run 2026-11-02 | result |
|---|---|---|
| the skip is designed, not a bug | `sed -n '100,112p' scripts/chain_controller.py`; `grep -n "KIP_RC\|kip"` | `_SKIP_RC` at line **161**, `{"train": (1,), "tensor": (3,), …}` — canon's `_KIP_RC:107` is wrong on both name and line |
| the package archive is real and its size | `find skills.pkg-archive -name SKILL.md \| wc -l` | **1042** (canon's figure confirmed) |
| the local-model harness state | `/v1/models` on `:8087`, `:11435`, `:11434`; `/v1/chat/completions` with a tools array | two endpoints refused; 4 of 5 declared models absent; `eve-v2u` "does not support chat"; `olmoe` "does not support tools" |
| the agent's own output, gated | commit `ab6be175`'s pipeline | 25 checks run, 1 non-blocking failure, `[AP5]` **2 findings** in assistant prose |
| a plausible number kept alive by being plausible | driver read + address-map decode | Model 2 = 1 MiB work + 4 MiB texture + 128 KiB buffer; the "62 MB" total **withdrawn** |
| the tools each appendix cites actually exist | `for t in …; do [ -e "$t" ]` | all present except `tools/cradle.py`, which lives at `Project_CRADLE/cradle.py` |

One entry above is the whole argument of this document: **`tools/cradle.py` does not exist.**
A citation that reads perfectly, points at a path that is one directory off, and would have
sent the next reader to a `FileNotFoundError` — or worse, to the conclusion that the tool was
deleted. Check the path before you quote it.

---

**Closing line, because these documents always end in one and it should be earned:** the
bleeding edge is not the newest tool. It is the shortest distance between a claim and the
thing that would prove it false — maintained on purpose, by people who have already been
wrong in every way listed above.
