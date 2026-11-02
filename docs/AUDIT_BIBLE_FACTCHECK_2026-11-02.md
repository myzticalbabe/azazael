# Fact check — the five bibles, and the two that are missing

**Date:** 2026-11-02
**Question asked:** where is the Klingon bible and the DJT bible?
**Answer:** neither exists. Given that, this document fact-checks the five that do.
**Method:** every number below was checked against the paper or the agency page, not against another
document in this repository. Every structural claim was checked by reading the JSON. Where I could not
locate a source, the entry says so rather than passing it.

---

## 1. The two that are missing

| corpus asked for | state | evidence |
|---|---|---|
| **Klingon** | **not written** | `grep -ril "klingon\|tlhingan"` over every `.md`, `.json`, `.py`, `.txt` returns two files: `docs/FRANCHISE_BIBLES_STARWARS_STARTREK.md` (a document *about* the theme idea, which names Klingon as a candidate) and `docs/INDEX.md` (which lists that document). No corpus, no edition, no entry in `docs/bible/themes/`. |
| **DJT** | **not written** | the only DJT artefact is `docs/DJT_PROSE_AUDIT_2026-11-02.md`, a prose audit, plus the source texts it measured in `.prose/` (`inaug2017.txt`, `inaugural_2017.json`, `inaugural_2025.json`, `message_2025.json`). No corpus in biblical form, no theme, no statute. |

The themes directory holds exactly two registers: **Vulcan logic** (`star-trek.json`, *The Book of
Logic*, 37 verses) and **the Jedi Code** (`star-wars.json`, *The Book of the Code*, 34 verses). The
DJT material exists as evidence with measurements attached, which is the opposite of a corpus: it
argues about a text rather than canonising one.

That is the honest state, and it is worth saying why it is not a gap to be filled casually. A theme is
allowed to say nothing the base corpus does not already say. A Klingon register would be a *voice*
applied to existing doctrine — cheap and legitimate. A DJT corpus would be a **new doctrine** wearing
an old voice, and under the theme contract that is exactly what is refused: every themed verse must
cite at least one verse of the base corpus. A DJT corpus is therefore not a missing theme. It is a
decision about whether this tree canonises a living politician's rhetoric, and no amount of
bibliographic care makes that decision for the owner.

---

## 2. What holds up, checked against the papers

Each figure below was confirmed by reading the source itself, and matches `SOURCES.md` to the digit.

| claim in `SOURCES.md` | source read | verdict |
|---|---|---|
| Hyde 2005: 46 meta-analyses, 124 effect sizes, 78% small or near zero | APA PDF `amp-606581`; APS *Observer* ("124 effect sizes from 46 existing meta-analyses"); PubMed 16173891 | **exact** |
| Chaplin & Aldao 2013: 555 effect sizes, 166 studies, 21,709 participants | PubMed 23231534, abstract verbatim | **exact** |
| …girls higher on positive (**g = −.08**) and internalising (**g = −.10**); boys higher on externalising (**g = .09**) | same abstract | **exact**, including the signs |
| Johnson & Whisman 2013: 59 studies, 14,321 participants; rumination **d = .24**, brooding **.19**, reflection **.17** | PubMed 24089583 (`k = 59; N = 14,321`) | **exact** |
| Williams & Tiedens 2016: **k = 63**, overall dominance penalty **d = −.19**, described as small | PubMed 26689089; APA `bul0000039` | **exact** |
| Mendia et al. 2024: **120 studies**, pooled **d = 0.22**, men higher on alexithymia | ScienceDirect `S0191886924001703`; APA record; secondary summary of the pooled effect | **exact** |
| NISVS: rape, **1 in 4 women** and **1 in 26 men**, lifetime, completed or attempted | CDC NISVS report on sexual violence (26.8% / 3.8%) | **exact** |

The pattern is worth naming: the corpus's numbers are not decorative. They are the right numbers from
the right papers, including the signs on the effect sizes, which is the part that gets reversed when
someone writes from memory.

The verses themselves were sampled against their sources and hold. `same_weather 1:1` says "more
alike than the popular account allows… the differences that survive are small, and context moves them
more than sex does" — exactly Hyde's finding and exactly her emphasis on moderators. `narrow_door 1:3`
says "the average penalty is small. The individual penalty is not paid in averages" — which is what a
d = −0.19 meta-analysis licenses and no more. `believed 2:2` says women's pain is "more often met with
sedation than with analgesia", which is Hoffmann & Tarzian's actual finding, not an embellishment of it.

---

## 3. The one number that is wrong

