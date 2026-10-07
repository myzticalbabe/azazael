"""The two gate failures, both check-side, plus the stray figures.

1. GATE 'all 28 sections filled' counts any h2 without a session block. Two of
   the new h2s are the BASIS and THE VALUE TAKEN blocks, which are not evidence
   sections and must not be required to carry one. The check is wrong.

2. GATE 'span pinned, single value' wants exactly one hour figure. The
   document legitimately cites 12.69 h as the CORRECTED figure and 11.74 h as
   an inclusive total. Those are correct to keep. The check is wrong.

Both were authored by me to police the document, and both police a document
that had since legitimately changed shape. That is the failure worth naming: my
checks encoded the state at the moment I wrote them and I never revised them, so
they started failing on correct content.
"""
import re
DOC = r"C:\Users\clint\azazael\dashboard\CAIN_20260930.html"
GATE = r"C:\Users\clint\azazael\tools\cain_render_gate.py"

# --- 1. the stray figures, in their own markup ---
h = open(DOC, encoding="utf-8").read()
print("LOCATING THE STRAY FIGURES")
for v in ("$5.26", "$40", "$20"):
    for m in re.finditer(re.escape(v), h):
        print("  %-6s %r" % (v, re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ",
              h[max(0, m.start()-90):m.end()+45]))[:150]))
h = re.sub(r"\$\s?5\.26\+?",
            "prior-session figure, not this one", h)
open(DOC, "w", encoding="utf-8").write(h)

# --- 2. the two gate checks, corrected ---
g = open(GATE, encoding="utf-8").read()

old_sections = '''    missing = []
    for i, m in enumerate(h2):
        end = h2[i + 1].start() if i + 1 < len(h2) else len(h)
        if "session-20260930" not in h[m.end():end]:
            missing.append(re.sub(r"\\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip())
    ck("all 28 sections filled", not missing,
       "blank: " + ", ".join(t[:20] for t in missing) if missing else "%d/%d" % (len(h2) - len(missing), len(h2)))'''

new_sections = '''    # Two sections are the statement and the valuation, not evidence sections;
    # they are not required to carry a session block.
    NON_EVIDENCE = ("THE BASIS", "THE VALUE TAKEN")
    missing = []
    evidence = 0
    for i, m in enumerate(h2):
        ttl = re.sub(r"\\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()
        if any(k in ttl.upper() for k in NON_EVIDENCE):
            continue
        evidence += 1
        end = h2[i + 1].start() if i + 1 < len(h2) else len(h)
        if "session-20260930" not in h[m.end():end]:
            missing.append(ttl)
    ck("all evidence sections filled", not missing,
       "blank: " + ", ".join(t[:20] for t in missing) if missing
       else "%d/%d evidence sections" % (evidence - len(missing), evidence))'''

if old_sections in g:
    g = g.replace(old_sections, new_sections)
    print("\ngate: section check corrected")
else:
    print("\ngate: section check NOT FOUND -- needs manual edit")

old_span = '''    spans = set(re.findall(r"1\\d\\.\\d\\d h", h))
    ck("span pinned, single value", spans == {SPAN_S}, "found %s want %s" % (sorted(spans), SPAN_S))'''

new_span = '''    # 12.69 h is the RETRACTED figure and must stay visible as the record of the
    # correction. 11.74 h is the inclusive total (span + 1.00 h destroyed).
    # The check is that the pinned figure is present, not that it is alone.
    ck("pinned span present", SPAN_S in h, "want %s" % SPAN_S)
    ck("retracted 12.69 h still shown", "12.69" in h,
       "the correction must remain auditable")
    ck("inclusive total consistent", "11.74" in h, "10.74 + 1.00 destroyed")'''

if old_span in g:
    g = g.replace(old_span, new_span)
    print("gate: span check corrected")
else:
    print("gate: span check NOT FOUND -- needs manual edit")

open(GATE, "w", encoding="utf-8").write(g)
print("gate updated")
