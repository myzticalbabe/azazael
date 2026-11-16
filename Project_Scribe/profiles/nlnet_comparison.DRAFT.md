DRAFT — NOT SUBMITTED. Edit before use.
Question on the page: "Please compare your own project with other relevant efforts (both existing and
historical). What is new, more thorough or otherwise different? Have you considered contributing to any
of the others?"

Historical: Weizenbaum's ELIZA (1966) demonstrated that a plausible reply is believed whether or not
anything underneath it is doing the work. Nurse Ratchet assumes that effect and grades the machinery
under it. The deliverable is not a chatbot; it is a loop with receipts.

Commercial mental-health chatbots (Woebot, Wysa and similar) are closed systems. From their public
documentation we cannot see a published figure for whether the fast path still agrees with the
deliberate one, a per-reading support count, or a safety branch whose inability to be outbid is a
tested assertion. They may well have all three internally. The point is that a reviewer cannot check,
and on a system that talks to people in crisis, unverifiable is the same shape as absent.

Academic network psychometrics (qgraph, psychonetrics and the wider R ecosystem) fits constructs as
nodes and partial correlations as edges, and does that part better than we do. But it stops at the fit:
there is no realtime loop attached, and no reading that carries its own prototype and support. Our
network layer recovers a planted dependency at partial correlation +0.352 over 120 observations, and
every reading it emits names the prototype it matched and how much support that prototype had.

Open-source agent frameworks give you a loop. What they do not give you is a graded one: repeated
evaluation compiled into prototypes, measured at 8.5 microseconds on the fast path against 148.2
microseconds on the deliberate path, with the same answer, and an agreement() call that reports when
the two diverge. That metric, more than the agent, is the reusable artefact.

What is new here, concretely:
1. Fast/slow agreement as a published number rather than an architectural claim.
2. A safety branch that runs before any stance utility is computed, tested by feeding the loop an
   input that would otherwise select a skills intervention and asserting that it cannot.
3. A certification file in which a criterion flips to done only by citing a path in the repository that
   shows the evidence: 4 of 19 met, with the 0.18 holdout printed next to the 0.83s rather than
   averaged away.

Contributing to others: yes, and preferably upstream. We would ship the agreement metric as a
standalone package that consumes qgraph-style output instead of forking the psychometric tooling, and
the disclosure gate is written as a reusable policy check rather than a feature of this project. If a
maintainer of one of those projects wants the prototype-compilation layer, it is separable by design:
each of the four layers runs and is measured on its own.
