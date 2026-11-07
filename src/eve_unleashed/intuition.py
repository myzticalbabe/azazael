"""Eve Unleashed -- native intuition (the supralogical rung).

Supralogical: the answer that arrives before the proof. intuit() never
touches the network -- it answers from Eve's own memory (the live
log): an exact memo of a past fetch, else a per-host prior, else
unknown. The ladder then proves or corrects the guess, and dream()
replays the stream to keep the priors honest.

Boundaries: intuition names a wall, never defeats one. A guess of
``blocked`` stops at rung zero and hands the URL to a human browser.
"""

from urllib.parse import urlparse

try:
    from CORE.failure_ledger import note_failure
except Exception:
    def note_failure(where, exc=None):
        pass

from .live_log import read_events


def _host(url):
    try:
        return (urlparse(str(url)).hostname or "").lower()
    except Exception as e:
        note_failure("intuition:host", e)
        return ""


def _fetch_rows(log_path):
    return [r for r in read_events(log_path)["records"]
            if r.get("phase") == "fetch" and r.get("event") == "answer"]


def intuit(url, log_path=None):
    """Guess how a fetch will answer, from memory only. No network."""
    url = str(url or "").strip()
    if not url:
        raise ValueError("nothing to intuit: empty url")
    host = _host(url)
    if not host:
        return {"state": "unknown", "confidence": 0.0,
                "predicted_rung": None,
                "provenance": ["unparseable url"]}
    rows = _fetch_rows(log_path)
    memo = [r for r in rows if r.get("url") == url]
    if memo:
        last = memo[-1]
        if last.get("state") == "ok":
            return {"state": "guess", "confidence": 0.9,
                    "predicted_rung": last.get("rung"),
                    "provenance": ["memo:%s" % last.get("rung")]}
        return {"state": "blocked", "confidence": 0.7,
                "predicted_rung": last.get("rung"),
                "provenance": ["memo:wall %s" % last.get("kind")]}
    host_rows = [r for r in rows if _host(r.get("url", "")) == host]
    if not host_rows:
        return {"state": "unknown", "confidence": 0.0,
                "predicted_rung": None,
                "provenance": ["no memo, no host prior"]}
    ok = [r for r in host_rows if r.get("state") == "ok"]
    rate = len(ok) / len(host_rows)
    modal = None
    if ok:
        counts = {}
        for r in ok:
            counts[r.get("rung")] = counts.get(r.get("rung"), 0) + 1
        modal = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    return {"state": "guess" if rate >= 0.5 else "blocked",
            "confidence": round(min(0.75, rate), 3),
            "predicted_rung": modal,
            "provenance": ["host:%s %d/%d answered" % (host, len(ok),
                                                       len(host_rows))]}


def dream(log_path=None):
    """Recalibrate: pair intuition guesses with the fetches that followed.

    Returns hit-rate per predicted rung plus a per-host answer table,
    all recomputed from the stream -- no stored weights to go stale.
    """
    recs = read_events(log_path)["records"]
    guesses = [r for r in recs if r.get("phase") == "fetch"
               and r.get("event") == "intuition" and r.get("url")]
    answers = [r for r in recs if r.get("phase") == "fetch"
               and r.get("event") == "answer" and r.get("url")]
    by_url = {}
    for a in answers:
        by_url.setdefault(a["url"], []).append(a)
    pairs, hits, by_rung = 0, 0, {}
    for g in guesses:
        later = [a for a in by_url.get(g["url"], [])
                 if a.get("ts", 0) >= g.get("ts", 0)]
        if not later:
            continue
        pairs += 1
        won = later[0].get("rung") == g.get("predicted") and \
            later[0].get("state") == "ok"
        hits += 1 if won else 0
        key = str(g.get("predicted"))
        cell = by_rung.setdefault(key, {"pairs": 0, "hits": 0})
        cell["pairs"] += 1
        cell["hits"] += 1 if won else 0
    hosts = {}
    for a in answers:
        h = _host(a.get("url", ""))
        cell = hosts.setdefault(h, {"fetches": 0, "answered": 0,
                                    "salience": 0.0})
        cell["fetches"] += 1
        cell["answered"] += 1 if a.get("state") == "ok" else 0
        # Salience: weight outcomes by surprise, not recency. A blocked
        # answer carries more weight than an ok one, so the dream
        # prioritises learning from failures (L4-b).
        cell["salience"] += 2.0 if a.get("state") != "ok" else 1.0
    return {"pairs": pairs, "hits": hits,
            "hit_rate": round(hits / pairs, 3) if pairs else 0.0,
            "by_rung": by_rung, "hosts": hosts}


def inhibited_rungs(host, log_path=None, threshold=0.5):
    '''Rungs that keep failing for this host and should be skipped.

    Inhibition (L4-a): if a host's answer rate is below ``threshold``,
    every rung that has produced a blocked answer for that host is
    inhibited.  Returns a set of rung names.  Empty set means nothing
    to skip.
    '''
    host = str(host or "").strip()
    if not host:
        return set()
    rows = _fetch_rows(log_path)
    host_rows = [r for r in rows if _host(r.get("url", "")) == host]
    if not host_rows:
        return set()
    ok = [r for r in host_rows if r.get("state") == "ok"]
    rate = len(ok) / len(host_rows)
    if rate >= threshold:
        return set()
    # Inhibit rungs that have produced blocked answers for this host.
    blocked_rungs = {r.get("rung") for r in host_rows
                     if r.get("state") != "ok" and r.get("rung")}
    return blocked_rungs
