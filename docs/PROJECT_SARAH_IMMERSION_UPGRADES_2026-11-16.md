# Project Sarah — Immersion Upgrade Proposal, All Known Neurodivergent Sub-Types

**Written:** 2026-11-16 · **HEAD at write:** `bf7e2703` · **Target stack:** MellifluousML A-I-O (Python 3.16t free-threaded, local inference, pmb/pams/krampus payload)
**Status:** design proposal, not a build order. **Acceptance language is forbidden here** — this document states what the evidence supports and what it does not.

> **Spec position, stated first because it changes how this reads.**
> Kilo's build instructions for Project Sarah are **not on disk** at the time of writing. A grep over
> `MELLI_OS/`, `MELLI_OS_SPEC.md`, `BRICK_MELLIFLUOUSML_AIO.md` and `azazael/docs/` returns exactly one
> mention of "Project Sarah" — `docs/HANDOFF_2026-11-16.md`, which names it as pending work and carries no
> design. So this document is written **against the MellifluousML stack** (local models, free-threaded
> runtime, pmb/pams memory, no cloud round-trip), not against a spec I have not seen. Where Kilo's brief
> already decides something, the brief wins; the modules below are named so they can be accepted, merged or
> rejected one at a time.

---

## 0. The thesis, in one paragraph

"Neurodivergent immersion" is usually built as *more* — more stimulation, more presence, more fidelity.
The measured direction is the opposite: in the one study that asked 20 autistic adults to rate multisensory
XR comfort directly, the **lowest-rated** condition was the one with click-triggered spatial audio
(M = 2.97/5, tied for lowest, 16 of 20 rating it low), and the **highest** was gradual light/audio with
optional vibrotactile/thermal feedback (M = 4.43). What they valued was clarity, self-pacing, gradual
transitions and an exit; what they disliked was abruptness, simultaneous demands and insufficient warning
(arXiv `2610.23833`). A system engineered to be tolerable is a system engineered to *reduce load on demand*,
not to maximize stimulus. That inversion is the whole design.

The second inversion: **the same feature helps one sub-type and harms another.** Reading fluency fonts are
worthless (measured, §2.1); a visible countdown timer that reduces ADHD inattention can *raise* anxiety in
autism; a gentle "how do you feel?" prompt is a bridge for alexithymia and an interrogation for PDA. So the
build cannot be a fixed experience with an accessibility checkbox. It has to be a **profile-driven runtime**
with a shared substrate and per-axis adaptation — which is Module 1, and everything else depends on it.

---

## 1. Evidence grades used in this document

| grade | meaning |
| --- | --- |
| **A** | Meta-analysis or multiple independent RCTs, consistent direction |
| **B** | One RCT, or a systematic review with material risk of bias |
| **C** | Small-N study, observational, preprint, or single-site trial |
| **D** | Mechanism plausible, **untested for this use** — a design hypothesis, never a claim |

**A grade D module is legitimate to build and forbidden to advertise as effective.** That distinction is the
difference between a product and a placebo with a roadmap.

---

## 2. What the evidence actually says — including where it says "no"

### 2.1 Three popular interventions that do not survive measurement

| intervention | measured result | grade | consequence |
| --- | --- | --- | --- |
| Dyslexia-specific fonts (Dyslexie, OpenDyslexic) | meta-analysis, 15 studies, N = 688: **g = −0.04, 95% CI [−0.15, 0.07], p = .5**; Kuster 2017 (n = 170) found no benefit | **A (null)** | Do not ship a font as a fix. Ship **letter-spacing and line-height controls** — extra-large letter spacing improved reading speed and errors (2021). |
| Coloured overlays / Irlen lenses | not endorsable as a reading intervention (Griffiths 2016; Suttle 2018) | **A (null)** | Offer as a cosmetic comfort preference only; never as evidence-backed treatment. |
| VR as a superior therapeutic medium | VR biofeedback **no better than 2D** in RCT (2025); adaptive VRET feasible only in small studies | **B** | Spend the budget on adaptive *content and pacing*, not on headset presence. A 2D implementation of the same governor should score the same. |

### 2.2 What does have signal

