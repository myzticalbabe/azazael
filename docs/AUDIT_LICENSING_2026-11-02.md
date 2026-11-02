# Audit — licensing (auditor 14 of 18, 2026-11-02)

**Scope:** verify the Apache-2.0 licensing files across the six publishable projects,
including four `LICENSE`/`NOTICE` pairs created earlier in this session and the
`Project_ELIZA` set restored from commit `3fd0b463`.

**Method:** 13 files read directly — 5 `LICENSE` bodies in full (not sampled), 6 `NOTICE`,
2 `CITATION.cff`, both `CODE_OF_CONDUCT.md` files. Nothing was executed; this is a
reading audit. No file outside the scope was modified.

**Headline:** every `LICENSE` is the complete, unmodified Apache License 2.0. One real
defect, one documentation error, and three cosmetic inconsistencies — none of them a
license defect.

---

## 1. LICENSE completeness — all five pass

| LICENSE | §1 | §2 | §3 | §4 abcd | §5 | §6 | §7 | §8 | §9 | END | APPENDIX |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `Project_Nurse_Ratchet` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Project_ELIZA` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Project_FLAMING_SWORD` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Project_FLAME` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Project_SHARDEX` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Project_CRADLE` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

All ten defined terms are present in §1 (License, Licensor, Legal Entity, You,
Source, Object, Work, Derivative Works, Contribution, Contributor). §4 carries all
four conditions (a)–(d) plus the "You may add Your own copyright statement"
paragraph. The APPENDIX retains the `Copyright [yyyy] [name of copyright owner]`
placeholder unfilled — **correct**, since that block is template text for downstream
users and must not be pre-filled.

**No shortened or reworded license found.** This was the specific risk worth testing,
because a clipped Apache text is a licensing defect that reads as complete at a glance.

### Byte-level differences (text identical, not a defect)

Worth knowing before anyone runs a checksum to "prove" the four copies match:

| File | Difference |
|---|---|
| `Project_Nurse_Ratchet/LICENSE` | one leading blank line, LF endings |
| `Project_ELIZA/LICENSE` | CRLF endings throughout, leading blank line |
| `Project_FLAMING_SWORD`, `FLAME`, `SHARDEX`, `CRADLE` | no leading blank line, LF endings — these four are byte-identical to each other |

A `cmp` between `Project_Nurse_Ratchet/LICENSE` and any of the four new ones will
report a difference on the first byte. The *license text* is the same; the leading
newline and line endings are not. If a hash check is used as evidence, hash the four
new files against each other and treat Nurse Ratchet/ELIZA as textually-equal rather
than byte-equal.

---

## 2. NOTICE and CITATION — project attribution

| File | Project named in it | Correct project? | License stated | Defect |
|---|---|---|---|---|
| `Project_Nurse_Ratchet/NOTICE` | Project Nurse Ratchet | **✓** | Apache-2.0 ✓ | none — and it explicitly disambiguates ELIZA as "a SEPARATE project … the forensic investigation suite … It is not this package." The earlier conflation is repaired in this direction. |
| `Project_Nurse_Ratchet/CITATION.cff` | Project Nurse Ratchet | **✓** | Apache-2.0 ✓ | none. Title is now "Project Nurse Ratchet: a therapeutic agent loop…"; the Weizenbaum reference note correctly says "The name itself is Nurse Ratched's, not ELIZA's". |
| `Project_FLAMING_SWORD/NOTICE` | Project FLAMING SWORD | **✓** | Apache-2.0 ✓ | none. Quotes its own README for the runtime basis and explicitly declines to claim any unverified third-party component. |
| `Project_FLAME/NOTICE` | Project FLAME | **✓** | Apache-2.0 ✓ | thinnest of the six — no runtime basis stated, no fidelity line. Truthful, just sparse. |
| `Project_SHARDEX/NOTICE` | PROJECT SHARDEX | **✓** | Apache-2.0 ✓ | project name in ALL CAPS while siblings use Title Case (cosmetic). Content is the strongest: names gitignored generated output, carries a fidelity statement, and an uninstall path. |
| `Project_CRADLE/NOTICE` | PROJECT CRADLE | **✓** | Apache-2.0 ✓ | ALL CAPS (cosmetic). Correctly names the sibling dependency `Project_FLAMING_SWORD` and identifies `tools/sentinel.py` as **THE REAPER** — which settles an open question from the publish manifest: REAPER is a component, not a tree. |
| `Project_ELIZA/NOTICE` | Project ELIZA | name correct, **subject wrong** | Apache-2.0 ✓ | **DEFECT L1** — see §3. |
| `Project_ELIZA/CITATION.cff` | Project ELIZA | name correct, **subject wrong** | Apache-2.0 ✓ | **DEFECT L2** — see §3. |

**Wrong-project attribution, both directions:** clean for Nurse Ratchet (it no longer
claims to be ELIZA). Clean for ELIZA in the sense that it does not claim to be Nurse
Ratchet — but see the defect below.

---

## 3. The one substantive defect: ELIZA's licensing metadata describes the wrong project

The owner's decree is that **Project ELIZA is the forensic investigation suite** and
Nurse Ratchet is the therapeutic health agent. ELIZA's licensing metadata was restored
from `3fd0b463` unchanged, so it still describes the therapeutic stack:

**L1 — `Project_ELIZA/NOTICE` attributes files that are not in the distribution.**
It names crisis resources in ``eliza/psyche/rt_agent.py`` and a labelled corpus in
``eliza/psyche/data/triage_corpus.jsonl``. Per the tree audit, `.gitignore` excludes
`/eliza/` and the package is generated by `tools/publicize.py`, so **no `eliza/`
directory ships**. A NOTICE pointing at absent paths is an attribution to nothing.
It also omits any statement that this project is the forensic investigation suite.

**L2 — `Project_ELIZA/CITATION.cff` and `Project_Nurse_Ratchet/CITATION.cff` carry
near-identical abstracts.** Both begin "A dependency-ordered stack of four layers: a
trait and affect model, a psychological network …" and differ only in the closing
sentence about the name. Two supposedly distinct projects cannot share one abstract;
that is how a rename error survives a correction. ELIZA's keywords are also the
therapeutic set (digital mental health, JITAI, network psychometrics).

**Not a licensing defect, but it is a licensing-metadata defect**, and it will be the
first thing a reader of the published ELIZA repo sees. It cannot be fixed by editing
the restored copy alone if the packaging gate regenerates these files — confirm which
generator owns `NOTICE`/`CITATION.cff` before editing, or the fix will be overwritten.

---

## 4. Second finding: a NOTICE statement that is false about its own evidence

Both `Project_Nurse_Ratchet/NOTICE` and `Project_ELIZA/NOTICE` state:

> "The Contributor Covenant text in CODE_OF_CONDUCT.md is used under CC BY 4.0 with
> attribution retained **at the top of that file**."

The attribution **is** retained and complete — the full `## Attribution` block naming
Contributor Covenant v2.1, the Mozilla enforcement-ladder credit and all five link
references is present at the **end** of the file (lines ~74–85 of 85 in both). So the
CC BY 4.0 obligation is **satisfied**.

