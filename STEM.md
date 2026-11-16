# STEM learning guide — azazael

AZAZAEL is a registry of small single-purpose programs ("worms"), a cluster system that runs them, and the harness that records what they did. It is the trunk the other projects in this account grew from.

This guide is for teachers, mentors, club leaders, parents and students who want to
use this repository as a vehicle for real STEM learning — in particular for girls and
other groups still under-represented in computing, engineering and mathematics. It
says what the project actually teaches, how to run a session with it, and what to
remove so that nobody is excluded by accident.

## What this project teaches

**Subject areas**

- distributed systems
- concurrency
- agent architecture
- observability and audit trails

**Skills practised**

- reading a call graph
- designing an isolated unit of work
- reasoning about failure modes
- writing a record that a stranger could check

## Prerequisites

One member of the group needs Python 3.13 or newer installed. A terminal is enough; no editor plugins and no cloud account.

Nothing else is assumed for the entry-level activity below: no prior programming
experience, no particular hardware, and no home internet connection.

## Six practices this repository is set up to support

These follow the published guidance on gender-equitable STEM education — connect the
work to learners' lives, let them investigate real problems, treat struggle as part of
the work, name and challenge stereotypes, make the work collaborative, and put
learners in front of diverse role models.

1. **Connect it to their lives.** every app that runs many small jobs in the background and reports what happened is the same shape as this project, including the ones on the learner's own phone
2. **Let them investigate.** ask each pair to add one worm that lists a directory and classifies what it finds, then predict what the cluster will do before running it
3. **Make struggle normal.** Build the session so that the first attempt is *expected*
   to fail. Say out loud that debugging is the subject, not a penalty. Ask "what did
   that error tell you?" before offering the answer.
4. **Challenge the stereotype.** Name who does this work and why it is not a gendered
   skill. Praise the method ("you isolated the variable"), not the person ("you're a
   natural") — the second kind of praise teaches learners that ability is fixed.
5. **Make it social.** split pairs into a 'registry' role and a 'cluster' role; they have to agree in writing on the contract between them before either writes code
6. **Show diverse role models.** the field's own history: Grace Hopper on compilers, Frances Allen on optimisation, Margaret Hamilton on flight software

## A 90-minute session

1. *(10 min)* Read one worm file together and draw what it touches.
2. *(20 min)* Trace a single run by hand on paper: which component hands what to which.
3. *(45 min)* Each pair writes one new worm and registers it; the group agrees the contract first.
4. *(15 min)* Run everything and compare the audit record with the paper trace.

## Vocabulary to define before the session

Specialist vocabulary is a hidden entry test if nobody explains it. Define each of
these the first time it appears, in one sentence, in the learners' own words:

1. **worm** — one small program with a single job.
2. **registry** — the list that says which worms exist.
3. **cluster** — the part that runs worms and collects results.
4. **audit record** — a line that proves what ran and when.

## Accessibility

Read [ACCESSIBILITY.md](ACCESSIBILITY.md) before running a session. Two rules matter
most in a mixed-ability room:

- Every activity must be completable with a keyboard alone, with a visible focus ring.
- Every instruction names the control or the heading ("the **Run** button in the
  toolbar"), never a colour or a position.

Pair learners rather than singling anyone out, and always offer a text-only route for
a visual step.

## Contributing as a learner

Small, well-scoped contributions are the point, not a consolation prize:

- Browse issues labelled
  [`good first issue`](https://github.com/myzticalbabe/azazael/labels/good%20first%20issue).
- Read [CONTRIBUTING.md](CONTRIBUTING.md) — it has a section written for first-time
  contributors.
- Ask in [SUPPORT.md](SUPPORT.md) if anything is unclear. Asking is expected here; it
  is not a failure.

## Licence and classroom reuse

Classroom, club and workshop use is welcome. See `LICENSE` for the exact terms, and
check whether your institution requires a separate agreement before redistributing
modified copies.