| intervention | measured result | grade |
| --- | --- | --- |
| Visual timers for time-blindness | inattention reduction correlated with Conners score, **ρ = 0.448, η² = 0.15** (2025); time-skill + assistive-device RCT (2017) improved time processing | **B** |
| Self-affirmation | APA 2025 meta, 67 studies, self-perception **g = .32**; small overall; **backfire reported for low self-esteem** (Wood 2009); null results exist | **A (small, conditional)** |
| Weighted blankets | anxiety **SMD 0.40** (2024 SR, 8 RCTs, 426 participants, half at high risk of bias); ADHD sleep RCT n = 94, d = 0.24–0.27, **larger in the inattentive sub-type (d = 0.58)**; not a standalone insomnia treatment | **B** |
| Interoception / emotion-recognition training | MT-ALEX: **d = 0.97** emotion recognition, **d = 1.14** alexithymia; 2026 digital RCT (n = 47, TAS-20 ≥ 61) significant; mindfulness SR **MD −5.28** | **B** |
| Haptic over visual heartbeat feedback | haptic interoceptive feedback outperformed visual (Dobrushina 2024) | **C** |
| HRV biofeedback (remote) | depression **g = −0.41** | **B** |
| Body doubling | survey N = 220, self-reported benefit; 2025 EEG study (ASSETS) found **no significant** focus or performance effect; **no RCT exists** | **C (self-report only)** |
| AI companion / chatbot for emotional support | companionship use associated with **lower** well-being, worse at higher intensity and self-disclosure (arXiv `2506.12605`); 4-week RCT n = 981: more daily use → more loneliness and dependence, less socialization; therapy bots endorsed harmful proposals in **19/60** scenarios (32%) | **B (harm)** |

### 2.3 Sub-type cognitive profiles (what the deficit actually is)

| sub-type | measured cognitive signature | grade |
| --- | --- | --- |
| Autism | processing speed **≈ −1 SD**, spiky profile across domains (ACN 2023 meta, > 1800 people); response inhibition SSRT **+23.1%** | **A** |
| ADHD | less specific profile; working memory slightly reduced; SSRT **+18.8%** (shared inhibition deficit with ASD) | **A** |
| Cognitive Disengagement Syndrome (formerly CDS/SCT) | **distinct from ADHD**, renamed in JAACAP 2023; 49% of cases are CDS-only; signature is *mind-wandering/daydreaming*, slow tempo, hypoactivity — not impulsivity | **A** |
| Dyslexia | phonological decoding + rapid naming; **not** a visual-font problem | **A** |
| Dyscalculia | magnitude/number-sense representation, not arithmetic practice alone | **B** |
| Dysgraphia | motor-orthographic transcription; dictation bypasses it | **B** |
| Dyspraxia / DCD | motor planning and sequencing; **ideation** of the next step, not strength | **B** |
| Alexithymia (transdiagnostic) | emotion *identification* and *description* deficits, not absence of feeling | **A** |
| PDA profile | evidence **weak and contested** — Kildahl 2021; JADD 2026 calls the construct's logic circular | **C (contested)** |
| Autistic burnout / masking | 13-article SR (2026): exhaustion, executive impairment, suicidal ideation **52–70%**; masking↔stress in EMA (2025) | **B** |
| Auditory processing disorder | degraded speech-in-noise, not hearing loss | **B** |
| Aphantasia / prosopagnosia / synaesthesia | cognitive variance, not deficit; changes which channel carries the content | **C** |

**Design consequence of the PDA row:** because the construct is contested, *do not gate features on a PDA
diagnosis*. Build autonomy-preserving interaction (invitations, choices, no imperative verbs) as the default
for everyone. It costs nothing when the construct is wrong and helps when it is right.

---

## 3. The sub-type → deficit → adaptation matrix

The columns are the eight axes of the profile vector (Module 1). "Primary" means the axis this sub-type most
often needs adjusted; "secondary" means it commonly co-occurs.