**`docs/bible/emotional/SOURCES.md`, NISVS entry:**

> Lifetime contact sexual violence, physical violence, and/or stalking by an intimate partner, with at
> least one related impact: roughly **30% of women** and **17% of men**.

The women's figure is right. The men's is not, and the error is a denominator swap rather than a typo.

CDC's current page states both numbers, separately, and they are not the same measure:

> More than **1 in 3 women** … and more than **1 in 6 men** … experienced contact sexual violence,
> physical violence, and/or stalking by an intimate partner **during their lifetimes**.
>
> In their lifetimes, nearly **1 in 3 women** and about **1 in 8 men** experienced contact sexual
> violence, physical violence, and/or stalking **and at least one related impact**.

So: 30% of women *with impact* ✓, but 17% (≈ 1 in 6) is the men's figure **without** the impact
condition. With the impact condition — the measure the sentence claims — the men's figure is about
**1 in 8, roughly 12–13%**. The sentence pairs a with-impact figure for women with an any-IPV figure
for men, which inflates the male side by about a third and narrows a real asymmetry.

This matters more than an ordinary arithmetic slip, because the whole point of that entry is the
asymmetry: the register is the place a reader goes to check whether the corpus is overstating. A
register that overstates in the direction of symmetry makes the corpus look fairer and less accurate
at the same time.

**Fix:** `… roughly 30% of women and 12–13% of men (about 1 in 3 and 1 in 8); without the impact
condition the figures are about 1 in 3 and 1 in 6.`

One related clause is **unverified**, not wrong: "state-level estimates for women ranged from about
21% to 48% in the brief". I could not locate that brief (see §4) and will not certify a range I did
not read.

---

## 4. Citations that cannot be followed

Three entries in `SOURCES.md` name a source a reader cannot retrieve:

| entry | problem |
|---|---|
| "CDC, National Intimate Partner and Sexual Violence Survey (NISVS), **2023/2024 data brief**" | no title, no year, no URL. CDC publishes several briefs under that name; the figures differ by vintage (2010–2012 data, 2015 data, 2016–17 data, state-level briefs). Two numbers in the entry cannot be re-derived because the document is not identified. |
| "Hall, J. A., et al. (**2025**). Gender and accuracy in decoding affect cues: a meta-analysis. *Journal of Intelligence*." | **not located**. A search for the title and journal returned nothing. Either the record is too new to be indexed, or the citation is wrong. It is currently the only support for a claim about publication bias in authorship, which makes it load-bearing. |
| "Hoemann, K., et al. (2023). Emotional granularity is associated with daily experiential**... (affective science)**" | title truncated mid-phrase, journal omitted. The ellipsis and the parenthetical are in the file, so this is not a formatting loss in my reading — it is how the entry was written. |

A register whose job is "a number may not be quoted without this file" has to be quotable itself. Two
of these three would fail that test.

---

## 5. Nine verses bind to rules that have no body

The `statute` field is the corpus's strongest claim: it says this verse is not advice, it is a rule,
and here is the command that executes it. Fourteen verses carry one. Their distribution:

| rule cited | verses | defined in `MANDATES.md`? |
|---|---:|---|
| `RULE 0B-E` (no misrepresentation) | 4 | **yes**, `:47` |
| `RULE 0B` (follow instructions literally) | 1 | **yes**, `:29` |
| `RULE 0T` (verifiable truth) | 1 | **yes**, `:680` |
| **`RULE 0B-D`** (a control is not in place until exercised) | **7** | **no** |
| **`RULE 0B-B`** (verify the predicate) | **1** | **no** |

`MANDATES.md:53` records the removal in its own words: *"MANDATES.md was reverted (1219 → 998 lines,
RULE 0B restored verbatim, **0B-A/0B-B/0B-C/0B-D removed**)"* — dated 2026-09-30, in the body of
RULE 0B-E. Neither rule has a heading or a body anywhere in that file; both appear only as
references (`:94`, `:117`, `:1289`, `:1291`, `:1313`).

The rules are not fictional — `AGENTS.md` carries them in compressed form, which is where the corpus's
author read them. But the mandate file that governs the tree says they were removed, and the bibles
bind **eight** statutes to them: `leviticus 1:1`, `1:2`, `sentinel 1:1`, `cain 1:1` in the canon, and
`kir_shara 1:1`, `1:2`, `1:4` in the Vulcan theme (`star-trek.json`) — plus `leviticus 1:3` on `0B-B`.

