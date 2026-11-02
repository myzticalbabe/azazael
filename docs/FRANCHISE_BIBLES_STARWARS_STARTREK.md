# The franchise bibles: Star Trek, Star Wars, and the Klingon edition

A dossier on how each franchise states its own creative law — theme, situation, character,
prose — and what a Klingon-language edition of that material actually is.

Every claim below carries a **tier** and a **retrieval state**, because the honest distinction
here is not "true/false" but "I read the document" versus "I read a page that describes the
document" versus "the URL is recorded and the fetch was refused":

- **A** — primary document, fetched and read in this session.
- **B** — official archive/index entry for a primary document (catalogue record, item metadata).
- **C** — credible secondary source that describes a primary document.
- **D** — snippet, forum post, or hearsay: pointer only, never load-bearing.
- **R** — **retrieved**, text in hand. **P** — **pointer**: URL recorded, fetch refused or
  returned a reader shell instead of text.

Two fetches were refused and are recorded as such rather than paraphrased from memory:
`bu.edu/clarion/guides/Star_Trek_Writers_Guide.pdf` → **404**, and
`tvwriting.co.uk/tv_scripts/TV_Bibles/Star_Trek_Writers_Guide.pdf` → **403**.

**Corrected 2026-11-02, later the same session.** The earlier note in this file said the
`archive.org` `_djvu.txt` endpoint returned a reader shell and that no bible prose was quoted.
That was a defect of the *request*, not of the archive: the filename is not `<id>_djvu.txt`, it
is the item's own title with spaces (`Star Trek The Next Generation Writers Guide_djvu.txt`).
The right way to get it is to ask `https://archive.org/metadata/<id>` for the file list and use
the `name` it returns. Doing that returned **81,641 bytes of text** (md5
`64f473b0c215ec917aa61e7b196decf8`) for the **Star Trek: The Next Generation Writer/Director's
Guide, Gene Roddenberry, March 23, 1987**. **§I.5 and §I.6 below quote from it directly, tier
A, retrieved.** The 1967 third revision is still not in hand: its prose is described, never
quoted.

---

## Part I — Star Trek: the bible as a studio instrument

### I.1 Lineage (what the document is, dated)

| date | document | tier | state |
| --- | --- | --- | --- |
| 1964-03-11 | **"Star Trek is…"** — Roddenberry's original pitch | C | P |
| 1966-02 | NBC picks up the series; the pitch becomes the guide's **"Second Revision"**, folding in changes between "The Cage" and "Where No Man Has Gone Before" | C | P |
| 1967-04-17 | **"Third Revision"**, updated and expanded by **D.C. Fontana**, with new character material — the version production staff and (through Lincoln Enterprises) fans received, and the one that became known as **"The Writer's Bible"** | C | P |
| 1967 | *The Star Trek Guide*, 31-page Norway Productions booklet for writers, sold by Lincoln Enterprises from 1967 | C | P |
| 1987-03-27 | ***Star Trek: The Next Generation* Series Bible, Season One**, by **David Gerrold** with Roddenberry | **B** | P (item metadata read) |
| 1987 | *TNG Writer/Director's Guide* — scanned by tvwriting.co.uk, OCR'd on archive.org | **B** | P |
| 2018-01-23 | *The Trek Files* 1-01 discusses the **April 1967** guide and its **"believability factor"** doctrine | C | R (episode description) |

Sources: Memory Alpha, "The Star Trek Guide (production document)" — **C, R**,
<https://memory-alpha.fandom.com/wiki/The_Star_Trek_Guide_(production_document)>; Fanlore,
"The Star Trek Guide (1967 official publication)" — **C, P**,
<https://www.fanlore.org/wiki/The_Star_Trek_Guide_(1967_official_publication)>; Internet
Archive item `star-trek-the-next-generation-bible` (**B, R**),
<https://archive.org/details/star-trek-the-next-generation-bible>; item
`star-trek-the-next-generation-writers-guide` (**B, P**).

Two facts from that record are worth more than the rest, because they define *what kind of
document a bible is*:

