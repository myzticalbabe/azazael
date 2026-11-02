# The Research–Creative Adaptation Paradigm

### A tutorial for developers who will inherit this tree

**Status:** working paper, 2026-11-02.
**Audience:** the next developer, human or agent, who is handed a brief and a
repository and is expected to produce something true.
**What you will be able to do afterwards:** take a body of research you did not
write, turn it into an artefact this estate can check, and leave behind a record
that a stranger can falsify.

---

## 0. The one-paragraph version

Research–creative adaptation is a four-movement discipline: **research** a subject
until you know the size of its effects and the limits of its studies; **adapt** that
knowledge into the register the house actually reads — code, corpus, render,
instrument; **verify** the adaptation with something that can fail; and **canonise**
it so the next person inherits the check and not just the conclusion. The creativity
is not decoration added after the research. It is the act of finding a form that can
hold a true claim without flattering it, and the discipline is refusing to let the
form improve the claim.

This paper is written from one session's work, because an abstraction with no
artefacts behind it is the failure mode the paper is about. Every example names a
path you can open.

---

## 1. Why this paradigm exists here

This tree has a rule that most repositories do not: **a number with no command is a
claim, and claims are refused.** `tools/bible_check.py` enforces it on a corpus of
prose; the commit hook enforces the corpus. The rule exists because the estate has
already paid for its absence — a circulated figure, a copied constant, a green gate
over a dead stack. Every one of those failures had the same shape: something
plausible was written down, and nothing could tell whether it was still true.

Research–creative adaptation is the positive form of that rule. It says:

1. A finding enters the tree through a **source you have read**, not a summary you
   have seen.
2. It enters as an **artefact** — a file, a schema, a test, a render — not as
   enthusiasm in a chat message.
3. The artefact must be **checkable by someone who distrusts you**.
4. The check is part of the deliverable. A conclusion without its check is a
   rumour with good formatting.

The paradigm is not "do research, then be creative." It is "do research, then build
the thing that would embarrass you if the research were wrong."

---

## 2. The four movements

```
   ┌──────────┐    ┌──────────┐    ┌────────────┐    ┌────────────┐
   │ RESEARCH │───▶│  ADAPT   │───▶│   VERIFY   │───▶│  CANONISE  │
   └──────────┘    └──────────┘    └────────────┘    └────────────┘
        │               │                │                 │
   effect size      a form that      a control that    one source of
   + limit          can hold it      can fail          truth + a reader
        │               │                │                 │
        └──── if the form cannot hold the limit, change the form ────┘
```

The arrow back is the important one. In this session the research on gender and
emotion could not be adapted as "women are more emotional" — the effect sizes
refused it — so the *form* changed: the specialised corpus opens with a book on how
small the differences are, and its last book lists what a system may not do with
them. The research did not decorate the artefact; it dictated its architecture.

---

## 3. Movement I — Research

### 3.1 Read the effect size before the sentence

A finding is a number with a sample and a design attached. If you cannot state the
effect size, the sample, and the design, you have a topic, not a finding.

Worked example, from the research behind `docs/bible/emotional/`:

| what was searched | what came back | what it forced in the corpus |
|---|---|---|
| gender differences in emotion | a metasynthesis of 46 meta-analyses: most effect sizes small or near zero | `female.json` opens with *The Book of the Same Weather* |
| emotion expression in children | 555 effect sizes, 166 studies, g ≈ 0.08–0.10, moderated by context | the difference is expression and context, not capacity |
| rumination | d ≈ 0.24, described by its authors as small | rumination is a response style, not a gender |
| alexithymia | d ≈ 0.22 over 120 studies | granularity is a skill, not a feminine trait |
| backlash for dominance | d ≈ −0.19 across 63 studies | `narrow_door 2:3`: "the average penalty is small; the individual penalty is not paid in averages" |
| partner violence | ~30% of women vs ~17% of men, lifetime, with impact; wide state range | prevalence is stated, and `refusals 1:4` forbids using it as a verdict |

