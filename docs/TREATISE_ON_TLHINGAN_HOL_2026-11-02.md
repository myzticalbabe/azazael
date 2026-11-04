# A treatise on `tlhIngan Hol`

### the Klingon language: its design, its grammar, its corpus, and what it costs to translate into it

*Written 2026-11-02. Every grammatical table below is reproduced from reference
material that traces to Marc Okrand's **The Klingon Dictionary** (1985); TKD itself
is not held in this tree, so nothing here is quoted from it. Composed example
sentences are marked as composition. Where a claim would need the book to settle,
the treatise says so instead of guessing.*

---

## I. What kind of object this is

Klingon is an **a priori artistic language** — not a pidgin, not an auxlang, not a
relexification of anything. It was designed to be spoken by a fictional species and
to *sound* unlike human language. Its sound and about a dozen words were devised by
James Doohan and Jon Povill for *Star Trek: The Motion Picture* (1979). The grammar
was commissioned from **Marc Okrand** for *Star Trek III: The Search for Spock*
(1984), and published in **The Klingon Dictionary** in 1985.

It is **regulated**, and by one person. The Klingon Language Institute and most
practitioners recognise only forms introduced by Okrand as canonical. This has three
consequences that matter more than the grammar:

- **Authority is citation, not usage.** There is no native community to ratify a
  change. A new coinage is not "wrong" in the way a foreigner's error is wrong; it is
  *unauthorised*, which is a different failure with a different remedy.
- **The canon has a shape.** Okrand added vocabulary on request over decades, so the
  lexicon is denser in some semantic fields than others, and the gaps are historical
  accidents, not design. The classic example: a word for a ship's bridge (`meH`)
  existed almost from the start, while a word for a bridge over water (`QI`) was not
  known until **2012**.
- **Design constrains translation.** Okrand deliberately avoided typologically common
  patterns. A text that translates smoothly into Klingon by ordinary means is
  probably not Klingon; the friction is the design.

Its ISO 639 code is `tlh` (both -2 and -3); Glottolog classifies it as `klin1234`.

---

## II. Phonology — the inventory, and why the alphabet looks broken

Klingon has **21 consonants and 5 vowels**. The consonant inventory is deliberately
asymmetric: there are **no velar plosives**, only one sibilant fricative, and the
common consonants `/k ɡ f h s z ʃ/` are all absent. Retroflex and uvular places of
articulation carry much of the "alien" effect.

| letter | IPA | note | letter | IPA | note |
| --- | --- | --- | --- | --- | --- |
| `'` | /ʔ/ | glottal stop — **a consonant**, not punctuation | `p` | /pʰ/ | aspirated |
| `b` | /b/ | | `q` | /qʰ/ | aspirated uvular |
| `ch` | /t͡ʃ/ | | `Q` | /q͡χ/ | affricate, **distinct from `q`** |
| `D` | /ɖ/ | retroflex | `r` | /r/ | trill |
| `gh` | /ɣ/ | | `S` | /ʂ/ | retroflex |
| `H` | /x/ | | `t` | /tʰ/ | aspirated |
| `j` | /d͡ʒ/ | | `tlh` | /t͡ɬ/ | lateral affricate |
| `l` | /l/ | | `v` | /v/ | |
| `m` | /m/ | | `w` | /w/ | |
| `n` | /n/ | | `y` | /j/ | |
| `ng` | /ŋ/ | | | | |

Vowels: `a` /ɑ/, `e` /ɛ/, `I` /ɪ/, `o` /o/, `u` /u/. Diphthongs are written
`ay`, `ey`, `Iy`, `oy`, `uy`.

**The uppercase letters are not capitals.** `D H I Q S` are separate letters whose
lowercase forms do not exist in the alphabet, because Okrand needed 21 letters from a
26-character keyboard and reserved the odd cases for sounds English readers would
otherwise flatten. This makes the orthography **case-sensitive**, and it has exactly
one true minimal pair: **`Qat`** *be popular* against **`qat`** *accompany*. Every
other case distinction is a spelling rule rather than a lexical contrast, but the
rule is strict — `hol` is not a word; `Hol` *language* is.

Two further portability traps, both structural rather than stylistic:

- **The apostrophe is a letter.** `'` is /ʔ/, so a text pipeline that treats `'` as
  quoting will corrupt Klingon silently.
- **`tlh` and `ng` are single consonants**, so naive syllable-splitting misreads
  every word containing them.

Stress: **not asserted here.** TKD describes it; the orthography does not mark it;
the book is not held. A learner should take stress from the dictionary rather than
from a secondary table. This treatise would rather have a gap than a plausible error.

