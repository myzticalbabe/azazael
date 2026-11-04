# The Bible in Klingon — accuracy audit

**Scope.** The Klingon-bible material in `docs/FRANCHISE_BIBLES_STARWARS_STARTREK.md`
(Part III), checked against the two sources that own it:

| source | tier | state | what it establishes |
| --- | --- | --- | --- |
| <https://www.kli.org/religious-text-translation-project/> | **A** | **R** (fetched 2026-11-02) | dates, coordinators, rationale, full book census, Klingon titles |
| <https://en.wikipedia.org/wiki/Klingon_language> + `/Klingon_grammar` | **C** | **R** (fetched 2026-11-02) | phonology, prefix/suffix tables, canon policy, published corpus |
| SWORD module `KLV` metadata + klingonword.org "Why a Klingon Bible?" | **B** | **R** (search 2026-11-02) | the KLV's own self-description as a relexification |
| `klv.mrklingon.org` | — | **stub** | returns "Please follow this link."; confirms the dossier's note that the site is a placeholder, not a text |

**The distinction the dossier blurred.** There are two different objects, and Part III
was titled in a way that let them merge:

1. **The Star Trek bible** — a production document (pitch, writers' guide, series
   bible). An *internal* document about how to write the show.
2. **The Bible in Klingon** — a *translation project*: the KLI's Religious Text
   Translation Project, running since 1994, translating scripture into a constructed
   language. An *external* corpus with a public census.

Part III is about (2), but §III.3 then presents "a Klingon edition of *this* dossier" —
which is a third thing again, and not a bible at all. Naming it "The Klingon edition"
made three objects look like one. Retitled to keep them apart.

---

## 1. Verified as stated (no change)

Every item below was read on the KLI page during this audit, not recalled:

- **1994 start, as the Klingon Bible Translation Project; Kevin Wilson coordinating
  until 2003.** Matches exactly.
- **Expanded and renamed the RTTP in 2015, coordinated by Melanie Roney.** Matches
  exactly. (Wikipedia's Klingon article attributes the *original* project to Roney;
  that is a compression, and the KLI page is the authority. The dossier had it right.)
- **Secular rationale, quoted.** The page's own words: "the KLI's goals do not include
  missionary work, but this is a project worthy of our efforts for purely secular
  reasons." The dossier's quotation is faithful.
- **`paq'a'`** for the Holy Bible; **`lalDan paq'a'`** for the religious class;
  **`yID lalDan paq'a'`** (Old Testament); **`'IHrIStoS lalDan paq'a'`** (New
  Testament). All four match, including the `'IHrIStoS` spelling of *Christ*.
- **Completed census**: `yonaH` (Jonah); `De' QaQ'e' ghItlhbogh marqoS` (Mark);
  Galatians, Ephesians, Philippians, Colossians, 1–2 Thessalonians, 1–2 Timothy,
  Philemon, 1–2 Peter, 1–3 John; `taDyoS` (Jude); `vep QaQ'e' qonbogh to'maS`
  (Gospel of Thomas). All marked *complete* on the page.
- **In-progress census**: `mattlhew` (Matthew, Michael Kounenos), `luqaS` (Luke, Jack
  Bradley), `bom` (Psalms, Kyle Dillon), Hebrews (Ester Lüken), James (Jack Bradley),
  Titus (Jack Bradley), `mormon paq`, the LDS hymnal. All match, names included.
- **Partials**: `rutlh` (Ruth) ch. 1; `'eSter` (Esther) ch. 1; `job` (Job) 13:14.
  Match. Note the page marks Ruth ch. 1 *and* "rut complete" in the same line — the
  page contradicts itself; the dossier's "ch. 1" is the defensible reading.
- **Tao Te Ching published.** Match.

## 2. Defects found and fixed

**2.1 The Tao Te Ching title was misspelled by copying the source (A-level source,
wrong text).** The KLI page prints `pIn'a' qan paqQDI'norgh`; the published book and
the standard bibliography give **`pIn'a' qan paQDI'norgh`** — `paQ` *teach*, with
`-DI'` + `-norgh`, not `paq` *book*. The page's `paqQ` is a typo. The dossier copied
it because it copied faithfully, which is how a typo survives a citation.

**2.2 Luke's Klingon title exists and was omitted.** The page carries
`vep QaQ'e' qonta'bogh luqaS` — "the good news that Luke composed" — with `-ta'`
(completed deliberately) where Thomas's title has `qonbogh` (that he composed). The
dossier listed only `luqaS`. Both titles belong, because the pair is the single
cleanest example of what `-ta'` does that a bare relative clause does not.

**2.3 Two titles on the KLI page are corrupted by duplicated suffixes.**
Colossians reads `nav QIn luHevpu'bogh qoloSaynganpu'nganpu'` and 1 Thessalonians
reads `… eSalonI'nganpu'nganpu'`. `-nganpu'` is *people of* + plural, and the page
doubles it. The dossier inherited neither (it named the epistles in English), which
was the right call, but the defect should be recorded so the next reader does not
"restore" it.

