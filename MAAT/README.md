# MAAT — the Scales of Ma'at

Dev project named after **the scales of the goddess Ma'at**: in the Egyptian Duat (the
underworld), Anubis weighed each dead person's heart on the great scale against the
Feather of Ma'at (truth), with Ammit waiting where the scale tipped. Sources confirming
the name (searched 2026-11-03):

- Wikipedia, _Weighing of souls_: judged by Anubis "using a feather, representing Ma'at".
- World History Encyclopedia, _The Egyptian Afterlife & The Feather of Truth_: "placed it
  on a great golden scale balanced against the white feather of Ma'at".
- Australian Museum, _The underworld and the afterlife in ancient Egypt_: "weighed
  against the feather of the goddess Ma'at".

Sibling ecosystem names already in use: RANI, swarms.

## What it is (skeleton)

An installable Python package that weighs opinions: N-judge AI panel assembly with
nested panel sizes 3, 5, 7, 9, 11 and per-holding majority + dissent-shift comparison.
The first useful payload is the SHARDEX AI-panel record (7/11 judges, 2026-11-03).

```
$ maat weigh --raw C:/Users/clint/Documents/ai_panel_opinions_raw.json
```

## Layout

```
MAAT/
├── pyproject.toml          # installable: pip install -e ., console script `maat`
├── README.md
├── .gitignore
├── src/maat/
│   ├── __init__.py
│   ├── __main__.py         # python -m maat
│   ├── panel.py            # bench / panel slicing / per-holding tallies
│   └── cli.py              # `maat weigh --raw ...`
└── tests/test_panel.py     # stdlib unittest
```

## Roadmap (small, ordered)

1. ✅ Skeleton: packaging, CLI, panel tallies, tests
2. Judge-runtime module: provider adapters (the stochastic runner becomes importable `maat.judges`)
3. Decoy-control sweep leg (H2 in the SHARDEX record stays advisory until this exists)
4. Nested-panel report rendering (markdown/HTML)

## Honesty rule

A check that cannot run is neither a pass nor a failure — it is named, with reasons.
Unreachable judges are recorded as unreachable, never as verdicts. AI panel opinions
are not legally binding; the tool produces an opinion record with provenance.
