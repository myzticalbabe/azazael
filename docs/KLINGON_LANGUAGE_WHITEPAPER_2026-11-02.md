# Klingon as a translation target — whitepaper

**Question this paper answers.** When a system produces text in Klingon
(`tlhIngan Hol`), what has it actually produced, how would anyone know, and what
should this tree require before such text is shipped or quoted?

**Short answer.** Klingon is a *regulated* constructed language with one author of
record, a real corpus, and a hard structural wall between "glossed English" and
"Klingon". The wall is not vocabulary — it is grammar that cannot survive
word-for-word transfer. The most complete Klingon Bible in existence is, by its own
author's description, **not a translation**, and that single fact is the best
available evidence for how this failure happens at scale. The recommendation is a
**fidelity grade on every Klingon string**, in the same way this tree already
requires a generated file to declare the source it was generated from.

Evidence and line-level checks: `docs/KLINGON_BIBLE_ACCURACY_2026-11-02.md`.
Language reference: `docs/TREATISE_ON_TLHINGAN_HOL_2026-11-02.md`.

---

## 1. The object

Klingon is an *a priori* artistic language, created for the Star Trek franchise.
Its sound and a dozen words were devised by James Doohan and Jon Povill for *Star
Trek: The Motion Picture* (1979); the language proper was commissioned from **Marc
Okrand** for *Star Trek III* (1984) and described in **The Klingon Dictionary**
(1985). Okrand remains the authority: the Klingon Language Institute and most
practitioners treat **only forms introduced by Okrand as canonical**.

Three properties follow, and each has a cost:

1. **One author of record.** There is no native speech community to settle disputes.
   Canonicity is a citation question, not a usage question. A novel coinage is not
   wrong so much as *unauthorised*, which is a different kind of wrong.
2. **A designed dissimilarity to human languages.** Okrand deliberately chose
   typologically rare features — 21 consonants with conspicuous gaps,
   object–verb–subject order, person agreement by prefix. This is why the language
   is hard for a machine to fake convincingly and easy to fake plausibly.
3. **A lexicon built for a fiction, then extended for use.** Early vocabulary was
   dense in spacecraft and warfare; everyday terms arrived late and by request. The
   canonical example: a word for *bridge* in the ship sense (`meH`) existed from near
   the beginning, while *bridge* as a structure over water (`QI`) was not known until
   2012.

## 2. The corpus, measured

What exists, as of the sources read on 2026-11-02:

| corpus | content | status |
| --- | --- | --- |
| Okrand, *The Klingon Dictionary* (1985; expanded 1992) | grammar + lexicon, the canon | the authority; **not held in this tree** |
| Okrand, *The Klingon Way* (1996), *Klingon for the Galactic Traveler* (1997) | idiom, culture, added lexicon | canon |
| Literary translations | *Hamlet*; `ghIlghameS` (Gilgamesh); `paghmo' tIn mIS` (Much Ado); `pIn'a' qan paQDI'norgh` (Tao Te Ching); `Sun pIn'a' veS mIw` (Art of War); `ta'puq mach` (The Little Prince); `QelIS boqHarmey` (Alice); `poH jan` (The Time Machine); `'aS 'IDnar pIana' Duna` (Wizard of Oz); `chIjwI' tIQ bom` (Ancient Mariner) | ≥10 published; *Hamlet* and Mark by Nick Nicholas |
| KLI **Religious Text Translation Project** | ~30 biblical and related documents; 2 Old Testament books complete (Jonah, and Mark/Luke-class NT books), 18 NT epistles complete, Gospel of Thomas complete, Mormon and LDS hymnal in progress | the largest single translation effort; census public |
| Drama / music | the opera `'u'`; *A Klingon Christmas Carol* | performed |
| Teaching | Duolingo course (beta 2018); Talk Now! *Learn Klingon* (2011, first course in `pIqaD`); KLI lessons | live |
| Machine translation | Bing Translator | documented as failing on prefix/suffix morphology |

**Speaker numbers are small and old.** "Around a dozen fluent" (Schoen, 1996);
"20–30" (Okrent, 2009). Any claim that Klingon is widely spoken is a claim about
fandom, not about speakers.

## 3. The failure mode, named by the project that committed it

The **Klingon Language Version** (KLV) of the World English Bible is complete,
published, and readable. Its own metadata says it is:

> "an experimental **relexification** of the WEB. It is **not properly a
> translation**, but a demonstration of what a `tlhIngan Hol` text might look like."
> — SWORD module `KLV` description; same wording on the author's "Why a Klingon
> Bible?" page

Relexification means: keep the English syntax and semantics, substitute Klingon
words. The output is *lexically* Klingon and *structurally* English. It is the
conlang equivalent of a 3D translation that carries the pixels and not the rules —
the surface is transported, the structure is not.

This matters beyond the KLV because it is the **exact output shape of a language
model** asked to "write it in Klingon". Fluency in the target is not required to
produce it; only a word list is. The KLV is therefore the control group for every
future claim that a machine has translated something into Klingon.

## 4. Four structural walls

Each of these makes word-for-word transfer not merely clumsy but ungrammatical.
Each is a table in the reference grammar, which is why the wall is checkable.