---

## III. Morphology

Klingon is **agglutinative and almost entirely suffixing**, with a small closed set
of prefixes on the verb. Its morphology is *extremely regular* — the irregularity in
the language is in the inventory and the word order, not in the inflection.

### III.1 Nouns and their three classes

Every noun belongs to one of three classes, and the class decides which plural and
which possessive you may use:

1. **beings capable of language** — people, gods, talking entities;
2. **body parts** (but not the body itself);
3. **everything else.**

There are no articles. `raS` is *table* or *the table* or *a table*; context decides.

Noun suffixes come in **five types**, applied in type order, and a word may carry at
most one suffix of each type. The canonical demonstration is
`vengHommeyqoqchajDaq` — *in their so-called villages* — which uses all five:

| type | function | suffixes | example |
| --- | --- | --- | --- |
| 1 | size, affection | `-'a'` augmentative, `-Hom` diminutive, `-oy` endearment | `ghom` group → `ghom'a'` crowd; `yuQ` planet → `yuQHom` planetoid; `vav` father → `vavoy` daddy |
| 2 | plural (by class) | `-pu'` language-users, `-Du'` body parts, `-mey` other | `qetwI'pu'` runners; `ghopDu'` hands; `quSmey` chairs |
| 3 | speaker's accuracy | `-qoq` so-called, `-Hey` apparent, `-na'` genuine | `QaHqoq` the so-called help; `jupna'` true friend |
| 4 | possession, determiners | `-wIj -lIj -Daj -maj -raj -chaj` (non-language-users); `-wI' -lI' -ma' -ra'` (language-users); `-vam` this, `-vetlh` that | `navwIj` my paper; `qeSwI'pu'lI'` your advisors; `Sojvam` this food |
| 5 | syntactic role | `-Daq` locative, `-vo'` ablative, `-mo'` causal, `-vaD` dative/benefactive, `-'e'` topic | `juHmajDaq` in our home; `qojvo'` away from the cliff; `je'wI'vaD` for the buyer |

Two asymmetries are worth naming because they are what a translator trips on:

- **`-mey` on a language-user is not a neutral plural.** `ghotmey` does not mean
  "people"; it means *people scattered all over the place*. The class system is
  semantic, so the "wrong" plural is a different claim, not a mistake.
- **Plural is optional when something else says it is plural** — a pronoun, a prefix,
  or a number. `Duy chaH` and `Duypu' chaH` both mean *they are emissaries*. English
  obligatorily marks plural; Klingon does not, and a translator who marks it every
  time produces a text that over-asserts.

### III.2 The verb: prefixes carry the clause

This is the single hardest part of the language and the reason machine translation
fails on it. **A prefix encodes both subject and object**, so the verb does not merely
agree — it *is* the clause's argument structure.

| subject ↓ / object → | none | me | you | him/her/it | us | you (pl) | them |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **I** | `jI-` | — | `qa-` | `vI-` | — | `Sa-` | `vI-` |
| **you** | `bI-` | `cho-` | — | `Da-` | `ju-` | — | `Da-` |
| **he/she/it** | `Ø-` | `mu-` | `Du-` | `Ø-` | `nu-` | `lI-` | `Ø-` |
| **we** | `ma-` | — | `pI-` | `wI-` | — | `re-` | `DI-` |
| **you (pl)** | `Su-` | `tu-` | — | `bo-` | `che-` | — | `bo-` |
| **they** | `Ø-` | `mu-` | `nI-` | `lu-` | `nu-` | `lI-` | `Ø-` |
| **unspecified** | `Ø-` | `vI-` | `Da-` | `Ø-` | `wI-` | `bo-` | `lu-` |

Imperatives have their own set: `yI-` (do it), `HI-` (do it to me), `gho-` (do it to
us), `tI-` (do it to them), `pe-` (you-pl, no object).

Three facts fall out of that table, and each is a wall for a translator:

1. **There is no separate pronoun requirement.** `vIlaD` already means *I read it*.
   Adding a pronoun is not wrong but it is emphatic, and a transfer that renders
   "I" every time produces a text that shouts.
2. **Third person is a zero prefix.** So a bare verb with no prefix is a
   third-person statement — which is why `paq QaQ` (*the book is good*) needs no
   copula and no "is".
3. **`-lu'` is not a passive.** It marks an *indefinite subject* and the ordinary
   prefixes then indicate the object: `vItlha'lu'` is *someone chases me*, with `vI-`
   still pointing at the object. English has no construction that maps cleanly, which
   is why "it was written" is one of the hardest short sentences to translate well.

