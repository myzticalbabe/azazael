"""Portal census — what Scribe can actually drive, measured one portal at a time.

Scribe could only fill the forms it had been hand-coded for: five open-source
programmes, no academic funder and no individual-only funder anywhere in the
registry. The registry says where the doors are; this measures what kind of door
each one is, on the day it is run, and writes the answer where the next run reads
it.

Six states, and the action each implies for Scribe:

    FORM_STATIC  >=3 fillable fields INCLUDING a free-text textarea    -> DRIVE_NOW
    SEARCH_ONLY  one to three fields, usually a query box             -> NEEDS_HOP
    NO_FIELDS    page served, no fields at all                        -> NEEDS_HOP
    AUTH_WALL    a password field on the page                         -> NEEDS_CREDENTIALS
    REFUSED      401/403/407/429 -- a wall, not a form                -> NEEDS_STEALTH
    ERROR        non-2xx, DNS failure, timeout                        -> INVESTIGATE

The distinction that matters: `NO_FIELDS` on a JavaScript-rendered form means a
browser is required (Scribe has one), while `AUTH_WALL` means Scribe is the wrong
tool and a human with an account is the right one. Collapsing those into "failed"
is how a capability audit becomes a complaint.

The textarea requirement is not decoration. Two measured false positives bought
it on 2026-11-03: grants.gov's search panel (2 selects + 4 inputs) and Wellcome's
newsletter box (first name, last name, email, research select) both scored as
application forms under a field-count test. An application asks the applicant to
write something; a query panel and a signup box do not.

Usage:
    python tools/portal_census.py --selftest            # pure, no network
    python tools/portal_census.py --run                 # live log, writes data/portal_census.json
    python tools/portal_census.py --run --emit-programs  # also writes data/discovered_programs.json
    python tools/portal_census.py --run --expect nlnet_propose=FORM_STATIC

Exit codes: 0 ran and every expectation held; 1 an expectation failed; 2 the run
could not be performed at all. An unreachable third-party portal is a recorded
reading (HED-4/HED-6), not a failed run: it is printed, written into
portal_census.json with its error string, and counts 0 here. A gate that fails
when someone else's server is down gets switched off, and a switched-off gate
protects nothing. Stdlib only.
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

# Importing scribe is deliberate: the census must read forms with the same parser
# the form-filler uses. A second parser would let the census report a field count
# that the filler cannot reproduce, which is a capability claim and not a measurement.
try:
    from scribe import UNFILLABLE_TYPES, parse_form_schema  # noqa: E402
except SystemExit:  # scribe exits at import when playwright is missing
    print("portal_census: scribe.py cannot be imported (playwright missing?). "
          "The census reads forms through scribe's own parser, so it cannot run here.",
          file=sys.stderr)
    sys.exit(2)

DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
REGISTRY = DATA_DIR / "grant_portals.json"
CENSUS_OUT = DATA_DIR / "portal_census.json"
PROGRAMS_OUT = DATA_DIR / "discovered_programs.json"

STATE_FORM = "FORM_STATIC"
STATE_SEARCH = "SEARCH_ONLY"
STATE_NONE = "NO_FIELDS"
STATE_AUTH = "AUTH_WALL"
STATE_REFUSED = "REFUSED"
STATE_ERROR = "ERROR"

STATES = (STATE_FORM, STATE_SEARCH, STATE_NONE, STATE_AUTH, STATE_REFUSED, STATE_ERROR)

ACTION = {
    STATE_FORM: "DRIVE_NOW",
    STATE_SEARCH: "NEEDS_HOP",
    STATE_NONE: "NEEDS_HOP_OR_BROWSER",
    STATE_AUTH: "NEEDS_CREDENTIALS",
    STATE_REFUSED: "NEEDS_STEALTH",
    STATE_ERROR: "INVESTIGATE",
}

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

CLIENT_RENDER_MARKERS = re.compile(
    r'__NEXT_DATA__|data-reactroot|id="root"|id="app"\b|ng-version|tfaforms|'
    r'vue\.js|window\.__NUXT__', re.I)


def fillable_fields(schema: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Fields a person could type into: drops submit/button/file/hidden/check/radio."""
    out: Dict[str, Dict[str, Any]] = {}
    for name, spec in schema.items():
        if spec["tag"] in ("textarea", "select"):
            out[name] = spec
            continue
        if spec["type"] in UNFILLABLE_TYPES:
            continue
        out[name] = spec
    return out