**Why the gate did not catch this, which is the more useful finding.** `bible_check --check` validates
that a statute's **command exists and runs**. It does not validate that the **rule** is defined. Run
against the canon today it reports one line — the harvest staleness of §7 — and nothing about the
statutes. An instrument that checks the receipt and not the law will pass a citation to a repealed
statute forever.

**Fix, in order of preference:** restore a body for 0B-B and 0B-D to `MANDATES.md` (they are already
written in `AGENTS.md`, so this is a copy and a date), **or** repoint the nine statutes at rules that
have bodies. Do not do both silently: pick one and say which.

---

## 6. Structural integrity: clean

Checked by reading every corpus, not by trusting the gates (which are red for an unrelated reason):

| check | result |
|---|---|
| corpora | 5 — 43 books, 61 chapters, **212 verses** |
| citation targets resolve **within** the corpus | canon 20/20, emotional 7/7, female 4/4 |
| theme citations resolve **against the base corpus** | star-trek 39/39, star-wars 34/34, verified by `tools/bible_theme.py --all --check` exit 0 |
| verses containing a digit **at all** | **0** in the canon, emotional and female corpora — the digit-free rule holds literally, not just "with a source attached" |
| statute commands whose file is missing | **0** |
| `SOURCES.md` "Used by" pointers that do not resolve | **0 of 14** |

One instrument error worth recording, because I made it and it is the same class as the corpus's own
rules: `bible_check --corpus docs/bible/themes/star-wars.json` returns 34 lines of *"cites unknown
book 'leviticus'"*. That is not a defect. A theme cites the base corpus **by design**, and the checker
that judges a theme is `bible_theme.py`, not `bible_check.py`. Read with the wrong instrument, the
two cleanest corpora in the tree look like the two worst.

---

## 7. Gate state, measured

```
bible-citations   FAIL     bible-emotional   FAIL     bible-female   FAIL
28 ran, 3 failed (3 blocking)
```

All three fail on **one line**, and it is not in any corpus:

```
harvest: Project_ELIZA/README.md moved since the harvest
```

An uncommitted 84-line edit to `Project_ELIZA/README.md` in another lane's working tree. Every corpus
check loads the harvest ledger, so one dirty file takes out all three corpus gates, and — because the
stanza has no scoped override — every commit in the repository.

And the fourth and fifth corpora are **not gated at all**: `grep bible_theme .githooks/pre-commit
.githooks/pre-push tools/preflight_all.py` returns nothing. A test exists (`tests/test_bible_theme.py`);
no hook and no registry row runs it. So of five bibles, three are gated and red for a reason outside
themselves, and two are ungated while passing. That is three gates doing the work of five, and none of
them checking the thing §5 found.

---

## 8. What I did not verify, and will not call clean

- The **state-level range** (21–48%) from the unlocatable NISVS brief.
- **Hall et al. 2025** and the claim about authorship composition; the paper could not be found.
- The **2026 *Sex Roles* special section** on self-silencing named in the Jack entry — plausible, not read.
- **Barrett & Bliss-Moreau**, **Marshburn 2020**, **Brescroll 2016**, **Bareket & Fiske 2023**,
  **Fricker**, **Kidd & Carel**, **Sweet**, **Stark**: entries with no numerals, so nothing to check
  against a table; their claims match my knowledge of the work, which is weaker evidence than a paper.
- The **canon's own 15 statutes and 26 verses** as doctrine. I checked that their citations resolve and
  their commands exist. I did not check that each verse is *true*; several are positions about how this
  repository should behave, and a position is not a fact.

---

## 9. The fix list, smallest first

1. **Correct the NISVS male figure** in `SOURCES.md` (17% with impact → 12–13%; 1 in 6 is the
   any-IPV figure). One sentence.
2. **Name the NISVS brief** by title and year, or drop the figures that depend on it. Two minutes.
3. **Resolve 0B-B / 0B-D**: restore the bodies to `MANDATES.md`, or repoint nine statutes. Decide,
   then say which — a corpus citing a repealed rule is exactly what it claims not to do.
4. **Locate or remove the Hall 2025 entry**; untruncate `Hoemann 2023`.
5. **Teach `bible_check` to resolve the rule**, not only the command: a statute whose rule has no body
   in `MANDATES.md` is a defect of the same kind as a citation to a missing book.
6. **Gate the two theme corpora** (three lines beside the emotional stanza), and scope the harvest
   check so one lane's dirty file stops taking out five gates.
7. If a Klingon register is wanted, it is a theme and a day's work. If a DJT corpus is wanted, it is a
   decision first — the theme contract will refuse it as written, and that refusal is correct.