### III.3 The verb: nine suffix types and the rovers

Verb suffixes are ordered in **nine types**, plus a class of **rovers** that may sit
between types. Aspect lives here; tense does not.

| type | function | suffixes |
| --- | --- | --- |
| 1 | reflexive / reciprocal | `-'egh` self, `-chuq` each other |
| 2 | volition, necessity | `-nIS` need, `-qang` willing, `-rup` prepared, `-beH` set up to (devices), `-vIp` afraid to |
| 3 | change of state | `-choH` become/begin, `-qa'` resume, do again |
| 4 | causative | `-moH` cause |
| 5 | indefinite subject, capability | `-lu'` someone, `-laH` can |
| 6 | speaker's certainty | `-chu'` perfectly, `-bej` certainly, `-law'` seems, `-ba'` obviously |
| 7 | **aspect** | `-pu'` perfective, `-ta'` perfective **and deliberate**, `-taH` continuous, `-lI'` continuous toward an end |
| 8 | honorific | `-neS` |
| 9 | syntactic | `-wI'` agentive, `-ghach` nominaliser, `-'a'` yes/no question, `-jaj` optative, subordinators `-pa' -vIS -DI' -meH -bogh -chugh -mo'` |

Rovers include negation `-be'`, emphasis `-qu'`, and reversal `-Ha'`.

**Aspect is not tense.** `-pu'` says the action is completed *in the time frame of the
sentence* — past, present or future. `qaS` *it occurs*; `qaSpu'` *it has occurred*.
The distinction between `-pu'` and `-ta'` is **intent**: `vIghorpu'` *I have broken it*;
`vIghorta'` *I have broken it on purpose*. Whole translation decisions turn on that
suffix, and it is the one most often mistranslated by a system that reads "-ta'" as
"past tense".

Two derived forms worth knowing:

- **`-wI'`** makes an agent noun — `'IjwI'` *listener*, and by the same rule
  `qetwI'` *runner*. It attaches to verbs, so a Klingon agent noun states what the
  person *does*, never what they *are*.
- **`-ghach`** nominalises a verb *that already carries suffixes*, which otherwise
  cannot be nominalised: `QallaHghach` *the ability to swim*.

Causation is productive enough to be a word-formation strategy:
`Say'` *be clean* → `Say'moH` *clean* (cause to be clean).

---

## IV. Syntax

**Order is object–verb–subject.** Not SVO with a quirk: the object comes first.

> `Do' DujDaq ghoqwI' Sam la'`
> fortunately / ship-LOC / spy / find / commander
> *Fortunately, the commander found the spy aboard the ship.*

Adverbs go sentence-initial; prepositional phrases go **before the object**, not after
the verb (Klingon has no prepositions — it has noun suffixes, so "aboard the ship" is
`DujDaq`, a suffixed noun).

**There is no copula.** A noun and an adjective, or two nouns, form a sentence:
`paq'a' QaQ` *the big book is good*. English "is" has no counterpart to translate;
it has to be *removed*.

**Clauses as objects take `'e'`.** A whole sentence can be the object of the next, and
`'e'` stands in for it:

> `bIpIv 'e' vItu'`
> you-are-healthy / that / I-it-observe
> *I see that you are healthy.*

**Relative clauses precede their head**, marked with `-bogh` on the verb:
`qonbogh to'maS` *Thomas who composed*. English postmodifies; Klingon premodifies.
This single rule reverses the word order of every relative clause in a translated
text, which is why relexified Klingon reads as though the sentences were built
backwards — because they were.

**Purpose uses `-meH`**, whose clause precedes the main clause: `jItlheDpa', HIboQ`
*before I depart, assist me* shows the same shape with `-pa'` (*before*).

**Subordination is suffixial**, not conjunctional: `-pa'` before, `-vIS` while (with
`-taH` on the same verb), `-DI'` as soon as, `-chugh` if, `-mo'` because.

**Questions.** A yes/no question adds `-'a'`: `DIboQnIS'a'` *do we need to assist
them?* The optative `-jaj` marks a wish: `bIQapjaj` *may you succeed*. The canonical
Klingon greeting is itself a question — `nuqneH`, literally *what do you want?* —
which is a fact about the culture carried in the grammar.

**Pronouns** are few and are used for emphasis or where the prefix cannot carry the
reference: `jIH` I, `SoH` you, `ghaH` he/she, `'oH` it, `maH` we, `tlhIH` you-pl,
`chaH` they. **Numbers**: `wa' cha' wej loS vagh jav Soch chorgh Hut maH` (1–10).

