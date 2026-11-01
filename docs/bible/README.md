# The Book of the Tree — the corpus, and what the checker will refuse

The Bible is written in `bible.json`, not in prose files, so that its citations can
be resolved and its figures traced. This directory holds the corpus, the rules the
validator enforces, and the generated genealogy. **The prose is Kilo's to write.**
What is here is the apparatus that keeps the prose honest, plus a seed corpus with
one book in each of four genres, so the checker has something to check and the
shape of a verse is visible.

```bash
python tools/bible_check.py --check               # the gate: exit 1 on any defect
python tools/bible_check.py                       # counts, if it is clean
python tools/bible_check.py --genealogy --write    # regenerate GENEALOGY.md
python tools/bible_check.py --json                 # machine-readable summary
```

`tools/bible_check.py --check` runs in the commit hook (`.githooks/pre-commit`,
stanza "Bible") and in the gate registry, so a corpus that contradicts itself
cannot be committed.

## The shape of a verse

```json
{
  "number": 1,
  "text": "A control shall be exercised before it is called a control.",
  "cites": ["genesis 1:2"],
  "source": "python tools/preflight_all.py --self-test",
  "statute": {"rule": "RULE 0B-D", "check": "python tools/preflight_all.py --self-test"},
  "variants": [{"reading": "The circulated reading", "text": "...", "source": "..."}]
}
```

Only `number` and `text` are required. The rest are refusals waiting to happen if
you add them half-way, which is the point:

| field | what it obliges |
|---|---|
| `cites` | every reference must resolve to a verse that exists. Forward and backward both fine; the canon is read whole. |
| `source` | required the moment a verse body contains a digit. It must name a repository path that exists, or the figure is a claim rather than evidence. |
| `statute` | a law needs a `rule` that exists in `MANDATES.md` **and** a `check` path that exists. A statute with nothing executing it is a proverb and is refused. |
| `variants` | the apparatus: `reading` names the manuscript (or the source), `text` is what it says, `source` is where it came from. The body keeps the reading of this codex. |

Refused outright, in body text and in variants alike: email addresses, phone
numbers, and the forensic deny tokens (`bcc_audit`, `FETCH_LOG`,
`edge_proof_ledger`, `identity_tiebreak`, `new_sources_log`, `REINVESTIGATION`).
Methodology ships; people do not. That is the same line
`Project_Nurse_Ratchet/DISCLOSURE_POLICY.md` draws, enforced here instead of
remembered.

## The genres, one job each

A canon written in a single register is pastiche. Declare a genre per book and let
the style follow the job:

| genre | the job | the model |
|---|---|---|
| `etiology` | why the tree exists at all | Genesis |
| `law` | statutes, each bound to a check | Leviticus, Deuteronomy |
| `history` | what was done, dated, including the failures | Samuel, Kings |
| `chronicle` | the census: what is actually in the tree | Numbers |
| `wisdom` | two-line aphorisms from experience | Proverbs |
| `lament` | the human register; no moral, no lesson | Psalms, Lamentations |
| `prophecy` | what must happen next, stated so it can fail | Amos, Isaiah |
| `gospel` | one account of a fix, from one witness | Mark |
| `epistle` | instruction to a lane | the letters |
| `apocalypse` | the release gate: what must not happen | Revelation |
| `genealogy` | generations, generated from the import graph | the begats |

## The apparatus is the honest part

Scripture solved this problem centuries before this tree did: variant readings,
with a footnote saying which manuscript has which. A figure that circulated and
was wrong belongs in `variants`, not in the body and not deleted — *"the
circulated reading: an accelerator of 7.80 GB reported as available"*, with the
source named. Deleting a wrong reading teaches nothing; the apparatus is how a
reader sees the correction happen.

## Growth is capped, as law

`limits.max_books` is 12 and `limits.max_verses_per_chapter` is 60, with hard
ceilings of 24 and 200 in the checker. To add a book, retire one. A canon of
sixty-six books is a parody with a bibliography, and an uncapped catalogue is how
this project's skills directory reached a thousand entries.

## Generations are generated

`GENEALOGY.md` is written by reading `src/` with `ast` and counting cross-package
imports. Do not edit it by hand: re-run the command. "And CORE begat PSYCHE" is a
claim a reader can check, which is the only kind this tree accepts — and the one
part of a scripture that cannot be embellished.

## Status

`seed` — Kilo replaces and extends this. `drafting` — the shape is settled and
books are arriving. `complete` — the declared books are written. The checker does
not care which; it only refuses a corpus that contradicts itself, so a Bible can
be written one book at a time and stay citable at every commit.