But the location claim is wrong: it is at the bottom, not the top. Small, and exactly
the kind of unexamined assertion that should not ship in the one file whose purpose is
attributing other people's work. Fix the phrase, not the file.

`Project_FLAMING_SWORD`, `FLAME`, `SHARDEX` and `CRADLE` have **no**
`CODE_OF_CONDUCT.md`, so their NOTICEs correctly make no CC BY claim. Verified by
directory listing of all four.

---

## 5. Cosmetic inconsistencies, listed so they are not rediscovered

1. **Casing:** `PROJECT SHARDEX` and `PROJECT CRADLE` vs `Project …` in the other four.
2. **Depth:** FLAME's NOTICE is two short paragraphs; SHARDEX's is a page. Neither is
   wrong, but a family of six should look like a family.
3. **Line endings:** ELIZA's `LICENSE` and `CODE_OF_CONDUCT.md` are CRLF; every other
   project is LF. Harmless in git, visible in diffs.
4. **Spelling, no action needed:** project = Nurse **Ratchet**, character = Nurse
   **Ratched**. The CITATION abstract and NOTICE both use the character spelling for
   the character and the project spelling for the project — deliberate and documented
   in that project's README.

---

## 6. What this audit did NOT establish

- **Nothing was executed.** No `cmp`, no `sha256sum`, no CFF schema validation. The
  completeness claim rests on reading all five licenses end to end, not on a hash.
- **CITATION.cff validity as CFF** was not schema-checked — only fields read against
  the CFF 1.2.0 keys I could see (`cff-version`, `title`, `version`, `date-released`,
  `license`, `type`, `authors`, `keywords`, `references`). A YAML parser is the check.
- **Whether `NOTICE`/`CITATION.cff` are generated.** If a generator owns them, hand
  edits to ELIZA are transient. Unowned question; it changes the fix for L1/L2.
- **`packages/azazael-core/**` and any vendored trees were not in scope**, so a
  third-party component there would not appear in this report.

---

*Prepared 2026-11-02 by auditor 14 of 18. All five LICENSE bodies read in full; no
license was found shortened or reworded. One substantive defect (ELIZA's metadata
describes the therapeutic project) and one false statement (CC BY attribution
location) recorded. No project file was edited.*