| sub-type | primary axis | secondary | the adaptation that bridges it | grade |
| --- | --- | --- | --- | --- |
| ADHD-inattentive | sustained attention | initiation threshold | chunked task cards (one instruction), visible progress, optional visual timer, re-entry after drift without penalty | **B** |
| ADHD-hyperactive | sensory gain / restlessness | initiation threshold | movement-permitting layout, fidget affordances, short cycles with a "burn" activity, no forced stillness | **C** |
| Autism | sensory gain | recovery latency | predictable transitions, pre-brief, literal language, exit-anywhere, silence-by-default audio | **B** |
| CDS / SCT | sustained attention (slow tempo) | processing speed | longer response windows, no timed prompts, "take the time you need" as default, gentle re-orientation cue | **B** |
| Dyslexia | processing speed (text) | working memory | letter-spacing + line-height, TTS read-aloud, syllable chunking, no font gimmick | **A** |
| Dyscalculia | time/number representation | working memory | quantities as bars and dots, "time remaining" as a ribbon not a clock, analog↔digital bridge | **B** |
| Dysgraphia | motor output | working memory | dictation-first input, no handwriting requirement, speech-to-text with edit-after | **C** |
| Dyspraxia / DCD | initiation (motor planning) | working memory | "next physical step" cueing, one action per screen, undo everywhere | **C** |
| Alexithymia | interoceptive accuracy | — | body-map + emotion-word ladder, 3 candidate labels with "not sure" first-class, haptic heartbeat | **B** |
| Autistic burnout | recovery latency | sensory gain | load meter, enforced breaks, low-demand "people-adjacent" mode, no streak pressure | **B** |
| APD | sensory gain (auditory) | working memory | captions on by default, speech-in-noise reduction, one voice at a time, visual redundancy | **B** |
| Aphantasia | channel preference | — | describe in words and structure, do not rely on "visualise this"; offer text-first | **C** |
| Non-speaking / minimally verbal | channel preference | processing speed | symbol sets (XAUR REQ 3a), pictogram + text + audio redundancy, AAC-shaped output | **B** |
| Tourette / tic | sensory gain | — | no suppression prompts, no "are you okay" interrupts, private-mode by default | **C** |

---

## 4. Fifteen upgrade modules

Each module is independently acceptable. Names are stable so Kilo's brief can adopt or reject them by name.
`Depends:` lists the module that must exist first.

### M1 — Cognitive Profile Vector (the substrate)
**Depends:** none.
Eight axes, each 0–1: `processing_speed`, `wm_span`, `sustained_attention`, `sensory_gain`,
`interoceptive_accuracy`, `time_discrimination`, `initiation_threshold`, `recovery_latency`.
Populated three ways, in this precedence: (1) explicit user sliders — the user is the authority;
(2) a 6-item behavioural micro-probe per axis (reaction-time, n-back-lite, time-estimation, body-map tap);
(3) inferred from session telemetry (abandon points, re-read counts, pause distributions) — **never**
diagnosis. Stored in pmb as a versioned record, not a mutable blob, so a profile change is auditable.
**Why this is M1:** every later module reads it, and the alternative — per-feature settings — is how
accessibility menus become a second product nobody maintains.

### M2 — Adaptive Pacing Governor
**Depends:** M1.
Speech rate 120–165 wpm (TTS ~150 wpm is the preferred band in the aphasia literature), chunk length 5–9
words, inter-chunk gap scaled by `processing_speed`, and a comprehension checkpoint every N chunks that
**slows** rather than repeats. Prosody: autistic speakers show slower rate and wider pitch range, so a
monotone synth is the wrong default — vary pitch, never rush.
**Cap:** the governor may only *reduce* demand. It never speeds up to "catch up".

### M3 — Sensory Gain Mixer with one global contract
**Depends:** M1.
One master "intensity" control scales **all** modalities together, plus per-modality trims. Implements XAUR
REQ 3b (mute non-critical) and REQ 3a (symbol sets) as real behaviour, not documentation.
**Contract:** every new sensory feature must declare its default in the mixer before it ships. A feature that
cannot be turned down does not land.

### M4 — Gradual-Transition Engine
**Depends:** M3.
Every state change ramps over 400–1200 ms; **never two modalities change simultaneously**; every change is
announced one beat before it happens. This is the single most-supported finding in the XR comfort study
(L4/L5 rated highest, M = 4.43), and it directly contradicts the standard "scene cut + sting" idiom.

### M5 — Self-Pacing and Unlimited Time
**Depends:** M1.
No countdown unless the user asks for one. XAUR REQ 12a. When a timer *is* requested, it is a visual ribbon
(the measured inattention effect, ρ = 0.448) with a pause that actually pauses.

### M6 — Predictability Packet
**Depends:** none.
Before any state change: what happens, how long it takes, how to leave. Symbol + literal sentence, W3C COGA
patterns (familiar design, literal language, chunking, no double negatives). This is the cheapest module in
the document and the highest-value one for autism and CDS.

### M7 — Exit-Anywhere and Safe-Place Return
**Depends:** M6.
XAUR REQ 11a and 13a: one keystroke returns to a low-stimulation hub, and the return **preserves** state via
pmb so re-entry is not a restart. Exit is never punished, scored, or commented on.

### M8 — Interoception Bridge
**Depends:** M1.
Body-map with tappable regions → emotion-word ladder → three candidate labels with **"not sure" as a
first-class answer**. Optional haptic heartbeat (haptic beat visual, Dobrushina 2024). Never a forced
free-text "how do you feel?" — that is the alexithymia failure mode.