Notice what the table does: it converts research into **constraints on prose**. The
small effect size is why the corpus cannot say "women are penalised" without the
qualifier; the wide range is why the corpus cannot say "one in three women you meet."

### 3.2 Prefer the primary paper, and read the abstract's caveat

Secondary coverage drops the limit first. A press release about a meta-analysis will
say "women are better at reading emotions"; the paper says the difference is small
and that the proportion of male authors moderates it. Adapt the paper, not the
release.

### 3.3 Search for the negative result on purpose

For any contested claim, run one search whose only job is to find the correction:
`"<claim> replication failure"`, `"<claim> meta-analysis null"`, `"<construct>
measurement critique"`. If the correction exists and you did not look for it, you
have not researched; you have shopped.

In this session that search is why **stereotype threat is not load-bearing anywhere
in the female corpus**: the meta-analytic picture is contested, so the corpus does
not borrow its authority. That decision is recorded in
`docs/bible/emotional/SOURCES.md` §9, under "what the corpus deliberately does not
cite." A register of exclusions is as valuable as a bibliography.

### 3.4 The saturation test

Stop searching when three conditions hold:

1. New searches return studies you have already read.
2. You can state the strongest counter-argument to your intended claim, in its own
   terms, without caricature.
3. You can say what evidence would change your mind.

If you cannot do (3), you are not ready to adapt. The adaptation would be a
commitment disguised as a summary.

---

## 4. Movement II — Adaptation

### 4.1 Choose the register by what the claim needs to survive

The same research can become several artefacts. The choice is not aesthetic; it is
about which form can carry the claim's *limits* without dropping them.

| register | holds | drops | use when |
|---|---|---|---|
| code | executable behaviour, invariants, per-person parameters | explanation, context | the claim is "the system must not do X" |
| validated corpus | doctrine with citations, refusals, apparatus | speed of reading | the claim governs vocabulary and judgement |
| test | falsifiability | nuance | the claim is a boundary |
| render | attention, sequence, mood | precision | the claim is about seeing |
| whitepaper | method and reasoning | enforcement | the claim is about how to work |

A claim about how a system should *speak about feeling* cannot live in a test alone.
It needs a corpus: a text a persona can be held to, with citations that resolve and
refusals that can be quoted back. That is why the emotional bible is a corpus and
not a docstring.

### 4.2 The fidelity budget

Adaptation is translation under a budget. Three things may be changed; three may
not.

**May change:** voice, structure, compression, metaphor, ordering, the artefact's
medium.

**May not change:** the size of an effect, the direction of a causal claim, the
population a study measured, or the existence of a competing finding.

The failure mode has a name worth using: **stereotype laundering** — taking a real
but small average difference, passing it through prose that removes the qualifier,
and returning a confident generalisation with a citation attached. The citation
makes it worse, because it is now defensible in an argument and false in use.

### 4.3 The constraint is the creativity

The most useful creative act in this session was accepting a constraint that looked
like an obstacle: **the corpus may not contain digits.** A figure needs a command,
and a research figure has no repository path, so the digit cannot enter the verse.

That constraint produced the architecture:

- the verses became qualitative claims that survive the loss of the number;
- the numbers moved to `SOURCES.md`, where each sits beside its study and its limit;
- a reader who wants the figure is sent to the caveat that came with it;
- the corpus can be quoted in a persona without smuggling a statistic into a
  conversation.

A constraint that forces provenance is not a limitation on creativity. It is the
shape of the creativity.

### 4.4 Four tests for a legitimate adaptation

Before you call an adaptation done, apply these. Any "no" sends you back to the
research, not to the prose.

1. **Decision test.** Does this artefact change what a system or a person would
   *do*? A beautiful restatement that changes nothing is a summary.
2. **Caveat test.** Does the artefact survive the strongest limit in the source? If
   the source says "small effect, contested," can your artefact still be read
   without implying "large, settled"?
3. **Failure test.** Can this artefact be shown false? If nothing could contradict
   it, it is decoration.
4. **Voice test.** Is it in the house's register, or in the register of the industry
   it was borrowed from? A canon written in a single borrowed register is pastiche.

