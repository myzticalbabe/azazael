DRAFT — NOT SUBMITTED. Every figure below is read from this repository; edit before use.
Question on the page: "How much money do you request for your project? In Euros. ... Please provide a
breakdown clarifying how the requested budget would be used. Which tasks will you undertake, and
(roughly) how much time/effort will each take? What hourly/daily/monthly rate did you use? Will there
be any expenses?"

€50,000 over 12 months: one developer at €45/hour (1,000 hours, €45,000) plus €5,000 fiscal host fee
(10%), and €0 expenses. There is no compute line, deliberately: the system runs on CPU. The realtime
turn is measured at a median 0.025 ms against a 50 ms budget, and the network layer fits a person's
construct graph from 120 observations. The cost of this project is people and ethics review, not GPUs.

1. A labelled corpus from real people — 300 h.
The current corpus is invented utterances, and certification.json refuses to mark that criterion done
for exactly that reason. Work: ethics/IRB submission, consent and withdrawal handling, recruitment,
clinician-rated instruments, and a development/holdout split frozen before any model touches it.
Closes three open certification criteria.

2. An independent recall lower bound for the crisis router — 150 h.
Today the router's recall is published as 0.83 / 0.83 / 0.18 across three holdouts, each scored once,
with the fitted development split (1.00) excluded and not counted. That spread is the finding: 0.18 on
one holdout is not a router yet. Work: write the holdouts and the bound method before running them, so
the number cannot be moved after it has been seen. Closes two open criteria.

3. A human in the loop, built rather than asserted — 250 h.
Escalation queue, an immutable per-turn audit log, a clinician accept/override path, and a test that
fails if any path can reach delivery without passing review.

4. Regulatory classification and scope of practice — 120 h.
A written classification opinion (EU MDR and UK MDR, software as a medical device) and a
scope-of-practice statement, from a consultant with a clinical-safety background. Their fee sits inside
this line. Closes five open criteria across two requirements, and decides whether this project is a
wellness tool or a medical device before anyone else has to guess.

5. Packaging so a reviewer can re-run every number — 100 h.
A reproducible harness, documentation, CI on three operating systems and a first tagged release. The
repository carries 148 test functions today and every one of them is runnable.

6. Reporting and contingency — 80 h.
Grant reporting, bookkeeping, and review of the disclosure gate (DISCLOSURE_POLICY.md refuses to ship
evidence about identifiable people).

What this money does not buy: a claim that the agent is safe to deploy. It buys the measurement that
would let somebody else make that claim. Four of nineteen certification criteria are met today and
fifteen are open, and a criterion closes only by naming a file path in the repository that shows the
evidence.