1. **A bible is a revision, not a revelation.** The Star Trek guide's authority came from being
   re-issued: pitch → second revision → third revision. Each edition absorbed what the previous
   one had got wrong on screen. That is a changelog with a myth attached.
2. **A bible is written by more than its credited author.** Roddenberry's name is on it; the
   edition everyone actually used was Fontana's. The document's real authorship is the
   production's accumulated corrections.

### I.2 Theme — how a Star Trek bible states a theme

The recurring structure across editions is a **thesis plus a prohibition**: what the show is
*for*, and the specific failures that will get a script rejected. The documented centre of that
thesis is the **"believability factor"** (per the April 1967 guide as discussed in *The Trek
Files*, **C**): a story is admitted when its science-fictional premise is a thin, plausible
sheet over a human problem, and rejected when the premise is the point.

An honest summary of the theme, in the guide's own logic rather than its wording, since the
wording is **P**:

- the future is a **workplace**, not a utopia tour — the ship is a job;
- conflict is **procedural and moral** before it is military;
- the alien is a **mirror**, never merely a monster;
- the ending is a **decision**, not a battle — the captain chooses, and the choice is argued.

### I.3 Situation — the shape of an episode

The guide's situation logic is a **formula with slots**, which is what made it teachable to
freelancers:

- **teaser** that poses a violation of the normal order (a distress call, an anomaly, a breach);
- **act structure** carrying two threads — a **ship problem** and a **person problem** — that
  must resolve through the same decision;
- the **alien-of-the-week** as the test case for a contemporary question, never the question
  itself;
- a **closing beat** that returns the crew to routine, so the next episode starts clean.

TNG's 1987 bible is where that formula is written most explicitly as a *format* document
(series premise, regulars, standing sets, what a freelance submission must contain) — **B**, not
read here. Its metadata alone (Gerrold, 1987-03-27, 600 ppi OCR scan, 51.5 MB) establishes the
document's scale: this is not a memo, it is a manual.

### I.4 Character — functions first, persons second

Both the 1967 and 1987 editions spend their longest sections on **regulars**, and the reason is
structural: a bible's job is to let a stranger write your characters without breaking them. The
documented consequence is that characters are described as **functions with a voice** — what
each one is *for* in an argument — and only then as biography.

The most-quoted instance of this (analysis, widely repeated, **not verified in a fetched
document** here) is the command-trinity reading of *Star Trek*: the captain as decision, the
science officer as detached reason, the doctor as the objection. Treat that as *received
interpretation*, **C/U**, not as the guide's own text.

### I.5 Prose — the register the guide enforces

Quoted from the **1987 TNG Writer/Director's Guide** (**A, R**) unless marked otherwise. This is
the document's own voice, which is the point: a writer's bible is written in the register it is
trying to impose, and this one is written in imperatives.

**The one rule everything else serves:**

> **BELIEVABILITY IS EVERYTHING. IT IS THE MOST ESSENTIAL ELEMENT OF ANY STAR TREK STORY.**

and it is operationalised as a test any reader can run, which is why the guide is teachable:

> If you're in doubt about a scene, you can apply this simple test: "Would I believe this if it
> was occurring on the bridge of the battleship Missouri?" If you wouldn't believe it in the
> twentieth century, then our audience probably won't believe it in the twenty-fourth.

**Prose is specified as a budget, not a flavour.** The guide fixes the container before it
allows the content: a **teaser and five parts**, teaser 3–5 pages, each part about 10–11 script
pages, first draft **"not more than 55-56 pages"**, running time **43 minutes**, and "long
rambling scenes are to be avoided". A rule that can be counted is a rule a room can enforce.

**Two registers are required to coexist, and the guide says which comes first:**

> A good STAR TREK story should have both a science fiction element and a personal element.