### 4.5 Worked example: research becoming architecture

`Project_ELIZA/eliza/psyche/affect.py` is the cleanest case in the tree. The
research finding was **similarity of capacity, difference in expression and
regulation**. The adaptation was not a paragraph about gender; it was an
architectural refusal:

- no function in the module takes a demographic attribute, so no caller can route a
  person through a group template;
- a test introspects the signatures and fails if such a parameter is added;
- display output carries felt and displayed state plus the rule that modified the
  display, so the system cannot tell a person what she "really" feels from what she
  showed.

That is research–creative adaptation at its best: the finding became a signature,
and the signature became a test. Read the module docstring before extending it; the
reasoning is there, in the code, where the next developer will trip over it.

### 4.6 Worked example: the creative loop is iterative, and the artefact is the judge

`renders/jaeger/` holds nine preview iterations of a single shot before the tenth
was accepted. The lesson is not "render nine times." It is that **you read the
rendered artefact, not the code that produced it.** Three defects in this tree have
survived source review and died only in the output: a scanline pass compositing
black through a mask, a dead middle band of a frame, and a readout printing a dash
where its number should be. A render is a research instrument pointed at your own
work.

### 4.7 Worked example: a ritual becoming one command

`tools/one_click_bootstrap.py` is the adaptation of a checklist into an artefact.
The research was a list of failure classes: hooks not installed, defaults not
applied, canon blocks drifted, anchors missing, packages absent, CI divergent,
metrics absent, reproof ratchets stale. The adaptation collapses them into one
entry point with eight named checks and a `--check` mode that is safe to run.

Two details make it an honest instrument rather than a nice script:

- each check reports `OK`, `RED`, or `BLIND` with a reason, never a bare pass;
- the one remaining red on this machine — `pywin32` — is reported as an unavailable
  wheel on the production interpreter rather than suppressed, because a check that
  hides its number when the reading is bad is worse than no check.

Run it before you trust a session:

```bash
python tools/one_click_bootstrap.py --check
```

---

## 5. Movement III — Verification

### 5.1 A claim needs its command

Write the command beside the claim, in the artefact, not in your memory. The canon
does this at the level of a single verse: a `statute` names a rule in `MANDATES.md`
and a `check` path that exists, and a law with nothing executing it is refused.

### 5.2 Every oracle ships a negative control

A validator that has never fired is unknown, not working. `tools/bible_check.py`
has tests that corrupt a corpus and assert the checker refuses it; `bible_ship.py`
has `--self-test`. When you add a check, add the input it must reject in the same
commit.

### 5.3 The instrument is part of the deliverable — and it will have bugs

This is the part tutorials usually omit. While adapting the two corpora, the shared
validator failed them for reasons that were *not* defects in the corpora:

1. `--check --corpus X` compared the canon's generated edition
   (`BOOK_OF_THE_TREE.md`) against a render of **X**, so every alternate corpus was
   reported stale by construction.
2. `--render --write` wrote to the hard-coded canon path, so rendering a sibling
   corpus would have overwritten the canon with it.

Both were fixed in `tools/bible_check.py`: the edition path is now derived from the
corpus (`edition_path()`), the generated-drift check only holds the canon to the
canon's edition, and the provenance line inside the rendered file names the corpus
it actually came from. The rendered file had been claiming
`docs/bible/bible.json` as its source while containing a different book — a false
provenance line a reader could not detect from the file itself.

The general lesson: **when a validator rejects your artefact, establish which of the
two is wrong before editing either.** A tool that cannot describe a second case is
a tool with a hidden assumption, and the assumption is a finding.

### 5.4 Preserve the exit status

A pipeline that swallows a non-zero exit is a check that reports success. In this
session the first validation looked green because `tail` consumed the status; the
rerun used `set -o pipefail` and the failure appeared. Measure the command, not the
last line of its output.

### 5.5 Stale artefacts lie in a specific way

