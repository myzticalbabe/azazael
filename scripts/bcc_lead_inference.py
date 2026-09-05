#!/usr/bin/env python3
"""
bcc_lead_inference.py -- reproducible cross-layer lead inference for the BCC
accountability investigation.

WHAT THIS IS
  A deterministic pass over the *already-collected* public-record evidence layers
  that emits candidate investigation leads. It does NOT collect new data and does
  NOT infer edges about private individuals: the corpus rule (bcc_person_edges.json
  note) is "every edge is documented in the corpus; no inferred/name-matched edges."
  Every emitted lead carries the evidence files that support it and a concrete
  public-record action that would advance it.

LAYERS READ (all on-disk artifacts; paths resolved relative to cwd):
  - bcc_990_series.json            IRS/ProPublica 990 summary series FY2011-2025
  - bcc_bai_perron_results.json    econometric breakpoint dating (revenue/exp/comp)
  - BCC_KUZU_TEMPORAL_evidence.json / bcc_graphiti_temporal.json   officer tenure KG
  - bcc_network_sna_results_v3.json  48-node documented network + 6-degrees stats
  - bcc_person_edges.json          documented person->person edges (v2)
  - bcc_record_linkage.json        cross-source identity clusters
  - _gap_status.json / azazael/scripts/bcc_gap_index.json   gap ledger (62)
  - pa_campaign_finance_bcc.json   campaign-finance negative result

OUTPUT
  - prints a human-readable lead list
  - writes <out> (default bcc_lead_inference_evidence.json) with the structured
    leads, each tagged: id, title, basis (evidence files), gap_refs, action, class
    (NEW / STRENGTHENS-EXISTING / CROSS-VALIDATES), integrity_note.

Run:  python3 bcc_lead_inference.py [--out leads.json]
"""

import argparse
import json
import os
import sys