---

## V. Lexicon and semantics

The lexicon was built for a fiction and then extended for use, and the seam shows.

- **Dense fields**: warfare, honour, command, shipboard life, insult, ceremony.
- **Sparse fields, filled late**: domestic life, food, emotion vocabulary, ordinary
  landscape terms. `QI` *bridge over water* arriving in 2012 is the emblem.
- **The consequence for translation**: a text dense in abstract nouns and ordinary
  objects will hit lexical gaps long before it hits grammatical ones. The temptation
  is to invent a compound. Klingon compounding is real, but a coinage is
  unauthorised and must be labelled as such.

Semantically, Klingon prefers **verbs to adjectives** (`QaQ` is *be good*, a verb) and
**actions to states**. That is a design choice with a translational cost: English
sentences built on "is" plus an adjective must be rebuilt around a verb, and every
rebuild is a place where meaning can drift.

---

## VI. Writing

Klingon is normally written in a **case-sensitive Latin transliteration**. That is
what the corpus, the dictionaries and the KLI use, and it is what a text file should
contain.

A native-looking script, **`pIqaD`**, exists and is used on screen and in licensed
products (the 2011 Talk Now! course was the first language course printed in it). Two
things about it matter practically:

- **It is not the language.** Klingon is not written in `pIqaD` the way English is
  written in Latin letters; the script is a presentation layer over the same
  transliteration.
- **It is encoded in Unicode's private-use area** (the CSUR convention), not in the
  standard planes. Text in `pIqaD` therefore does not reliably survive copy-paste,
  search, or most toolchains. Ship the transliteration; treat the script as artwork.

The on-screen glyphs in the series were largely decorative, designed as set dressing;
the correspondence between glyph and sound was standardised later by the community,
not by the production. Any claim that Okrand designed a native writing system should
be treated as false until a citation says otherwise.

---

## VII. The corpus

| work | note |
| --- | --- |
| **The Klingon Dictionary** (1985; expanded 1992) | grammar and lexicon; the canon |
| **The Klingon Way** (1996); **Klingon for the Galactic Traveler** (1997) | idiom, culture, added vocabulary |
| ***Hamlet*** (2000) | translated by Nick Nicholas; the proof that the language can carry Shakespearean register |
| **`ghIlghameS`** | the Epic of Gilgamesh |
| **`paghmo' tIn mIS`** | Much Ado About Nothing |
| **`pIn'a' qan paQDI'norgh`** | Tao Te Ching — `paQ` *teach*, not `paq` *book* |
| **`Sun pIn'a' veS mIw`** | The Art of War |
| **`ta'puq mach`**, **`QelIS boqHarmey`**, **`poH jan`**, **`'aS 'IDnar pIana' Duna`**, **`chIjwI' tIQ bom`** | The Little Prince, Alice, The Time Machine, Wizard of Oz, Ancient Mariner |
| **the opera `'u'`** | entirely in Klingon |
| ***A Klingon Christmas Carol*** | first production primarily in Klingon; only the narrator speaks English |
| **KLI Religious Text Translation Project** (1994– ) | ~30 biblical documents; Mark by Nick Nicholas; see `docs/FRANCHISE_BIBLES_STARWARS_STARTREK.md` Part III |
| **the KLV** | a complete Bible *relexification*, by its author's own description not a translation |

The corpus is what makes Klingon more than a curiosity: it is large enough that
questions of register, verse and idiom have actual precedent, and small enough that a
newcomer can read most of it.

---

## VIII. What translation into Klingon actually costs

Four walls, each a table above, each fatal to word-for-word transfer:

1. **The prefix is the clause** (§III.2). You cannot place words and then inflect;
   the prefix choice *is* the argument structure. Reordering a transferred sentence
   leaves the wrong prefix on the verb, which does not parse.
2. **Order is OVS, with PPs before the object** (§IV). Every clause inverts.
3. **Aspect replaces tense; there is no infinitive** (§III.3). English auxiliary
   stacks have no morpheme targets, only constructions.
4. **There is no passive** (§III.2). "It was built" must become *someone built it*,
   with `-lu'`.

A fifth, lexical: **relatives precede their heads** (§IV), so every `-bogh` clause is
built in the opposite direction from English.

### A graded demonstration

Each line is **my composition**, checked pattern by pattern against the tables above.
Nothing here is a quotation, and the grade says what a reader may do with it.