**(a) The verb prefix encodes the object.** Klingon marks subject *and* object on the
verb with a single prefix. English "I read the book" is four words; Klingon is two —
`paq vIlaD` (*book I-it-read*) — because `vI-` already says "I, acting on it".
Transfer English order and you get the subject prefix on an object-bearing clause,
which does not parse. There is no "I read" plus a separate object; the prefix choice
is the grammar.

**(b) Order is OVS.** Object first, verb, then subject. A transfer preserves SVO and
inverts every clause. Adverbs go sentence-initial and prepositional phrases precede
the object, so the inversion is systematic, not local.

**(c) Aspect is not tense, and there is no infinitive.** `-pu'` and `-ta'` are
perfective — completed within the time context — and the second adds *deliberately*.
Tense is carried by context and time adverbs. English "will have been going to" has
no morpheme-by-morpheme target; it has a construction, and a transfer that reaches
for auxiliaries invents grammar.

**(d) The passive does not exist.** English "it was built" must become an indefinite
subject: `qonlu'pu'` — *someone composed it*, with `-lu'`. `-lu'` is not a passive;
it makes the subject indefinite and leaves the object where it was. A relexifier
either invents a passive or reaches for the pronoun `'oH`, and both are wrong in
different ways.

A fifth wall is lexical rather than structural: relative clauses **precede** their
head and are marked on the verb with `-bogh`, so "Thomas who composed" is
`qonbogh to'maS`. English postmodifies; Klingon premodifies. Every relative clause
in a transferred text is backwards.

## 5. What fidelity would mean, as a ladder

The useful output of this paper is not "Klingon is hard". It is a grade, so that a
reader can tell what they are holding:

| grade | name | test | who can produce it |
| --- | --- | --- | --- |
| **G0** | gloss sheet | attested words, no sentences; each term traceable to canon | anyone with a dictionary |
| **G1** | relexification | target words, source syntax; *looks* translated | a word list, or a language model |
| **G2** | composed and checked | every clause checked against the prefix/suffix tables; composition labelled as composition | a careful learner, with the tables open |
| **G3** | signed translation | a Klingonist has read it and put their name on the choices | a Klingonist |

The KLV is **G1 at full Bible scale**. The RTTP is **G3 by construction** — it is
coordinated, attributed per book, and its titles show deliberate grammatical
choices (Luke's `qonta'bogh` with `-ta'` *deliberately* against Thomas's bare
`qonbogh`). §III.3a of the franchise dossier is **G2**, and says so per row.

**Completeness is not fidelity.** A finished book proves a translator stopped, not
that the result reads as Klingon. Grade and completeness are orthogonal axes, and
collapsing them is how the KLV's 66 books get cited as evidence the language
"handles" scripture.

## 6. Recommendations

**R1 — Every Klingon string in the tree carries a grade.** G0–G3, with the source
it is traceable to. An ungraded string is a defect, for the same reason an
unattributed number is: it asserts fidelity it has not demonstrated. This mirrors
`bible_check.py --check`, where a generated file must be current with its source or
the gate fails.

**R2 — Machine output is never labelled a translation.** It may be labelled
*composition* (G2) or *relexification* (G1). The KLV's own honesty is the standard:
it publishes under a description that says what it is not.

**R3 — Quote canon, never paraphrase it.** Klingon has one author of record. A
paraphrase of an Okrand form is a coinage wearing a citation, and the citation will
not survive checking.

**R4 — Do not extend the census as if it were coverage.** "The RTTP has done 18
epistles" is a fact about a project's progress. "Klingon can carry Pauline
theology" is a claim that requires reading the translations. Keep them apart.

**R5 — Treat `pIqaD` as an encoding risk, not a font choice.** The script is
encoded in Unicode's private-use area (CSUR) rather than in the standard planes, so
text in `pIqaD` does not survive copy-paste, search, or most toolchains. Ship the
Latin transliteration; treat the script as presentation. Note also that the
transliteration is **case-sensitive** and uses the apostrophe as a *consonant*
(`'` = /ʔ/), both of which break naive text handling — this is documented as the
reason the Duolingo course declined to leave beta.

## 7. Legal note, stated because it is load-bearing for reuse

CBS holds copyright in the official dictionary and canonical descriptions of the
language. A constructed language is generally treated as a protected creation, while
a natural language is not; dictionary *entries* are facts and not copyrightable, but
formatting, example sentences and usage notes are. Practical consequence: quoting a
Klingon sentence with attribution is ordinary citation; redistributing a lexicon or
a dictionary's apparatus is not.

## 8. Open questions

1. **TKD is not held in this tree.** Every grammar claim above is consistent with
   reference tables that cite it, not quoted from it. A claim that decides anything
   should be checked against the book.
2. **No Klingonist has reviewed any composition produced here.** G2 is a ceiling
   until one does.
3. **The KLV text itself has not been read.** The paper quotes its self-description
   and not its verses; showing one verse beside its English source would convert the
   argument from description to demonstration.

---

## Sources

| source | tier | state |
| --- | --- | --- |
| kli.org Religious Text Translation Project | **A** | **R** — dates, coordinators, secular rationale, census, titles |
| crosswire SWORD `KLV` metadata; klingonword.org "Why a Klingon Bible?" | **B** | **R** — relexification, "not properly a translation" |
| Wikipedia *Klingon language*, *Klingon grammar* | **C** | **R** — phonology and morphology tables, canon policy, corpus list |
| Okrand, *The Klingon Dictionary* | **A** if held | **not held** |