A cached count, a generated file, a snapshot: each answers for a tree it no longer
describes. Regenerate before you quote, or say which run you are quoting. The canon
already treats this as a first-class defect — the drift check refuses a stale
edition, and the harvest ledger reports how many observations have landed since its
snapshot without failing the build, because a gate that goes red every time someone
records a bug fix gets switched off.

---

## 6. Movement IV — Canonisation

### 6.1 One source of truth, and the copy is the enemy

The first thing that happens to a second copy is drift. So the canon is written
once, validated once, and every other appearance is a pointer:

- `docs/bible/bible.json` — the canon of the tree;
- `docs/bible/emotional/emotional.json` — the canon of the felt;
- `docs/bible/emotional/female.json` — the specialised canon;
- `docs/bible/emotional/SOURCES.md` — the only place a research figure may be
  quoted from.

When you add a corpus, add it to the prose that governs the corpus directory
(`docs/bible/README.md`), not to five summaries. Canonisation is not announcing; it
is putting the thing where the next check will find it.

### 6.2 Update the bible in its own voice

A canon that describes a tree which no longer exists is a dead document with good
formatting. When the corpora were added, the corpus README gained a section written
in its own register — what the siblings are, why they are corpora rather than
themes, what changed in the validator to make them possible, and what they inherit.
That edit is part of the deliverable, not a chore after it.

### 6.3 Memory writes have two clocks

- **Encounter time:** every error, near-miss, or retracted claim, recorded when it
  happens, in one small batch. Reconstruction at session end over-weights whatever
  is still salient and loses the detail that made the error instructive.
- **Turn end:** outcomes — what was built, what was decided and why, what the user
  asked for next.

A lesson that is not closed (`mark_lesson_followed` with a real note) is a lesson
the next session cannot tell from an unread one.

---

## 7. The anti-pattern catalogue

Each of these has cost this estate something. Learn them by name.

| anti-pattern | what it looks like | the tell |
|---|---|---|
| **Stereotype laundering** | a real, small group difference restated without its qualifier | the citation is present and the effect size is not |
| **Eloquence as truth** | a beautifully written passage nobody can check | you cannot name the command that would falsify it |
| **Citation theatre** | a bibliography assembled from search snippets | you cannot state the sample or the design of any entry |
| **Adapting the metric** | the artefact is shaped to make the dashboard green | the measurement changed, the behaviour did not |
| **Oracle without a control** | a new check that has never fired | no test asserts it rejects a known-bad input |
| **The second copy** | a summary that will drift from its source | two files claim to be authoritative |
| **Over-generalisation** | a rule true in every situation and decisive in none | it cannot name the decision it changes |
| **Instrument worship** | trusting a generated count for a verdict | the count was never re-run against the current tree |
| **Permission theatre** | asking whether to do the authorised task | the request already said to do it |

The last one is worth a sentence. If the user asked for the work, the ordinary steps
— running the validator, installing the declared dependency, regenerating the
artefact — are authorised by the request. Asking again spends the user's attention
on a decision they already made.

---

## 8. Tutorial: build one corpus in an afternoon

A concrete recipe, using this tree's tools. Substitute your subject.

### Step 1 — Write the research register first

Create `docs/<your-topic>/SOURCES.md`. For each source: the finding, the effect
size, the sample, the design, and the limit. Write the limit *before* you write the
verse that will use the finding. If you cannot write a limit, you have not read the
paper.

### Step 2 — Choose the schema before the prose

Read `tools/bible_check.py`'s docstring and `docs/bible/README.md`. Know what will
be refused: digits without a path, unresolved citations, a statute without a check,
a heading with a figure, a book without an introduction at `complete` status.

### Step 3 — Draft books as domains, not as chapters of an essay

A book is a subject with a job. Give it a `genre` from the declared list and let the
genre set the voice: `law` for what must hold, `lament` for what happened, `wisdom`
for what was learned, `apocalypse` for what must not happen. One register for twelve
books is pastiche.

### Step 4 — Put the apparatus in, while the correction is fresh

For every claim you are correcting, add a `variant` with the wrong reading and where
it came from. Deleting a wrong reading teaches nothing; the apparatus is how a
reader watches the correction happen.