def classify(status: int, html: str, final_url: str = "") -> str:
    """One page -> one state. Pure: no network, no state, no clock."""
    if status in (401, 403, 407, 429):
        return STATE_REFUSED
    if status == 0 or status >= 400:
        return STATE_ERROR
    schema = parse_form_schema(html or "")
    fields = fillable_fields(schema)
    has_password = any(spec["type"] == "password" for spec in schema.values())
    has_long = any(spec["tag"] == "textarea" for spec in fields.values())
    # A login page is a login page even when it has three ordinary inputs on it.
    if has_password and len(fields) <= 3:
        return STATE_AUTH
    # Free text is what separates an application from a query panel or a
    # mailing-list box. Count alone said "form" for both of those on 2026-11-03.
    if has_long and len(fields) >= 3:
        return STATE_FORM
    if len(fields) >= 1:
        return STATE_SEARCH
    if re.search(r"login|sign[-_ ]?in|account/", final_url or "", re.I):
        return STATE_AUTH
    return STATE_NONE


def fetch(url: str, timeout: int = 12) -> Tuple[int, str, str, int, str]:
    """GET one URL. Returns (status, html, final_url, bytes, error). Never raises.

    The error text is returned rather than swallowed: a status of 0 is a reading,
    and "ERROR" that cannot say whether it was DNS, TLS or a timeout is a state
    the next person has to re-derive by hand.
    """
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "identity",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(4_000_000)
            text = raw.decode(resp.headers.get_content_charset() or "utf-8", "replace")
            return resp.status, text, resp.geturl(), len(raw), ""
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read(200_000).decode("utf-8", "replace")
        except Exception:
            body = ""
        return exc.code, body, getattr(exc, "url", url), len(body), f"HTTP {exc.code} {exc.reason}"
    except Exception as exc:
        return 0, "", url, 0, f"{type(exc).__name__}: {exc}"


