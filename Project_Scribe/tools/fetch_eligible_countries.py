"""Fetch NLnet's Horizon Europe eligible-country list into Project_Scribe/data/.

The list is the funder's own, verbatim, with the page and its stated revision
date recorded next to it -- so an ineligibility verdict can be traced to a
source rather than to a recollection.
"""
import json
import re
import pathlib
import urllib.request

URL = "https://nlnet.nl/OIS/european-dimension/"
OUT = pathlib.Path(__file__).resolve().parents[1] / "data" / "eligible_countries.json"

req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

# The list sits between the "last updated" sentence and the "Why do all" heading.
start = html.find("last updated on")
start = html.find("</p>", start)
end = html.find("Why do all of these countries")
block = html[start:end]

text = re.sub(r"<br\s*/?>", "\n", block, flags=re.I)
text = re.sub(r"</li>", "\n", text, flags=re.I)
text = re.sub(r"<[^>]+>", " ", text)
text = text.replace("\u2212", "\n").replace("\u2013", "\n")
text = re.sub(r"[ \t]+", " ", text)

# Two defects in the funder's own markup, corrected here rather than silently:
#   "Austria Azerbaijan" arrives with the comma missing between them;
#   "Vietnam - Wallis et Futuna Islands" arrives joined by a spaced dash.
CORRECTIONS = {
    "austria azerbaijan": ["Austria", "Azerbaijan"],
}

names = []
for line in text.splitlines():
    for part in re.split(r",|\s+-\s+", line):
        name = re.sub(r"^\s*[-–—]?\s*", "", part).strip(" .")
        if not name or len(name) < 3 or name.lower().startswith("list of horizon"):
            continue
        names.extend(CORRECTIONS.get(name.casefold(), [name]))

seen, countries = set(), []
for name in names:
    key = name.casefold()
    if key in seen:
        continue
    seen.add(key)
    countries.append(name)

OUT.parent.mkdir(parents=True, exist_ok=True)
payload = {
    "source": URL,
    "retrieved": "2026-11-03",
    "statement": ("People and organisations of these eligible countries can participate on the same "
                  "terms as those from EU member states; 60% of the funds must go to people from "
                  "this list for a European dimension."),
    "notes": ["Two entries were corrected where the source markup is malformed: a missing comma "
              "between Austria and Azerbaijan, and a spaced dash joining Vietnam to Wallis et "
              "Futuna Islands."],
    "horizon_europe": countries,
}
OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

print(f"wrote {OUT} with {len(countries)} entries")
for probe in ("United States", "Netherlands", "United Kingdom", "Canada", "Brazil", "Nigeria", "Kenya"):
    hit = probe.casefold() in seen
    print(f"  {'IN ' if hit else 'OUT'} {probe}")