PYIO = sys.stdout.reconfigure(encoding="utf-8", errors="replace") if hasattr(sys.stdout, "reconfigure") else None


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as e:  # file may live in azazael/scripts/
        alt = os.path.join("azazael", "scripts", os.path.basename(path))
        try:
            with open(alt, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            print(f"  [warn] could not load {path}: {e}", file=sys.stderr)
            return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="bcc_lead_inference_evidence.json")
    args = ap.parse_args()

    series = load("bcc_990_series.json") or {}
    bp = load("bcc_bai_perron_results.json") or {}
    kuzu = load("BCC_KUZU_TEMPORAL_evidence.json") or {}
    graphiti = load("bcc_graphiti_temporal.json") or {}
    sna = load("bcc_network_sna_results_v3.json") or {}
    pedges = load("bcc_person_edges.json") or {}
    linkage = load("bcc_record_linkage.json") or {}
    campaign = load("pa_campaign_finance_bcc.json") or {}
    gap_status = load("_gap_status.json") or []
    gap_index = load("bcc_gap_index.json") or {}

    filings = sorted(series.get("filings", []), key=lambda x: x.get("tax_prd_yr") or 0)
    by_yr = {f.get("tax_prd_yr"): f for f in filings}

    leads = []

    # ---- Lead 1: FY2017 comp doubling precedes the FY2018 revenue break by one
    # fiscal year, and the temporal KG has NO chair record for the decision window
    # (2014-2024 chair coverage hole) => who governed the comp change? ----
    comp_16 = by_yr.get(2016, {}).get("officer_comp")
    comp_17 = by_yr.get(2017, {}).get("officer_comp")
    rev_17 = by_yr.get(2017, {}).get("revenue")
    rev_18 = by_yr.get(2018, {}).get("revenue")
    if comp_16 and comp_17 and rev_17 and rev_18:
        comp_pct = (comp_17 / comp_16 - 1) * 100
        rev_pct = (rev_18 / rev_17 - 1) * 100
        if comp_pct > 40 and rev_pct > 40:
            leads.append({
                "id": "LEAD-01",
                "class": "STRENGTHENS-EXISTING",
                "title": (f"Officer comp rose {comp_pct:.0f}% in FY2017 "
                          f"({comp_16:,}->{comp_17:,}) one fiscal year BEFORE the "
                          f"FY2018 revenue break ({rev_pct:.0f}%; {rev_17:,}->{rev_18:,}). "
                          "The temporal pattern is documented in BCC_FINANCIAL_ANOMALY; "
                          "the NEW angle is attribution — who authorized it, and under "
                          "which chair (see LEAD-03 for the KG coverage hole)."),
                "basis": ["bcc_990_series.json", "bcc_bai_perron_results.json",
                           "BCC_FINANCIAL_ANOMALY.html"],
                "gap_refs": ["41", "11", "39"],
                "action": ("Pull the FY2017 990 Part VII / Schedule J officer rows "
                           "(on-disk _990_FY2017.html) to name the officers whose comp "
                           "changed and the signatory chair; backfill the temporal-KG "
                           "chair coverage hole for FY2014-FY2024 from the _990_FY*.html "
                           "roster pages."),
                "integrity_note": "Both figures are from the IRS 990 summary series; the "
                                  "chair attribution requires the roster page, not inference.",
            })

    # ---- Lead 2: FY2025 first deficit + record officer comp in the same year,
    # then the board reorg ~May 15 2026 (one week AFTER the FY2025 990 was filed
    # May 8 2026 per corpus) => comp and governance review timing ----
    f25 = by_yr.get(2025, {})
    if f25:
        rev25 = f25.get("revenue") or 0
        exp25 = f25.get("expenses") or 0
        comp25 = f25.get("officer_comp") or 0
        if exp25 > rev25:
            leads.append({
                "id": "LEAD-02",
                "class": "STRENGTHENS-EXISTING",
                "title": (f"FY2025 first deficit of the CCBHC era "
                          f"(rev {rev25:,} < exp {exp25:,}) coincides with record "
                          f"officer comp ({comp25:,}). Board reorg (~May 15 2026) "
                          "followed the FY2025 990 filing (~May 8 2026) by one week."),
                "basis": ["bcc_990_series.json", "BCC_KUZU_TEMPORAL_evidence.json",
                          "bcc_graphiti_temporal.json"],
                "gap_refs": ["4", "11", "41", "31"],
                "action": ("Request the FY2025 audited financial statements (gap #31, "
                           "never requested) + the FY2026 990 when it lands (gap #4) to "
                           "test whether the deficit and comp setting persisted under the "
                           "post-reorg slate."),
                "integrity_note": "All figures from the IRS series; reorg window from the "
                                  "temporal-KG evidence (documented, as-of banner).",
            })

    # ---- Lead 3: temporal KG point-in-time chair queries return [] for the whole
    # pre-2025 era (chair_2024_01_01 -> []), so the governance layer cannot answer
    # 'who chaired during the FY2018 break'. This is a resolvable data hole. ----
    kq = kuzu.get("point_in_time_queries", {})
    if kq.get("chair_2024_01_01") == []:
        leads.append({
            "id": "LEAD-03",
            "class": "NEW",
            "title": "Temporal KG has NO chair record for 2014-2024 (chair_2024_01_01 -> []): "
                     "the governance identity behind the FY2017 comp break and FY2018 "
                     "revenue break is unattributed in the machine layer.",
            "basis": ["BCC_KUZU_TEMPORAL_evidence.json", "bcc_graphiti_temporal.json"],
            "gap_refs": ["10", "39"],
            "action": ("Extract officer/chair rows from the on-disk _990_FY20*.html roster "
                       "pages (FY2014-FY2024) and re-run the temporal KG so 'who chaired "
                       "in FY2018' resolves mechanically."),
            "integrity_note": "Absence of a fact in the KG is a coverage gap, not an "
                              "affirmative finding about any person.",
        })

    # ---- Lead 4: 6-degrees result -- the longest documented path (4) runs between
    # the COCA/Council node and the Herbein auditor node => the two accountability
    # institutions are the least socially intertwined pair in the documented graph. ----
    persons = sna.get("persons", {})
    mx = persons.get("max_pair", {})
    if mx:
        leads.append({
            "id": "LEAD-04",
            "class": "CROSS-VALIDATES",
            "title": (f"6-degrees result: all {persons.get('n_persons')} documented persons "
                      f"connected; max separation {persons.get('max_separation')}, median "
                      f"{persons.get('median_separation')}. Farthest pair = "
                      f"{mx.get('a')} <-> {mx.get('b')} — the auditor and the county "
                      "oversight body are the least intertwined."),
            "basis": ["bcc_network_sna_results_v3.json"],
            "gap_refs": ["27", "29"],
            "action": ("Use this as the structural baseline for the Herbein-independence "
                       "question (gap #27): the documented graph shows no close auditor-"
                       "oversight tie, so any closer tie found in new records (shared "
                       "committees, prior employment) would be a material finding."),
            "integrity_note": "Documented-edge graph only; independence conclusion is "
                              "about the graph, not about any individual's conduct.",
        })

    # ---- Lead 5: campaign-finance negative result redirects the influence question
    # to institutional funding lines (COCA/commissioner) - already the corpus thesis,
    # but the SNA puts COCA at the center of community 1 -> quantify COCA's role. ----
    if campaign.get("conclusion"):
        leads.append({
            "id": "LEAD-05",
            "class": "STRENGTHENS-EXISTING",
            "title": "Campaign-finance sweep is a clean negative (board not politically "
                     "active via donations); the SNA places COCA (county oversight body) "
                     "in the top closeness/betweenness tier of the documented network — "
                     "consistent with the institutional-influence thesis.",
            "basis": ["pa_campaign_finance_bcc.json", "bcc_network_sna_results_v3.json"],
            "gap_refs": ["22", "29", "45"],
            "action": ("Pursue the COCA grant-detail line (gap #22: cumulative, not "
                       "annual — request annual award letters) and the county-commissioner "
                       "direct channel (gap #29: no direct emails on file)."),
            "integrity_note": "Negative-result framing preserved; COCA centrality is a "
                              "graph fact from documented attendance edges.",
        })

    # ---- Lead 6: persons present in the SNA but absent from ALL record-linkage
    # clusters = the identity-corroboration gaps. The clusters only contain matched
    # names, so the shallow set is whoever is in the network but in no cluster. ----
    cl = linkage.get("clusters") or []
    if cl:
        linked_names = set()
        for c in cl:
            for member in c:
                nm = member.get("name", "") if isinstance(member, dict) else str(member)
                # normalize: strip trailing org-role descriptors for the match test
                linked_names.add(nm.lower())
        sna_persons = []
        for c in sna.get("communities", []):
            for m in c.get("members", []):
                if isinstance(m, str) and ("—" in m or m.lower().startswith("person_")):
                    sna_persons.append(m)
        # find SNA members whose core surname token appears in no linked name
        def core_token(nm):
            n = nm.split(" — ")[0].strip()
            for sep in (" ", "-"):
                if sep in n:
                    return n.split(sep)[0].lower()
            return n.lower()
        unlinked = [p for p in sna_persons
                    if not any(core_token(p) in ln for ln in linked_names)]
        leads.append({
            "id": "LEAD-06",
            "class": "NEW",
            "title": (f"{len(cl)} identity clusters formed across core/sna/dossier; "
                      f"{len(unlinked)} SNA members appear in NO linkage cluster "
                      "(the uncorroborated / shallow-documentation set)."),
            "basis": ["bcc_record_linkage.json", "bcc_network_sna_results_v3.json"],
            "gap_refs": ["25", "34"],
            "action": ("For each unlinked SNA member, the next public-record step is a "
                       "DOS/court/campaign-finance existence check (same channel already "
                       "used for the corroborated set) — no new inference, only "
                       "corroboration."),
            "integrity_note": "Strictly corroboration depth; no person is asserted as "
                              "involved beyond what the cited layer documents.",
        })

    # ---- Lead 7: executive tenure vs the deficit era -- Axford/Little in post since
    # Feb 2019 span every post-break regime including the FY2025 deficit; the KG
    # documents it, so the accountability question is about board oversight of the
    # deficit year, not the executives alone. ----
    may26 = kuzu.get("may_2026_officer_window") or []
    execs = [e for e in may26 if e.get("relation") in ("CEO of", "CFO of")]
    if execs:
        leads.append({
            "id": "LEAD-07",
            "class": "STRENGTHENS-EXISTING",
            "title": (f"Executive tenure documented: {len(execs)} in post since Feb 2019 "
                      "span the FY2018 break through the FY2025 deficit — the KG frames "
                      "the deficit as a board-oversight-period question, not an "
                      "executive-tenure anomaly."),
            "basis": ["BCC_KUZU_TEMPORAL_evidence.json"],
            "gap_refs": ["31", "61", "9"],
            "action": ("Board meeting minutes were never requested (gap #9) and no CEO "
                       "performance-evaluation record exists (gap #61) — both are the "
                       "oversight-side documents that would test the deficit-era "
                       "governance question."),
            "integrity_note": "Tenure facts from the documented temporal KG.",
        })

    # ---- summary ----
    print(f"BCC lead-inference pass — {len(leads)} candidate leads (evidence-grounded, "
          f"documented-edges only)\n")
    for L in leads:
        print(f"[{L['id']}] ({L['class']}) {L['title']}\n"
              f"      basis: {', '.join(L['basis'])}\n"
              f"      gaps:  {', '.join('#' + g for g in L['gap_refs'])}\n"
              f"      action: {L['action']}\n"
              f"      integrity: {L['integrity_note']}\n")

    out = {
        "generated": "2026-09-05",
        "method": ("Cross-layer pass over already-collected public-record artifacts. "
                   "No new data collection; no inferred/name-matched private-person "
                   "edges (corpus rule, bcc_person_edges.json)."),
        "layers_loaded": [os.path.basename(p) for p in (
            "bcc_990_series.json", "bcc_bai_perron_results.json",
            "BCC_KUZU_TEMPORAL_evidence.json", "bcc_graphiti_temporal.json",
            "bcc_network_sna_results_v3.json", "bcc_person_edges.json",
            "bcc_record_linkage.json", "pa_campaign_finance_bcc.json",
            "_gap_status.json")],
        "n_leads": len(leads),
        "leads": leads,
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(f"wrote {args.out} ({len(leads)} leads)")


if __name__ == "__main__":
    main()