The science-fiction element "should be thought-provoking and visual" and "need not be a huge
galactic event"; the personal element is "a human dilemma". When the two collide, the guide's
order is explicit: the adventure must capture attention **first**, and the comment about
humanity comes after ("once the above has captured the audience's attention, we want to
include our usual comments about the challenges humanity now faces").

**Character is written as behaviour under selection pressure**, not as interiority:

> The crew of the Enterprise are intelligent, witty, thoughtful, compassionate, caring human
> beings -- but they have human faults and weaknesses too -- although not as many or as
> severe as in our time. They have been selected for this mission because of their ability to
> transcend their human failings.

**The negative list is the most useful part of the document**, because it is where a bible
becomes a gate rather than a mood board. Thirteen items, of which the load-bearing ones are:

- no psionics or "mysterious heavenly powers" — "the explanation must be extrapolated from a
  generally accepted science theory";
- no "galaxy policemen" — "We are not in the business of toppling cultures that we do not
  approve of";
- "Plots involving a whole civilization rarely work" — deal with specific characters from
  another culture instead;
- no jeopardy manufactured by making the crew stupid or the technology fail;
- no fantasy, no "swords and sorcery", no melodrama — "Melodrama is a writing style which does
  not require believable people."

**The structural device that carries exposition** is the log: Captain's Log, Medical/Science/
Supplemental, and Away Logs, "ALWAYS introduced with a stardate", a five-digit number plus one
decimal (`41254.7`), the leading `4` meaning 24th century. That is a prose rule disguised as a
formatting rule: exposition is spoken by a character who is writing it down.

**What is inference, not quotation** (the 1967 booklet is still **P**): that the same
present-tense, active, camera-facing discipline governs the earlier guide, and that
"no irony about the premise" is a rule rather than a house style. The 1987 text supports the
first (it is written as the script will be shot) and does not address the second.

That is why the bible reads flat and works: it is a specification, not a story.

### I.6 The self-description that dates it

The 1987 guide opens with a **NOTICE TO WRITERS** that refuses unsolicited submissions except
from recognised literary agents (**A, R**), and states its position relative to the original
series in a phrase worth keeping: the new ship is "a vessel of less 'battleship sterility'",
because 24th-century progress is "centered on improving the quality of life". A bible is also a
**pitch to the writers it is recruiting**, and this one argues from aesthetics (light, comfort,
vegetation in the corridors) as much as from plot.

---

## Part II — Star Wars: there is no writer's bible, and that is the finding

Star Trek's bible is a **document with revisions**. Star Wars has no equivalent, and the search
result is the answer: what the franchise calls canon is a **chain of drafts plus a frame story**,
not a manual.

### II.1 What the "bible" actually is

| artifact | what it does | tier | state |
| --- | --- | --- | --- |
| **"The Star Wars"** (1973 treatment, ~13 pp.) | the first prose statement of the universe; a synopsis, not a guide | C | P |
| **"Adventures of the Starkiller, Episode One: The Star Wars"** (1975 drafts) | the treatment expanded toward a shooting script; the **"Journal of the Whills"** frame returns here | C, D | P |
| **"…as taken from the Journal of the Whills"** (later draft title) | names the in-universe source of the text — the bible *as fiction* | D | P |
| the 1976 novelization | the first published canon text; ghostwritten from the drafts | C/U | P |
| Lucasfilm's continuity operation (Holocron; after 2014, the Story Group) | replaces the document with a **database and a committee** | C/U | P |

Sources: Salon, Chris Taylor, 2014-10-03, "Secrets of the *Star Wars* drafts" — **C, P**,
<https://www.salon.com/2014/10/03/secrets_of_the_star_wars_drafts_inside_george_lucas_amazing_and_very_different_early_scripts/>;
theforce.net forum listing of draft titles — **D, P**,
<https://boards.theforce.net/threads/the-scripts-of-the-skywalker-saga.50053902/>.

**The structural difference, stated plainly:** a Star Trek bible tells a writer *what the show
is*; the Star Wars drafts show *what the story became*. One is normative, the other is
archaeological. That is why Star Wars canon disputes are about **which draft** and Star Trek
canon disputes are about **which series**.

### II.2 Theme

The documented thematic centre (Lucas on the **"used future"** aesthetic, quoted in secondary
sources: **C**) is a deliberate refusal of the clean-future look — the universe is second-hand,
repaired, lived in. The narrative consequence is a **mythic register borrowed from comparative
mythology** (Campbell's monomyth, which Lucas has discussed publicly at length; **C/U** here):
the hero's call, the threshold, the ordeal, the return.

Themes as the drafts arrange them:

- **inheritance and orphanhood** — the protagonist is defined by what he does not know about
  his parentage;
- **machinery as moral condition** — the same technology is farm equipment or a weapon
  depending on who holds it;
- **institutional decay** — the Republic's rot is administrative before it is military;
- **the Force as an unexplained given** — the bible never explains it, which is what keeps it
  available to later stories.

### II.3 Situation

Star Wars has no episode formula; it has a **sequence grammar**:

- an **inciting capture** (a princess, a plan, a droid) that hands the protagonist a task;
- a **descent into a place that is not the hero's** (cantina, Death Star, underworld) where the
  rules are renegotiated;
- a **set-piece escalation** whose geography must be legible without dialogue;
- a **duel that externalises the argument**;
- a **ritual close** (medal, funeral, sunset) that converts violence into ceremony.

### II.4 Character

Where Star Trek's bible specifies functions for an ensemble, the Star Wars drafts specify
**archetypes in collision**: the orphan, the mentor who must be lost, the rogue who must choose,
the princess who is a commander, the villain who is a warning. The "bible" here is the
**casting of functions onto a family**, which is why the saga can be re-entered at any point.

### II.5 Prose

The register is **pseudo-archaic and declarative** — the "long time ago" frame, the
present-tense synopsis voice, proper nouns used without apology. The prose rule that follows is
the opposite of Star Trek's: Star Trek's guide asks the writer to **explain the premise**;
Star Wars' drafts ask the writer to **never explain the world**, only the situation.

---

## Part III — The Klingon edition

### III.1 What exists, from the project that makes it

The Klingon Language Institute's **Religious Text Translation Project** is the authority, and
its own page is the primary source for the whole section — **A, R**,
<https://www.kli.org/religious-text-translation-project/>:

- the project began in **1994** as the **Klingon Bible Translation Project** (coordinated by
  **Kevin Wilson** until **2003**), and was expanded and renamed the **RTTP in 2015**
  (coordinated by **Melanie Roney**);
- the KLI states its motive explicitly as **secular** ("the KLI's goals do not include
  missionary work"), which matters: this is a *language-corpus* project, not a religious one;
- the whole Bible is **`paq'a'`** (the "big book"); the religious books as a class are
  **`lalDan paq'a'`**; the Old Testament is **`yID lalDan paq'a'`** and the New Testament
  **`'IHrIStoS lalDan paq'a'`**;
- **completed**: `yonaH` (Jonah), `marqoS` (Mark — titled **`De' QaQ'e' ghItlhbogh marqoS`**),
  the Galatian, Ephesian, Philippian, Colossian, Thessalonian, Timothian, Philemon, Petrine and
  Johannine epistles, `taDyoS` (Jude), and the non-canonical **`vep QaQ'e' qonbogh to'maS`**
  (Gospel of Thomas);
- **in progress**: `mattlhew` (Matthew), `luqaS` (Luke), `bom` (Psalms), Hebrews, James, Titus,
  the Book of Mormon (`mormon paq`), and a Latter-day Saint hymnal (`quvwI'pu' tIQHa' … bommey`);
- also completed: chapters of `rutlh` (Ruth, ch. 1), `'eSter` (Esther, ch. 1) and `job`
  (Job 13:14); plus a published **Tao Te Ching**, `pIn'a' qan paqQDI'norgh`.

**Read that list as an engineering result, not trivia.** It is a corpus census: ~30 documents
in a constructed language, each one evidence that the language can carry a register it was not
designed for. That is exactly the problem a franchise bible poses too.

### III.2 The trap the KLV names for us

The **Klingon Language Version** of the World English Bible (`klv.mrklingon.org`) describes
itself as **"not a translation"** — a **relexification**: English syntax and semantics carried
word-for-word into Klingon vocabulary. Its own author says so (**C**, <http://klv.mrklingon.org/>,
fetched but the page is a redirect stub; the description is corroborated by the r/tlhInganHol
discussion of the KLV and by Wikipedia's survey of Bible translations into constructed
languages, **C, P**).

This is the single most useful fact in the dossier for anyone building a "bible in Klingon": a
word-for-word transfer **looks** like the source language and is not the target language. A
Klingon bible that reads like an English bible in costume has failed the same way a 3D
translation fails when it carries the pixels instead of the rules — the surface is transported
and the structure is not.

### III.3 A Klingon edition of *this* dossier — gloss sheet, not prose

Composing Klingon sentences requires a Klingonist; a machine that invents grammar produces the
KLV's failure mode with extra confidence. So the Klingon edition is presented as a **gloss
sheet of attested terms** (all from the KLI page above) plus the section headings of Parts I–II,
each rendered by the nearest attested term, with the mapping shown so a translator can correct
it:

| section | Klingon rendering | basis (attested) |
| --- | --- | --- |
| the bible / the big book | **`paq'a'`** | KLI: the Holy Bible is `paq'a'` |
| the bible of a religion | **`lalDan paq'a'`** | KLI: the religious books as a class |
| Star Trek's writer's bible | **`paq'a' qonlu'pu'bogh`** — *the book that was composed* | `paq'a'` attested; `qon` (compose/record) attested on the KLI page in `qonbogh to'maS`, `qonta'bogh luqaS` |
| Star Wars' draft chain *(no single book)* | **`nav QIn`** — *message document* | KLI: each epistle is `nav QIn` |
| theme | **`bom`** — *song* (the nearest attested register word) | KLI: Psalms = `bom` |
| character | **`quvwI'pu'`** — *the honoured ones* (as a class of persons) | KLI: the hymnal's `quvwI'pu'` |
| prose / register | **`Hol`** — *language* (with `tlhIngan Hol` = the Klingon language) | KLI: `tlhIngan Hol` throughout |
| completed / in progress | **`… qaStaHvIS`** — *while it happens* (status, not a fact) | marked **unverified composition**: no attested phrase on the KLI page |

#### III.3a From gloss to sentences — composed, and labelled as composed

The gloss sheet can be taken one step further without pretending to be a translator: Klingon is
**object–verb–subject**, marks person on the verb by prefix, and builds aspect and attitude from
suffix chains, so a short sentence can be assembled from attested roots and checked pattern by
pattern. Every line below is **my composition**, not a quotation, and the last column says what a
Klingonist still has to decide. Nothing here is presented as `tlhIngan Hol` prose.

| # | Klingon | literal | what is doing the work | status |
| --- | --- | --- | --- | --- |
| 1 | `paq'a' vIlaD` | big-book I-read-it | `vI-` 1sg subject / 3sg object; `laD` *read* | **safe pattern** (canonical OVS + prefix) |
| 2 | `paq'a' vIlaDnIS` | big-book I-read-it-need | `-nIS` *need to* | **safe pattern**; suffix order after the verb stem |
| 3 | `tlhIngan Hol vIghoj` | Klingon language I-learn-it | `ghoj` *learn*; the stock self-description of a learner | **safe pattern** |
| 4 | `mu'tlheghmey vIlaD` | sentences I-read-them | `-mey` plural (non-body-part) | **safe pattern**; `mu'tlhegh` = *sentence* |
| 5 | `bom vIqon` | song I-compose-it | `qon` *compose/record*, the same root the KLI uses in `qonbogh to'maS` | **safe pattern** |
| 6 | `paq'a' laDmeH Hol vIghoj` | big-book for-reading language I-learn-it | `-meH` purpose clause before its main clause | **needs a Klingonist** — purpose clauses are correct in shape but this one stacks two objects (`Hol` and the implied book) |
| 7 | `paq'a' boqonta'` | big-book you-pl-composed-it | `bo-` 2pl subject / 3sg object, `-ta'` *accomplished* | **needs a Klingonist** — `-ta'` asserts completion, which may be the wrong claim about a revision chain |
| 8 | `paq'a' QaQ` | big-book good | no copula: a noun + adjective is a sentence | **safe pattern**; `QaQ` *be good* |

Read the table as a **fidelity ledger**, which is the whole point of the section. Rows 1–5 and 8
are grammar a learner can defend; rows 6–7 are the places where a machine writing Klingon
produces something that *looks* translated. Compare the English: "the guide is a specification,
not a story" has no Klingon row here at all, because the honest answer is that I cannot render
it without inventing a metaphor — and inventing one is exactly what the KLV did at scale.

What would close this section: a Klingonist's signature on rows 6–7, or their replacement, plus
one attested citation for `mu'tlhegh` from a dictionary rather than from memory.

Two of the gloss-sheet rows are **attested vocabulary in an unattested construction**, and they are
marked as such on purpose. The rule this dossier applies to itself is the rule the Klingon
Language Version broke: **do not present a gloss as a translation.** A Klingon edition becomes
real when a Klingonist signs it; until then it is a specification for that work, with every term
traceable to the project that owns the language.

### III.4 Why the Klingon edition belongs in this dossier at all

Because the three documents answer the same question from three directions:

- **Star Trek's bible** says: here is what the show is, revised as we learn.
- **Star Wars' drafts** say: here is what the story became, in order.
- **The Klingon RTTP** says: here is a language being extended until it can carry a book it was
  never built for, with a census of which books are done.

All three are **translation problems with a ledger**: what was carried, what was not, and who
signs the difference. A bible that does not state its own fidelity is a rumour with a binding.

---

## What was retrieved, in full, and what was not

| source | tier | state | note |
| --- | --- | --- | --- |
| kli.org RTTP project page | **A** | **R** | full book census, dates, coordinators, Klingon titles |
| Memory Alpha, *The Star Trek Guide* | C | **R** | 1964 pitch, 1966 second revision, 1967-04-17 Fontana third revision |
| archive.org TNG Series Bible item | **B** | **R** | Gerrold, 1987-03-27, OCR, 51.5 MB |
| archive.org TNG Writer/Director's Guide item | **B** | **R** | metadata API resolved the file list; `_djvu.txt` fetched, 81,641 bytes, md5 `64f473b0c215ec917aa61e7b196decf8` |
| **TNG Writer/Director's Guide full text**, Roddenberry, 1987-03-23 | **A** | **R** | quoted in §I.5–I.6: believability test, 13-item negative list, teaser + five parts, stardate format, NOTICE TO WRITERS |
| archive.org TNG Series Bible item `_djvu.txt` | **B** | P | filename now known (`Star_Trek_-_The_Next_Generation_Bible_djvu.txt`, 84,077 bytes); not fetched this session |
| Fanlore, *The Star Trek Guide* (1967) | C | P | 31 pp., Norway Productions, Lincoln Enterprises |
| *The Trek Files* 1-01 (2018) | C | **R** | April 1967 guide; "believability factor" |
| Salon, Lucas drafts (2014-10-03) | C | P | draft titles and Whills frame |
| theforce.net draft list | D | P | pointer only |
| klv.mrklingon.org | C | P | "not a translation" — relexification, per its own description |
| bu.edu Star Trek Writers Guide PDF | — | **404** | fetch refused; no text |
| tvwriting.co.uk Star Trek Writers Guide PDF | — | **403** | fetch refused; no text |

**Next fetch, if this line of work continues:** the 1967 third revision (no working host found
yet: bu.edu 404, tvwriting 403 — try the Norway Productions/Lincoln Enterprises scan directly),
and the 1987 **series bible** text (filename known from the metadata API: 84,077 bytes). The
1987 **Writer/Director's Guide** is now in hand, so the prose characterisation in §I.5 rests on
quotation where it says it does and on inference only where it is marked as inference. The 1967
guide's prose remains undescribed by me, not because it is unavailable in principle but because
no host has served it to this session yet.