### M9 — Time Scaffolding
**Depends:** M1, M5.
Duration made visible as length (ribbon, bar, dot-train), not as clock arithmetic. "Time remaining" phrasing,
not "ends at 14:40" — which is dyscalculia-hostile. Optional time-estimation micro-game as the training
component (time-skill RCT, 2017).

### M10 — Working-Memory Offload
**Depends:** none.
Persistent visible scratchpad; one instruction per card; recognition over recall (show the options, do not
ask the user to remember them); "show, don't tell" previews.

### M11 — Initiation Ladder, autonomy-preserving
**Depends:** M10.
Task broken into "the next physical action" (open the lid, not "get ready"). Framed as an invitation with a
choice, never an imperative — this is the PDA-safe default that costs nothing if the construct is contested.
Body doubling offered as an **optional, labelled self-report tool**, explicitly not claimed as evidence-based.

### M12 — Masking-Load Meter and Burnout Guard
**Depends:** M1.
Tracks cumulative demand (session length, modality count, transitions, social load) and enforces soft stops
before the recovery-latency axis is breached. Post-session, offers the "people-adjacent" low-demand mode the
burnout literature names as recovery: solitude, sensory respite, pacing, low-demand re-engagement.

### M13 — Anti-Dependency Companion Contract
**Depends:** none.
The harm evidence is the strongest signal in this entire document, so it gets a contract, not a feature flag:
hard caps on companion time; no parasocial intensification (no "I missed you", no exclusivity language); the
companion **never** gives un-supervised clinical advice (32% harmful-endorsement rate); every reflective
session ends by pointing outward — a person, an action, or the user's own next step.

### M14 — Affirmation Engine (the Project Sarah core)
**Depends:** M1, M8, M13.
**Value-affirmation, not trait praise.** Self-affirmation's effect is g = .32 and it **backfires for low
self-esteem**, so: user-authored affirmations, no comparison to others, no streak-shaming, no "you're
amazing" (trait praise is the backfire shape). The engine surfaces the user's *own* stated values and a
concrete instance of acting on them this week. If it cannot find one, it says so — it does not invent
evidence.

### M15 — Cross-Modal Redundancy (not simultaneity)
**Depends:** M3.
The same content via text + audio + pictogram, with the user choosing the channel. Critically: **redundancy
is not simultaneity** — simultaneous demands were the second-most-disliked thing in the XR study. Redundant
channels exist so one can be *off*.

---

## 5. Hyper-edge immersion levers, with hard caps

"Hyper-edge" here means the levers that push presence past the comfortable middle. Each one needs a cap or it
becomes the thing the user has to escape from.

| lever | what it buys | cap |
| --- | --- | --- |
| Gradual multi-modal ramps (light + slow audio + optional vibrotactile/thermal) | highest measured comfort (M = 4.43/5) | ramp floor 400 ms; never simultaneous with a content change |
| Vibrotactile / thermal feedback | high rated, novel channel, works when audio is off | **off by default**, explicit consent, per-session re-consent |
| HRV-adaptive difficulty | real signal (HRV-B depression g = −0.41) | adapts **downward only**; never raises challenge on a "good" reading; visible to the user |
| Embodiment / avatar presence | identity and agency | low fidelity, no mirror, no reflective surfaces, no uncanny face |
| Local-model personalisation | no cloud round-trip, no data leaving the machine, latency low enough to pace | any personalisation must be inspectable and deletable per-record in pmb |
| Spatial audio | immersion in games | **user-initiated only** — click-triggered spatial audio was the lowest-rated condition (M = 2.97). No surprise panning. |

**Never, under any cap:** flicker above 3 Hz, parallax scroll, autoplay motion, abrupt light change, two
simultaneous demands, countdown on a first visit, or a "focus mode" that removes the exit.

---

## 6. Do-not-build list

1. **A dyslexia font as a fix.** g = −0.04, p = .5. Letter-spacing instead.
2. **Coloured overlays as treatment.** Offer as preference, never as evidence.
3. **VR-first anything.** VR biofeedback was not better than 2D; presence is not the mechanism.
4. **A therapy chatbot with no supervision boundary.** 19/60 harmful endorsements.
5. **Weighted-blanket claims beyond anxiety/sleep-onset.** SMD 0.40 with half the trials at high risk of bias.
6. **Body-doubling as an "evidence-based" feature.** Self-report only; no RCT; one EEG study found no effect.
7. **Diagnosis-gated features.** PDA is contested; the autonomy default helps regardless.
8. **Streaks, scores and "you missed a day".** Directly antagonistic to burnout recovery.
9. **Forced eye contact, "social skills" framing, or suppression prompts for tics.**
10. **A single "accessibility mode".** One switch for eight axes is the failure this document exists to avoid.