def census_one(portal: Dict[str, Any], timeout: int) -> Dict[str, Any]:
    started = time.time()
    status, html, final, size, error = fetch(portal["url"], timeout=timeout)
    elapsed_ms = int((time.time() - started) * 1000)
    state = classify(status, html, final)
    fields = fillable_fields(parse_form_schema(html or "")) if html else {}
    return {
        "id": portal["id"],
        "name": portal["name"],
        "category": portal["category"],
        "audience": portal.get("audience", []),
        "region": portal.get("region", ""),
        "role": portal.get("role", ""),
        "url": portal["url"],
        "final_url": final if final != portal["url"] else "",
        "http_status": status,
        "bytes": size,
        "ms": elapsed_ms,
        "error": error,
        "state": state,
        "action": ACTION[state],
        "client_rendered": bool(CLIENT_RENDER_MARKERS.search(html or "")),
        "field_count": len(fields),
        "fields": {n: {"tag": s["tag"], "type": s["type"], "required": s["required"],
                       "maxlength": s["maxlength"], "options": len(s["options"])}
                   for n, s in sorted(fields.items())},
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def to_program(record: Dict[str, Any]) -> Dict[str, Any]:
    """A measured form -> a GrantProgram-shaped entry Scribe can actually open.

    Field keys stay exactly as the form names them; scribe.FIELD_ALIASES already
    bridges the profile vocabulary (project_name -> project, contact_email ->
    email), so no second mapping table is invented here.
    """
    fields: Dict[str, str] = {}
    for name, spec in record["fields"].items():
        if spec["tag"] == "textarea":
            selector = f'textarea[name="{name}"]'
        elif spec["tag"] == "select":
            selector = f'select[name="{name}"]'
        else:
            selector = f'input[name="{name}"]'
        fields[name] = selector
    return {
        "key": f"census_{record['id']}",
        "name": record["name"],
        "url": record["url"],
        "description": f"Discovered by tools/portal_census.py on {record['checked_at']} "
                       f"({record['state']}, {record['field_count']} fillable fields) — "
                       f"{record['category']}, audience {','.join(record['audience']) or 'unspecified'}",
        "fields": fields,
        "required_docs": [],
        "bypass_config": {},
        "submit_selector": "input[type='submit'], button[type='submit']",
        "success_indicators": ["submitted", "thank you", "received", "confirmation"],
        "form_available": True,
        "application_method": "web_form",
        "bounds": {},
        "source": "portal_census",
        "measured_at": record["checked_at"],
    }


def self_test() -> int:
    """Negative controls: each state must be reachable, and none may be a default."""
    failures: List[str] = []

    def check(name: str, got: Any, want: Any) -> None:
        ok = got == want
        print(f"  [selftest] {name}: {'ok' if ok else f'FAIL got={got!r} want={want!r}'}")
        if not ok:
            failures.append(name)

    check("plain text is not a form", classify(200, "<html><body>hello</body></html>"), STATE_NONE)
    check("search box only is SEARCH_ONLY, not a form",
          classify(200, '<form><input name="q" type="search"></form>'), STATE_SEARCH)
    check("three fields + textarea is a form",
          classify(200, '<form><input name="a" required><input name="b">'
                        '<textarea name="c" maxlength="4000"></textarea></form>'), STATE_FORM)
    # Both controls below are the real pages that produced false positives on
    # 2026-11-03, reduced to their shape. They must never score as a form again.
    check("grants.gov search panel is not an application form",
          classify(200, '<form><select name="dateRange"></select><input name="inp-CFDA">'
                        '<input name="inp-keywords"><input name="inp-opportunity-number">'
                        '<input name="search" maxlength="100"><select name="sortby"></select></form>'),
          STATE_SEARCH)
    check("wellcome newsletter box is not an application form",
          classify(200, '<form><input name="search"><input name="subscriberFirstName">'
                        '<input name="subscriberLastName"><input type="email" name="subscriberEmailAddress">'
                        '<select name="subscriberResearch"></select></form>'),
          STATE_SEARCH)
    check("four inputs and no textarea is a query panel",
          classify(200, '<form><input name="a"><input name="b"><input name="c"><input name="d"></form>'),
          STATE_SEARCH)
    check("email + password is AUTH_WALL, not SEARCH_ONLY",
          classify(200, '<form><input name="e" type="email"><input name="p" type="password">'
                        '<input type="submit"></form>'), STATE_AUTH)
    check("403 is REFUSED", classify(403, ""), STATE_REFUSED)
    check("429 is REFUSED", classify(429, ""), STATE_REFUSED)
    check("500 is ERROR", classify(500, ""), STATE_ERROR)
    check("status 0 (no response) is ERROR", classify(0, ""), STATE_ERROR)
    check("hidden/submit/file inputs do not make a form",
          classify(200, '<form><input type="hidden" name="t"><input type="file" name="f">'
                        '<input type="submit" name="s"></form>'), STATE_NONE)

    # Every state must be produced by at least one control above, or the state
    # machine has a branch nothing exercises.
    reached = {classify(200, "<html><body>hello</body></html>"),
               classify(200, '<form><input name="q"></form>'),
               classify(200, '<form><input name="a"><input name="b">'
                            '<textarea name="c"></textarea></form>'),
               classify(200, '<form><input name="p" type="password"></form>'),
               classify(403, ""), classify(500, "")}
    check("all six states reached by controls", sorted(reached), sorted(STATES))

    print(f"  [selftest] {'clean' if not failures else str(len(failures)) + ' failure(s)'}")
    return 1 if failures else 0


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(prog="portal_census", description=__doc__)
    parser.add_argument("--selftest", action="store_true", help="pure controls, no network")
    parser.add_argument("--run", action="store_true", help="census every registered portal")
    parser.add_argument("--emit-programs", action="store_true",
                        help="write measured FORM_STATIC portals to data/discovered_programs.json")
    parser.add_argument("--registry", default=str(REGISTRY))
    parser.add_argument("--timeout", type=int, default=12)
    parser.add_argument("--expect", action="append", default=[],
                        metavar="ID=STATE", help="assert a portal's state; repeatable")
    args = parser.parse_args(argv[1:])

    if args.selftest:
        return self_test()
    if not args.run:
        parser.print_help()
        return 2

    registry_path = Path(args.registry)
    if not registry_path.exists():
        print(f"registry missing: {registry_path}", file=sys.stderr)
        return 2
    portals = json.loads(registry_path.read_text(encoding="utf-8"))["portals"]

    log_path = LOGS_DIR / f"portal_census_{time.strftime('%Y%m%d_%H%M%S')}.log"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = open(log_path, "w", encoding="utf-8", errors="replace")
    real_stdout = sys.stdout

    class Tee:
        def write(self, s: str) -> int:
            real_stdout.write(s)
            log_file.write(s)
            log_file.flush()
            return len(s)

        def flush(self) -> None:
            real_stdout.flush()
            log_file.flush()

    sys.stdout = Tee()
    records: List[Dict[str, Any]] = []
    try:
        print("#" * 72)
        print(f"# PORTAL CENSUS — {len(portals)} portals, timeout {args.timeout}s")
        print(f"# log: {log_path}")
        print("# read-only: one GET per portal, nothing is opened, filled or submitted")
        print("#" * 72, flush=True)

        for portal in portals:
            print(f"\n=== {portal['id']}  [{portal['category']}]  {portal['url']}", flush=True)
            record = census_one(portal, args.timeout)
            records.append(record)
            print(f"    {record['state']:12s} {record['action']:22s} http={record['http_status']} "
                  f"{record['bytes']}B {record['ms']}ms fields={record['field_count']}"
                  f"{'  (client-rendered)' if record['client_rendered'] else ''}", flush=True)
            if record["error"]:
                print(f"      error: {record['error']}", flush=True)
            if record["fields"]:
                shown = list(record["fields"].items())[:6]
                for name, spec in shown:
                    cap = f" maxlen={spec['maxlength']}" if spec["maxlength"] else ""
                    req = " required" if spec["required"] else ""
                    print(f"      {spec['tag']:8s} {name}{req}{cap}", flush=True)
                if len(record["fields"]) > len(shown):
                    print(f"      ... {len(record['fields']) - len(shown)} more", flush=True)
            if record["final_url"]:
                print(f"      redirected to {record['final_url']}", flush=True)

        counts = {s: sum(1 for r in records if r["state"] == s) for s in STATES}
        by_category: Dict[str, Dict[str, int]] = {}
        for r in records:
            bucket = by_category.setdefault(r["category"], {s: 0 for s in STATES})
            bucket[r["state"]] += 1

        print(f"\n{'='*72}")
        print(f"{'PORTAL':26s} {'CATEGORY':26s} {'STATE':13s} ACTION")
        print(f"{'-'*72}")
        for r in records:
            print(f"{r['id']:26s} {r['category']:26s} {r['state']:13s} {r['action']}")

        print(f"\n{'='*72}")
        print("BY CATEGORY")
        for category, bucket in sorted(by_category.items()):
            filled = ", ".join(f"{s}={n}" for s, n in bucket.items() if n)
            print(f"  {category:26s} {filled}")

        drivable = [r["id"] for r in records if r["state"] == STATE_FORM]
        print(f"\nScribe can drive today ({len(drivable)}): {', '.join(drivable) or 'none'}")
        for state in (STATE_AUTH, STATE_REFUSED, STATE_ERROR, STATE_SEARCH, STATE_NONE):
            ids = [r["id"] for r in records if r["state"] == state]
            if ids:
                print(f"  {state:12s} -> {ACTION[state]:22s} {', '.join(ids)}")

        expectations: List[str] = []
        failed: List[str] = []
        for spec in args.expect:
            pid, _, want = spec.partition("=")
            got = next((r["state"] for r in records if r["id"] == pid), "<absent>")
            line = f"expect {pid} = {want} -> got {got}"
            (expectations if got == want else failed).append(line)
            print(f"[EXPECT] {'ok  ' if got == want else 'FAIL'} {line}")

        payload = {
            "_meta": {
                "schema": "scribe/portal-census@1",
                "registry": str(registry_path.name),
                "ran_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "portals": len(records),
                "counts": counts,
                "log": str(log_path.name),
                "notes": "Read-only census. A state is a measurement of one page at one "
                         "moment; a funder redesign invalidates it, so re-run before "
                         "trusting a row.",
            },
            "portals": records,
        }
        CENSUS_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                              encoding="utf-8")
        print(f"\nwrote {CENSUS_OUT.name}")

        if args.emit_programs:
            programs = [to_program(r) for r in records if r["state"] == STATE_FORM]
            # encoding="utf-8" is not optional here: on Windows write_text()
            # defaults to the locale codec, so ensure_ascii=False produced a
            # cp1252 file that scribe then failed to read as UTF-8 — the run
            # wrote a program list its own filler could not open.
            PROGRAMS_OUT.write_text(json.dumps(
                {"_meta": {"schema": "scribe/discovered-programs@1",
                           "emitted_at": payload["_meta"]["ran_at"],
                           "from": CENSUS_OUT.name,
                           "note": "Measured by the census, not written by hand. Scribe "
                                   "merges these into PROGRAMS at import when this file "
                                   "is present."},
                 "programs": programs}, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"wrote {PROGRAMS_OUT.name} with {len(programs)} program(s)")

        errors = [r["id"] for r in records if r["state"] == STATE_ERROR]
        print(f"\n{counts[STATE_FORM]} drivable | {counts[STATE_AUTH]} credential-walled | "
              f"{counts[STATE_REFUSED]} refused | {counts[STATE_SEARCH] + counts[STATE_NONE]} need a hop | "
              f"{counts[STATE_ERROR]} error")
        if errors:
            print("unreachable (recorded, not fatal): " + ", ".join(errors))
        if failed:
            print("expectations failed: " + "; ".join(failed))
        print(f"log: {log_path}")
        return 1 if failed else 0
    finally:
        sys.stdout = real_stdout
        log_file.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
