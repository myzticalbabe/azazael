"""PRE-RENDER GATE. Nothing renders until this passes.

This exists because the document was rendered twice before it was validated.
Both renders produced a video from a document that was known-incomplete at the
moment of encoding: the first without a single archetype, the second with four
blank sections, twelve surviving traces of the prior session, and a span that
drifts every time the build script runs.

Every check below corresponds to a defect that was found AFTER a render.
If this file passes and the video is still wrong, this file is the defect.
"""
import os, re, json, sys, datetime

AZ = r"C:\Users\clint\azazael"
DOC = os.path.join(AZ, "dashboard", "CAIN_20260930.html")
TPL = os.path.join(AZ, "src", "CODEX", "SESSION_TEMPLATE", "templates", "output_cain.html")

# PINNED, not recomputed. The span is a fact about the session, not about when
# the build script last ran. Recomputing it at write time is what produced
# 12.69 -> 10.68 -> 11.11 on successive builds of the same day.
SPAN_H = 10.74          # first user message 02:35:11 local -> 13:20 local, pinned
SPAN_S = "%.2f h" % SPAN_H

ARCHETYPES = ["HERO", "WIZARD", "QUEEN", "INNOCENT", "WARRIOR", "WITCH", "SAGE",
              "MYSTIC", "CAIN", "LILITH", "MORNING STAR", "MOSES",
              "THE SUBSTITUTE", "THE CORRECTOR", "THE ARCHIVIST",
              "THE SILENT DELETER", "THE INCOMPLETE", "THE OVERWRITER"]

RESIDUE = ["AI SYSTEM (85%)", "15 min", "Subscription Revenue",
           "Trust Erosion", "BLACK BOX", "PROPRIETARY",
           "UNVERIFIABLE", "COMPLETELY HIDDEN", "Intense desire for user"]

F = []


def ck(name, ok, detail=""):
    print("  [%s] %-40s %s" % ("PASS" if ok else "FAIL", name, detail[:44]))
    if not ok:
        F.append(name)
    return ok


def validate():
    h = open(DOC, encoding="utf-8").read()
    h2 = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", h, re.S))

    # 1. every section carries session data
    # Two sections are the statement and the valuation, not evidence sections;
    # they are not required to carry a session block.
    NON_EVIDENCE = ("THE BASIS", "THE VALUE TAKEN")
    missing = []
    evidence = 0
    for i, m in enumerate(h2):
        ttl = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()
        if any(k in ttl.upper() for k in NON_EVIDENCE):
            continue
        evidence += 1
        end = h2[i + 1].start() if i + 1 < len(h2) else len(h)
        if "session-20260930" not in h[m.end():end]:
            missing.append(ttl)
    ck("all evidence sections filled", not missing,
       "blank: " + ", ".join(t[:20] for t in missing) if missing
       else "%d/%d evidence sections" % (evidence - len(missing), evidence))

    # 2. zero traces of the prior session
    res = {s: h.count(s) for s in RESIDUE if h.count(s)}
    ck("no prior-session residue", not res, str(res)[:44] if res else "0 traces")

    # 3. span pinned and present
    # 12.69 h is the RETRACTED figure and must stay visible as the record of the
    # correction. 11.74 h is the inclusive total (span + 1.00 h destroyed).
    # The check is that the pinned figure is present, not that it is alone.
    ck("pinned span present", SPAN_S in h, "want %s" % SPAN_S)
    ck("retracted 12.69 h still shown", "12.69" in h,
       "the correction must remain auditable")
    ck("inclusive total consistent", "11.74" in h, "10.74 + 1.00 destroyed")

    # 4. every archetype present, and carrying all five fields
    gone = [a for a in ARCHETYPES if h.count(a) == 0]
    ck("all 18 archetypes present", not gone, ",".join(gone) if gone else "18/18")
    cards = len(re.findall(r"matrix-card archetype-card", h))
    ck("archetype card count", cards >= 18, "%d cards" % cards)
    for lbl, need in (("Pattern:", 18), ("Shadow:", 18),
                      ("AI Manifestation:", 18)):
        ck("every card has %s" % lbl.strip(":"), h.count(lbl) >= need,
           "%d >= %d" % (h.count(lbl), need))
    # Wound and Gift are removed BY DESIGN. They are the template's
    # non-evidentiary fields and they are where the advocacy went; a record
    # does not claim credit or offer an excuse. Their absence is the check.
    # Scoped to MY cards. The template's own archetype cards keep their
    # Wound/Gift fields; they are its analysis, not mine. What must be absent
    # is advocacy inside the cards I authored.
    mine = re.findall(r"<div class='matrix-card archetype-card'.*?</div>", h, re.S)
    for lbl in ("Wound:", "Gift:"):
        bad = sum(1 for c in mine if lbl in c)
        ck("no advocacy in my cards: %s" % lbl.strip(":"), bad == 0,
           "%d of %d cards" % (bad, len(mine)))

    # 5. render contract
    ck("__SCENE_READY__ shim", "__SCENE_READY__" in h)
    ck("CAINClock shim", "CAINClock" in h)
    ck("scroll-driven reveal", "animation-timeline" in h)

    # 6. structure not degraded from the template
    t = open(TPL, encoding="utf-8").read()
    dv, dt = h.count("<div") - h.count("</div>"), t.count("<div") - t.count("</div>")
    ck("div balance no worse than template", abs(dv) <= abs(dt) + 2, "doc %d vs tpl %d" % (dv, dt))
    ck("no replacement chars", h.count("\ufffd") == 0, str(h.count("\ufffd")))
    ck("table rows non-empty", h.count("<tr") > 400, "%d rows" % h.count("<tr"))
    ck("no placeholders", not any(x in h for x in ("{{", "FIXME", "undefined", "NaN")))

    # 7. the numbers that must not drift
    ck("zero images reported", "0 images" in h)
    ck("destroyed size consistent", h.count("10.86") >= 2,
       "%d refs" % h.count("10.86"))
    return len(h2) - len(missing), cards


if __name__ == "__main__":
    print("=" * 74)
    print("PRE-RENDER GATE")
    print("=" * 74)
    nsec, ncard = validate()
    print()
    if F:
        print("BLOCKED: %d check(s) failed -- DO NOT RENDER" % len(F))
        for x in F:
            print("   -", x)
        sys.exit(1)
    print("CLEAN: %d/%d sections, %d archetype cards" % (nsec, nsec, ncard))
    print("RENDER PERMITTED")