### Step 5 — Validate, and read the failure as a finding

```bash
python tools/bible_check.py --check --corpus docs/<your-topic>/corpus.json
```

If it fails, decide which is wrong: the corpus or the checker. In this session the
checker was wrong twice. Fix the smaller thing, and add the case to the test suite.

### Step 6 — Render, and read the rendered artefact

```bash
python tools/bible_check.py --render --write --corpus docs/<your-topic>/corpus.json
```

The renderer writes beside the corpus. Read the output as a reader would; the
provenance line, the headings, and the note placement are all part of the claim.

### Step 7 — Add the corpus to the prose that governs it

One section in the directory README, in that document's voice: what this is, why it
is a corpus rather than a theme, how to check it, what it refuses.

### Step 8 — Wire the check

If the corpus is meant to hold, it needs a consumer: a commit-hook stanza, a gate
registry entry, a test that runs it. An artefact nobody checks is a draft with a
schema.

### Step 9 — Record the decisions

One memory batch at turn end: what was built, the two validator bugs, the decision
not to cite contested literature, the file paths. Absolute dates.

### Step 10 — Report the limits

Say what you did not do. The corpus does not diagnose, does not replace a clinician,
does not cover every woman, and does not carry the figures itself. Those limits are
in the artefact, and they belong in the report too.

---

## 9. Checklist before you ship an adaptation

- [ ] I read the primary source, not the summary.
- [ ] I can state the effect size, the sample, and the design.
- [ ] I can state the strongest counter-argument without caricature.
- [ ] The artefact survives the source's caveat.
- [ ] Every figure has its command or lives in a register with its limit.
- [ ] Every citation resolves.
- [ ] A test or a control can show the artefact is wrong.
- [ ] The validator passes, and I read its output rather than its exit line.
- [ ] The generated file was regenerated, not hand-edited.
- [ ] The governing README describes the new artefact.
- [ ] The check is wired to something that runs without me.
- [ ] I have named what this does not do.

---

## 10. Exercises

1. **Find the laundered statistic.** Take any popular article about a group
   difference. Find the underlying meta-analysis. Write the sentence the article
   should have written, with the effect size and the limit. Then write the corpus
   verse that would survive both.
2. **Break your own validator.** Add a corpus with a digit in a verse and no
   `source`. Confirm the checker refuses it. Then add one that cites a verse in a
   different corpus and confirm it is refused too. If either passes, you have found
   a hole, not a convenience.
3. **Adapt without prose.** Take a finding you believe and express it as a
   signature, an invariant, or a test — no comments. If the implementation cannot
   carry the finding, the finding was not operational.

---

## Appendix — the artefacts this paper is about

| path | what it is |
|---|---|
| `docs/bible/bible.json` | the canon of the tree: 15 books, 26 verses, 9 pinned configs |
| `docs/bible/emotional/emotional.json` | the canon of the felt: 8 books, 58 verses |
| `docs/bible/emotional/female.json` | the specialised canon: 9 books, 57 verses, 5 corrected readings |
| `docs/bible/emotional/SOURCES.md` | every figure, with its study and its limit |
| `docs/bible/emotional/README.md` | the contract for the sibling corpora |
| `docs/bible/README.md` | the canon's own prose, updated to name its siblings |
| `tools/bible_check.py` | the validator, including `edition_path()` and the corpus-aware drift check |
| `Project_ELIZA/eliza/psyche/affect.py` | research adapted into a signature that refuses a demographic parameter |
| `Project_ELIZA/tests/test_psyche_affect.py` | the test that keeps the refusal true |
| `tools/one_click_bootstrap.py` | a checklist adapted into one command with eight named checks |
| `renders/jaeger/` | nine previews, because the artefact is the judge |

---

*Methodology ships; people do not. Nothing in this paper, or in the corpora it
describes, is a diagnosis, a prediction about a person, or a substitute for a
clinician. Where the evidence is small or contested, the artefact says so, and that
sentence is the point of the whole exercise.*
