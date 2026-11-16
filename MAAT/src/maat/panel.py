"""Panel weighing logic.

Input is an opinions raw file: a JSON list of rows shaped like
``{"judge": {...,"id": N}, "result": {"ok": bool, "parsed": {...}}}``,
each parsed verdict carrying H1..H5 and a "dissent" sentence.
"""
from __future__ import annotations

import json
import pathlib

HOLDINGS = ("H1", "H2", "H3", "H4", "H5")


def load_raw(path: str | pathlib.Path) -> list[dict]:
    rows = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError(f"expected a JSON list of judge rows, got {type(rows).__name__}")
    return rows


def complete(row: dict) -> bool:
    """A judge row counts only when its verdict is genuinely usable."""
    res = row.get("result") or {}
    parsed = res.get("parsed")
    return bool(res.get("ok")) and isinstance(parsed, dict) and all(
        f"H{i}" in parsed for i in range(1, 6)) and "dissent" in parsed


def bench(rows: list[dict]) -> list[dict]:
    """Reachable, complete judges in bench (id) order."""
    ordered = sorted(rows, key=lambda r: (r.get("judge") or {}).get("id", 0))
    return [r for r in ordered if complete(r)]


def tally(rows: list[dict], size: int) -> dict:
    """Per-holding majority for the first `size` judges of the bench."""
    sub = rows[:size]
    t = {h: {"AFFIRM": 0, "REVERSE": 0} for h in HOLDINGS}
    dissent_named = 0
    for r in sub:
        p = r["result"]["parsed"]
        for h in HOLDINGS:
            v = str(p.get(h, "")).strip().upper()
            if v in t[h]:
                t[h][v] += 1
        d = (p.get("dissent") or "").strip().lower()
        if d and d != "none":
            dissent_named += 1
    return {"size": size, "judges": len(sub), "tally": t, "dissent_named": dissent_named}


def compare(path: str | pathlib.Path, sizes=None) -> tuple[list[dict], int]:
    """All requested panel sizes that the reachable bench can actually convene."""
    from . import PANEL_SIZES

    rows = bench(load_raw(path))
    n = len(rows)
    sizes = sizes or PANEL_SIZES
    panels = [tally(rows, s) for s in sizes if s <= n]
    return panels, n
