---
name: azazael-package-index
description: Look up a Python package reference (aadict, impacket, numpy, msldap, pwntools, ...) from ONE archived index instead of loading 1,042 separate package skills. Use when you need a package's version, summary or usage note.
metadata:
  category: reference
  project: azazael
---
# Azazael Package Index

## What changed, and why

Until **2026-10-30** this tree registered **1,042 `azazael-pkg-*` skills** next to
203 real ones. Their frontmatter descriptions alone were **138,964 bytes (~34.7k
tokens)**, and every client that lists skills paid that on every request — about
four times the cost of the canon `AGENTS.md`, to advertise a catalogue the model
then has to ignore. 54 package names existed twice (`azazael-pkg-anyio` **and**
`azazael-pkg314t-anyio`), so the list also taught the model that it is noise.

They were not deleted. They were archived **byte for byte**:

```
skills.pkg-archive/source/<name>.md          source corpus (former skills/)
skills.pkg-archive/load/<name>/SKILL.md      former load path (.agents/skills/)
tools/data/pkg_index.json                    generated index, 1,042 rows
```

## How to use it

```sh
python tools/skills_find.py anyio             # search package / name / summary
python tools/skills_find.py --layer pkg314t   # only the 3.14t/3.15t entries
python tools/skills_find.py --show azazael-pkg-anyio   # print the archived skill
python tools/skills_find.py --stats           # index health, duplicate report
```

`--show` prints the original SKILL.md — the same text that used to be registered
as its own skill. Nothing is lost by asking for it on demand.

## What is NOT archived

The **203 real skills** stayed loadable: `azazael-*` workflow skills, the
`bin-*` tool wrappers, and the package-catalogue entries that carry real
procedure rather than a version string. If a package skill is not in the index,
it was never a package skill.

## Restoring one

```sh
cp skills.pkg-archive/source/azazael-pkg-anyio.md skills/azazael-pkg-anyio.md
python tools/sync_skills.py            # or: python tools/canon_drift_check.py --fix
```

Restoring 1,042 is the thing to avoid: it is a 34.7k-token bill on every request.
Restoring the one you need is cheap, and that is the whole point of the index.
