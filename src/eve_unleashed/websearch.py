"""websearch.py -- web search with five keyless providers, no single throat.

One source is a mirror with opinions. This module fans a query
across five providers that need no key -- Wikipedia search,
Library of Congress, Open Library, Crossref, and Stack Exchange --
and returns one deduplicated list where every hit names its
provider. A provider that is down, slow, or blocked reports an
error entry; it never sinks the others and is never counted as
zero results. That distinction is the whole module: `empty` means
the provider answered and found nothing, `error` means it could
not answer, and the two are never merged.

Discipline, stated: 12-second per-provider timeout, a named
User-Agent on every request, at most 5 hits kept per provider,
and deduplication by normalized URL. No scraping of HTML result
pages, no credentialed APIs, no query logging anywhere.
"""
import json as _json
import time as _time
import urllib.parse as _parse
import urllib.request as _request

try:
    from CORE.failure_ledger import note_failure
except Exception:
    def note_failure(where, exc=None):
        pass

_TIMEOUT = 12
_UA = {"User-Agent": "EveUnleashed-websearch/1.0 (research; keyless)"}
_PER_PROVIDER = 5

PROVIDERS = ("wikipedia", "loc", "openlibrary", "crossref",
             "stackexchange")


def _get(url):
    """One HTTP GET parsed as JSON. Returns (data, error)."""
    try:
        req = _request.Request(url, headers=_UA)
        with _request.urlopen(req, timeout=_TIMEOUT) as r:
            return _json.load(r), None
    except Exception as e:
        note_failure("websearch:get", e)
        return None, str(e)[:160]


def _wikipedia(query):
    url = ("https://en.wikipedia.org/w/api.php?action=query&list=search"
           "&srsearch=%s&format=json&srlimit=%d" % (_parse.quote(query),
                                                   _PER_PROVIDER))
    data, err = _get(url)
    if err:
        return {"via": "wikipedia", "state": "error", "detail": err,
                "hits": []}
    hits = [{"title": h.get("title", ""),
             "url": "https://en.wikipedia.org/wiki/" + _parse.quote(
                 h.get("title", "").replace(" ", "_")),
             "snippet": h.get("snippet", "").replace("<span class=\"searchmatch\">", "")
             .replace("</span>", "")[:200]}
            for h in (data or {}).get("query", {}).get("search", [])]
    return {"via": "wikipedia",
            "state": "ok" if hits else "empty",
            "detail": "%d hit(s)" % len(hits), "hits": hits[:_PER_PROVIDER]}


def _loc(query):
    url = "https://www.loc.gov/search/?q=%s&fo=json&c=%d" % (
        _parse.quote(query), _PER_PROVIDER)
    data, err = _get(url)
    if err:
        return {"via": "loc", "state": "error", "detail": err, "hits": []}
    hits = [{"title": r.get("title", ""),
             "url": r.get("url", ""),
             "snippet": ("%s -- %s" % (r.get("title", ""),
                                       r.get("date", "") or "undated"))[:200]}
            for r in (data or {}).get("results", [])]
    return {"via": "loc", "state": "ok" if hits else "empty",
            "detail": "%d hit(s)" % len(hits), "hits": hits[:_PER_PROVIDER]}


def _openlibrary(query):
    url = "https://openlibrary.org/search.json?q=%s&limit=%d" % (
        _parse.quote(query), _PER_PROVIDER)
    data, err = _get(url)
    if err:
        return {"via": "openlibrary", "state": "error", "detail": err,
                "hits": []}
    hits = [{"title": d.get("title", ""),
             "url": "https://openlibrary.org%s" % d.get("key", ""),
             "snippet": ", ".join(d.get("author_name", [])[:3])[:200]}
            for d in (data or {}).get("docs", [])]
    return {"via": "openlibrary", "state": "ok" if hits else "empty",
            "detail": "%d hit(s)" % len(hits), "hits": hits[:_PER_PROVIDER]}


def _crossref(query):
    url = "https://api.crossref.org/works?query=%s&rows=%d&select=title,URL,author,published" % (
        _parse.quote(query), _PER_PROVIDER)
    data, err = _get(url)
    if err:
        return {"via": "crossref", "state": "error", "detail": err,
                "hits": []}
    hits = []
    for item in (data or {}).get("message", {}).get("items", []):
        title = "; ".join(item.get("title", []))
        hits.append({"title": title,
                     "url": item.get("URL", ""),
                     "snippet": title[:200]})
    return {"via": "crossref", "state": "ok" if hits else "empty",
            "detail": "%d hit(s)" % len(hits), "hits": hits[:_PER_PROVIDER]}


def _stackexchange(query):
    url = ("https://api.stackexchange.com/2.3/search/advanced"
           "?order=desc&sort=relevance&q=%s&site=stackoverflow&pagesize=%d"
           % (_parse.quote(query), _PER_PROVIDER))
    data, err = _get(url)
    if err:
        return {"via": "stackexchange", "state": "error", "detail": err,
                "hits": []}
    hits = [{"title": it.get("title", ""),
             "url": it.get("link", ""),
             "snippet": "score %s, %s answer(s)" % (
                 it.get("score", "?"), it.get("answer_count", "?"))}
            for it in (data or {}).get("items", [])]
    return {"via": "stackexchange", "state": "ok" if hits else "empty",
            "detail": "%d hit(s)" % len(hits), "hits": hits[:_PER_PROVIDER]}


_FNS = {"wikipedia": _wikipedia, "loc": _loc,
        "openlibrary": _openlibrary, "crossref": _crossref,
        "stackexchange": _stackexchange}


def search(query, providers=PROVIDERS):
    """Fan out, isolate failures, dedupe by URL. Returns the bundle."""
    if not query or not query.strip():
        raise ValueError("nothing to search: empty query")
    wanted = [p for p in providers if p in _FNS]
    if not wanted:
        raise ValueError("no known providers named: %s" % (providers,))
    legs, seen, hits = [], set(), []
    for name in wanted:
        try:
            leg = _FNS[name](query.strip())
        except Exception as e:
            note_failure("websearch:%s" % name, e)
            leg = {"via": name, "state": "error",
                   "detail": str(e)[:160], "hits": []}
        for h in leg.get("hits", []):
            key = (h.get("url") or h.get("title", "")).lower().strip()
            if key and key not in seen:
                seen.add(key)
                hits.append({**h, "via": name})
        legs.append({"via": name, "state": leg.get("state", "error"),
                     "detail": leg.get("detail", "")[:160],
                     "kept": len([h for h in leg.get("hits", [])])})
    return {"query": query.strip(),
            "searched_utc": _time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                           _time.gmtime()),
            "legs": legs,
            "answered": sum(1 for l in legs if l["state"] != "error"),
            "hits": hits,
            "note": ("error legs could not answer and are not zeros; "
                     "empty legs answered with nothing found.")}