---

## 7. Instrumentation — how you know a deficit was actually bridged

Every reading carries its denominator (HED-9). Four measurements, all within-subject:

| measure | instrument | target |
| --- | --- | --- |
| Task completion without abandonment | session telemetry, per module, `completed / started` | lift vs. baseline profile-matched control run |
| Re-read / re-listen rate | content telemetry | fall on text axes, not rise on audio axes |
| Time-to-first-action after a card appears | timestamp delta | fall on `initiation_threshold`, no fall on `processing_speed` |
| Self-reported load (1–5) + recovery time after session | one question, exit survey | load down, recovery latency down |

**A module that raises the load score while raising completion has not bridged a deficit — it has made the
task compulsory.** Both numbers ship together or neither does.

---

## 8. Build order against the MellifluousML stack

| phase | modules | why this order |
| --- | --- | --- |
| **P0** | M1 profile vector + M6 predictability + M7 exit | everything reads the profile; exit and predictability are the safety floor |
| **P1** | M3 mixer + M4 transitions + M2 pacing | the sensory substrate; all three are cheap and all three are prerequisites for immersion |
| **P2** | M10 offload + M11 initiation + M9 time | the executive-function cluster; these are the deficit-bridging core |
| **P3** | M8 interoception + M14 affirmation | the Project Sarah core; needs M8's vocabulary before M14 can be honest |
| **P4** | M12 load meter + M13 companion contract | guards; ship before any companion feature, not after |
| **P5** | M5 self-pacing timer + M15 redundancy + hyper-edge levers | the polish layer; only after the caps in §5 are enforced in code |

**Stack notes.** Free-threaded 3.16t means the adaptation loop can run on a worker thread without a GIL stall
in the render path — but the governor must be bounded and monotonic-polled, never a `sleep(0.01)` busy-wait.
Profile and session telemetry live in pmb (versioned records, inspectable, deletable). Local A-I-O models do
the pacing decisions and the affirmation drafting; nothing in this design requires a network call, which is
also the privacy answer for a population that has good reasons not to trust data collection.

---

## 9. Open questions — for Kilo's brief, not answerable here

1. **Does Kilo's spec already fix the profile model?** If it does, M1 must be rewritten as an adapter, not a
   competing substrate.
2. **Which sub-types are in v1?** This document covers all known sub-types; shipping all fifteen modules at
   once is how none of them get tested. P0+P1 alone is a defensible v1.
3. **Is there haptics hardware in the target environment?** M8's haptic heartbeat and the vibrotactile lever
   are D/C-grade without a device.
4. **What is the local model budget?** M2 and M14 want a model good enough to write a non-generic sentence;
   a small model will produce the trait-praise shape that backfires.
5. **Who is the affirming voice — the system or the user?** M14 assumes user-authored. If the spec assumes
   system-authored, the backfire risk has to be addressed explicitly.

---

## 10. Provenance

- arXiv `2610.23833` — *Sensory Comfort Across Multisensory XR Prototypes for Autistic Adults* (read in full;
  n = 20; L3 spatial-audio M = 2.97, L5 multi-modal M = 4.43).
- Annals of Dyslexia 2026 — Dyslexie/OpenDyslexic meta-analysis, 15 studies, N = 688, g = −0.04.
- APA 2025 self-affirmation meta-analysis, 67 studies, g = .32; Wood 2009 on backfire.
- 2024 weighted-blanket systematic review, 8 RCTs / 426 participants, SMD 0.40; ADHD sleep RCT n = 94.
- MT-ALEX (d = 0.97 / 1.14); 2026 digital alexithymia RCT n = 47; Dobrushina 2024 haptic interoception.
- JAACAP 2023 CDS renaming; ACN 2023 processing-speed meta (> 1800 people); SSRT +18.8% ADHD / +23.1% ASD.
- 13-article autistic-burnout SR (2026); masking↔stress EMA (2025).
- arXiv `2506.12605` AI companionship; 4-week RCT n = 981; 19/60 harmful-endorsement audit.
- W3C XAUR (REQ 3a/3b, 11a, 12a, 13a) and W3C COGA design patterns.
- Kildahl 2021 and JADD 2026 on the contested PDA construct.

**Expiry.** These figures are trusted for the session that measured them. Re-measure the XR comfort ranking
and the font meta-analysis before quoting them in a shipped claim; both are the kind of reading that gets
overturned by the next cohort.