| # | Klingon | morphemes | English | grade |
| --- | --- | --- | --- | --- |
| 1 | `paq vIlaD` | book / I-it-read | I read the book | **G2** — OVS + `vI-` |
| 2 | `paq vIlaDnIS` | … / need | I need to read the book | **G2** — type-2 suffix |
| 3 | `paq vIlaDtaH` | … / continuous | I am reading the book | **G2** — aspect, not tense |
| 4 | `paq vIlaDpu'` | … / perfective | I have read the book | **G2** |
| 5 | `paq vIlaDta'` | … / perfective+deliberate | I have read the book (on purpose) | **G2** — the intent claim |
| 6 | `paq vIlaDbe'` | … / not | I do not read the book | **G2** — rover |
| 7 | `paq DalaD'a'` | book / you-it-read / Q | do you read the book? | **G2** |
| 8 | `paq qonlu'pu'` | book / someone-composed / perf | the book has been composed (by someone) | **G2** — `-lu'`, not a passive |
| 9 | `qonbogh to'maS` | composed-who / Thomas | Thomas, who composed (it) | **G2** — relative precedes head |
| 10 | `paq laDmeH jIghoj` | book / read-in-order-to / I-learn | I learn in order to read the book | **G2, lexically open** — `-meH` is right; whether `ghoj` takes this complement is a Klingonist's call |
| 11 | `paq QaQ` | book / be-good | the book is good | **G2** — no copula |
| 12 | `nuqneH` | what / you-want | what do you want? (the greeting) | **attested** |

The point of the table is row 8 next to row 7 and row 9 next to row 3: the grammar
*forces* choices that English leaves implicit (who acts on what; whether it was
deliberate; whether there was an agent at all). A translated text that does not show
those choices is not translating; it is substituting.

### The fidelity ladder

| grade | what it is | who can produce it |
| --- | --- | --- |
| **G0** | gloss sheet — attested terms, no sentences | anyone with a dictionary |
| **G1** | relexification — target words, source syntax | a word list, or a language model |
| **G2** | composed and checked against the tables, labelled as composition | a careful learner |
| **G3** | signed by a Klingonist | a Klingonist |

The KLV is G1 at the scale of a whole Bible. The RTTP is G3 by construction. Anything
a machine produces without review is G1 with better spelling, and saying so is the
only honest label available.

---

## IX. An order of study, and why

1. **Phonology and the alphabet**, including the case rule and the apostrophe. Cheap,
   and it prevents every subsequent error of transcription.
2. **Noun suffix types 1–5 in order.** The chain `vengHommeyqoqchajDaq` is the whole
   system in one word; learn it and the noun is done.
3. **The verb prefix table.** The hard part, and the part that repays memorisation
   most: nine productive prefixes plus the imperatives carry every clause.
4. **Aspect (type 7) before anything lexical.** `-pu'` / `-ta'` / `-taH` / `-lI'`
   decide what a sentence claims about time and intent.
5. **Syntax: OVS, no copula, `'e'`.**
6. **Relatives and purpose** (`-bogh`, `-meH`), because they invert.
7. **Read the canon.** TKD, then *The Klingon Way* for idiom. A learner who reads
   only secondary tables learns a language that resembles Klingon.

---

## X. Limits of this treatise

- **TKD is not held.** Every table is reproduced from reference material that cites
  it. The tables are consistent and internally checkable; they are not quotations.
- **No Klingonist has reviewed the composed rows.** They are G2 by my own grading,
  which is exactly the grade a careful non-expert can claim and no more.
- **Stress is not described** (§II) for the same reason.
- **The `pIqaD` mapping is not verified here.** The treatise asserts only what is
  safe: it is a presentation layer, privately encoded, and not the language itself.
- **No claim is made about the KLV's text**, only about its self-description. Reading
  one verse beside its English source would settle the argument better than any
  description of it.

---

## Sources

| source | tier | state |
| --- | --- | --- |
| kli.org Religious Text Translation Project | **A** | **R** — project history, census, Klingon titles |
| Wikipedia *Klingon language* | **C** | **R** — history, phonology, canon policy, corpus, speakers, copyright |
| Wikipedia *Klingon grammar* | **C** | **R** — noun/verb suffix and prefix tables (trace to TKD) |
| crosswire SWORD `KLV` metadata; klingonword.org | **B** | **R** — relexification, "not properly a translation" |
| Okrand, *The Klingon Dictionary* (1985/1992) | **A** if held | **not held** |

*Companion documents: `docs/KLINGON_BIBLE_ACCURACY_2026-11-02.md` (the audit that
produced the corrections), `docs/KLINGON_LANGUAGE_WHITEPAPER_2026-11-02.md` (the
decision paper).*