**2.4 The KLV was under-sourced and is now pinned.** The dossier called it tier **C,
P**, with the description "corroborated by a subreddit and by Wikipedia". The
self-description is stronger than that: the SWORD module metadata at
<https://www.crosswire.org/sword/modules/ModInfo.jsp?modName=KLV> and the author's
own "Why a Klingon Bible?" page state that the KLV is "an experimental
**relexification** of the WEB. It is **not properly a translation**, but a
demonstration of what a `tlhIngan Hol` [Klingon] text might look like". That is
tier **B** and it is the KLV describing itself. The author is Joel Anderson, of the
Universal Translator Assistant Project. The claim the dossier builds on it — *a
word-for-word transfer looks like the source language and is not the target
language* — stands, and now rests on the project's own words.

**2.5 Mark's translator is known and was missing.** The Mark text is by **Nick
Nicholas**, the Hellenist and Lojbanist who also translated *Hamlet*. That is not
trivia: it means the two best-known Klingon translations of a large literary work
were made by one person with formal Greek, which is exactly the credential a
relexification lacks.

## 3. The grammar rows, re-scored against the reference grammar

The dossier's §III.3a composed eight sentences and graded them. Re-checked against
the prefix and suffix tables:

| # | claim in dossier | verdict |
| --- | --- | --- |
| 1 | `paq'a' vIlaD` — `vI-` 1sg→3sg, OVS | **correct**; `vI-` is "I–it" |
| 2 | `-nIS` *need to*, after the stem | **correct**; type-2 volition suffix |
| 3 | `tlhIngan Hol vIghoj` | **correct**; OVS with the language as object |
| 4 | `mu'tlheghmey`, `-mey` non-body-part plural | **correct**; `mu'tlhegh` *sentence* |
| 5 | `bom vIqon`, `qon` *compose/record* | **correct** |
| 6 | `paq'a' laDmeH Hol vIghoj` — flagged "needs a Klingonist" | **over-cautious.** `-meH` purpose attaching to `Hol` is well-formed and the main clause is clean. The honest grade is *defensible*: the open question is lexical (`ghoj` taking a language), not structural |
| 7 | `paq'a' boqonta'` — flagged for `-ta'` | **correctly flagged, for the wrong reason.** `-ta'` is not "accomplished" but *completed **on purpose***. The sentence therefore claims the addressees finished deliberately, which is a claim about intent, not about state. That is the defect, and it is sharper than "may be the wrong claim about a revision chain" |
| 8 | `paq'a' QaQ` — noun + adjective, no copula | **correct**; `QaQ` *be good*, and a verb with no subject prefix is a third-person statement |

One addition the dossier should have made and did not: **`-lu'`**. `paq'a' qonlu'pu'`
— "the big book has been composed" — is the form that avoids naming a composer at
all, and it is the correct Klingon when the agent is genuinely unknown or irrelevant
(this is not a passive; it makes the *subject* indefinite). Every "who wrote it"
question in a corpus with a revision chain wants `-lu'`, and its absence from the
gloss sheet is the section's largest gap.

## 4. What the census actually proves, stated carefully

The dossier says the ~30 documents are "evidence that the language can carry a
register it was not designed for". True, with one qualification worth keeping: a
completed book is evidence that a translator finished, not that the result reads as
Klingon rather than as glossed English. The KLV is the control group for exactly
that distinction — it is complete, published, and *by its author's own account* not a
translation. **Completeness is not fidelity**, and the census alone cannot tell the
two apart. Only the translator's method can, which is why 2.5 (who translated Mark)
matters more than the count.

---

## 5. Sources, and what is still unread

| source | tier | state |
| --- | --- | --- |
| kli.org RTTP page | **A** | **R** — full census, re-read this audit |
| crosswire SWORD `KLV` module metadata | **B** | **R** via search snippet; the module file itself not downloaded |
| klingonword.org "Why a Klingon Bible?" | **B** | **R** via search snippet |
| Wikipedia *Klingon language* / *Klingon grammar* | **C** | **R** — used only for grammar tables, which trace to Okrand |
| `klv.mrklingon.org` | — | **stub**, "Please follow this link." — no text retrievable |
| Okrand, *The Klingon Dictionary* (1985) | **A** if held | **not held** — every grammar claim above is second-hand through Wikipedia's tables, which cite TKD. A claim about Klingon that matters should be checked against TKD itself |

**Next fetch, if this continues:** the KLV module text itself (to quote a verse and
show the relexification rather than describe it), and a copy of TKD for the grammar
tables. Until then, treat §3's verdicts as *consistent with* the reference grammar,
not as *quoted from* it.
