"""BCC graph extension pass (2026-09-06).

Adds three user-requested structures to graphify-out/graph.json:
1. Person-to-harm attribution edges (corpus-graded: EXTRACTED vs INFERRED).
2. Person-to-document bipartite projection on canonical person nodes
   (consolidated via the Splink/RapidFuzz linkage clusters already in the corpus).
3. Recusal-cluster <-> Edward-Jones-cluster join through the documented
   Transparency Wall (HIDDEN_NETWORK Mechanism 4) and the Schedule L
   all-NO certification that covers BCC board members.

Accuracy constraints honored from the corpus:
- Goodman-Hinnershitz is NOT a BCC board member (City Council + COCA director),
  so she gets NO Schedule L coverage edge; she joins the wall via her
  recusal-record opacity (RECUSAL_EVIDENCE / HIDDEN_NETWORK Mechanism 3).
- H-7 (Blind Cliff) stays unattributed: the corpus attributes it to no person.
- Every new edge carries source_file + confidence + note.

Output: graphify-out/.graphify_extract.json (rebuilt from graph.json + additions).
"""
import json
from pathlib import Path

gpath = Path("graphify-out/graph.json")
g = json.loads(gpath.read_text(encoding="utf-8"))
edges = g.get("edges") or g.get("links")

# strip stale community fields for a clean rebuild
nodes = {}
for n in g["nodes"]:
    n = {k: v for k, v in n.items() if k not in ("community", "community_name")}
    nodes[n["id"]] = n

# degree map for picking the best existing node when labels collide
deg = {}
for e in edges:
    deg[e["source"]] = deg.get(e["source"], 0) + 1
    deg[e["target"]] = deg.get(e["target"], 0) + 1


def find(frag):
    """Best existing node id whose label or id contains frag (case-insensitive)."""
    frag = frag.lower()
    cands = [nid for nid, n in nodes.items()
             if frag in n.get("label", "").lower() or frag in nid.lower()]
    if not cands:
        return None
    cands.sort(key=lambda x: deg.get(x, 0), reverse=True)
    return cands[0]


new_nodes = []


def ensure(node_id, label, source_file, file_type="concept"):
    if node_id not in nodes:
        nodes[node_id] = {"id": node_id, "label": label, "file_type": file_type,
                          "source_file": source_file, "source_location": None,
                          "source_url": None, "captured_at": None, "author": None,
                          "contributor": "BCC extension pass 2026-09-06"}
        new_nodes.append(node_id)


new_edges = []


def edge(s, t, rel, conf, score, src, note):
    new_edges.append({"source": s, "target": t, "relation": rel, "confidence": conf,
                      "confidence_score": score, "source_file": src,
                      "source_location": None, "weight": 1.0, "note": note})


# ---- resolve anchors that must already exist ----
BCC = find("Berks Counseling Center")
EJ = find("Edward Jones")
COCA = find("Council on Chemical Abuse")
UW = find("United Way")
DOCS = {k: find(k) for k in [
    "EXPANDED_EVIDENCE", "Consolidated Scroll", "Harm Evidence Master",
    "PATIENT_HARM_REPORT", "HIDDEN_NETWORK", "HIDDEN_HARM_INFERENCE",
    "COMPLIANCE_SELF_DEALING", "RECUSAL_EVIDENCE", "CAMPAIGN_FINANCE",
    "EMPLOYEE_REVIEWS", "COI_REQUEST", "INVESTMENT_PEOPLE", "PEOPLE_DOSSIER",
    "BCC_TEMPORAL_KG", "BCC_RECORD_LINKAGE", "BCC_SPLINK", "DATA_REFERENCE",
    "INVESTIGATION_GAPS", "Donor Reconstruction", "Deep Dive Harm"]}
missing = {k: v for k, v in DOCS.items() if v is None}
if BCC is None or EJ is None or COCA is None:
    print("FATAL: anchor node missing", BCC, EJ, COCA)
    raise SystemExit(1)
print("missing doc anchors (edges to them will be skipped):", missing)

# ---- canonical persons (ensure) ----
P = {
    "gaul": find("brenda_gaul") or find("Brenda Gaul"),
    "seitz": find("crystal_seitz") or find("Crystal Seitz"),
    "plageman": find("joseph_plageman_jr") or find("Plageman"),
    "ralph": find("jeffrey_ralph") or find("Jeffrey Ralph"),
    "gh": find("marcia_goodman_hinnershitz") or find("Goodman-Hinnershitz"),
    "axford": find("christine_axford") or find("Axford"),
    "little": find("greg_little") or find("Greg Little"),
    "bromley": find("richard_bromley_jr") or find("Bromley"),
}
ensure("frances_malley", "Frances Malley (former CEO, left Jan 2019)", "HIDDEN_HARM_INFERENCE.html", "person")
ensure("linda_krause", "Linda Krause (BCC Director, Edward Jones)", "COMPLIANCE_SELF_DEALING_ANGLES.html", "person")
ensure("john_robinson", "John Robinson (BCC Treasurer FY2025, Robinson & Associates owner)", "COMPLIANCE_SELF_DEALING_ANGLES.html", "person")
ensure("missy_orlando", "Missy Orlando (BCC Director, United Way employee)", "COMPLIANCE_SELF_DEALING_ANGLES.html", "person")
ensure("robinson_associates_llc", "Robinson & Associates LLC (PA #3967553)", "COMPLIANCE_SELF_DEALING_ANGLES.html", "organization")
ensure("furniture_soup_inc", "Furniture Soup, Inc. (Gaul-owned vendor)", "COMPLIANCE_SELF_DEALING_ANGLES.html", "organization")
ensure("transparency_wall", "The Transparency Wall (Hidden Network Mechanism 4)", "HIDDEN_NETWORK.html", "concept")
ensure("schedule_l", "Schedule L (Related-Party Certification: all-NO)", "COMPLIANCE_SELF_DEALING_ANGLES.html", "document")
MALLEY, KRAUSE, ROBINSON, ORLANDO = "frances_malley", "linda_krause", "john_robinson", "missy_orlando"
RA, FS, WALL, SL = "robinson_associates_llc", "furniture_soup_inc", "transparency_wall", "schedule_l"

# ---- 1. identity consolidation (same_as) from linkage clusters ----
HHI = "HIDDEN_HARM_INFERENCE.html"
SDA = "COMPLIANCE_SELF_DEALING_ANGLES.html"
HN = "HIDDEN_NETWORK.html"
RE = "RECUSAL_EVIDENCE.html"
same_as = {
    P["plageman"]: ["coi_request_letter_plageman", "hidden_network_plageman",
                    "investment_people_report_joseph_plageman_jr", "plageman_joseph",
                    "scroll_record_plageman", "social_presence_leads_joseph_plageman_jr",
                    "bcc_temporal_kg_plageman_chair_interval"],
    P["seitz"]: ["coi_request_letter_seitz", "hidden_network_seitz", "scroll_record_seitz",
                 "social_presence_leads_crystal_seitz", "bcc_temporal_kg_seitz_chair_interval"],
    P["gaul"]: ["coi_request_letter_gaul", "hidden_network_gaul", "social_presence_leads_brenda_gaul"],
    P["ralph"]: ["coi_request_letter_ralph", "social_presence_leads_jeffrey_ralph"],
    P["gh"]: ["complaint_letter_goodman_hinnershitz", "recusal_evidence_marcia_goodman-hinnershitz",
              "scroll_record_goodman_hinnershitz", "social_presence_leads_marcia_goodman_hinnershitz"],
    P["axford"]: ["complaint_letter_axford", "social_presence_leads_christine_axford",
                  "scroll_letter_html_ceo_christine_axford", "axford"],
    P["little"]: ["complaint_letter_little", "investment_people_report_greg_little",
                  "scroll_letter_html_cfo_greg_little", "social_presence_leads_greg_little"],
    P["bromley"]: ["bromley_richard"],
}
sa_count = 0
for canon, variants in same_as.items():
    if not canon:
        continue
    for v in variants:
        if v in nodes and v != canon:
            edge(canon, v, "same_identity_as", "EXTRACTED", 1.0,
                 "BCC_RECORD_LINKAGE.html + BCC_SPLINK_LINKAGE.html",
                 "Identity variant consolidated per record-linkage clusters")
            sa_count += 1
print(f"identity edges: {sa_count}")

# ---- 2. officer/founder roles (EXTRACTED, FY2025 990 + Sep 3 2026 site addendum) ----
if BCC:
    edge(P["seitz"], BCC, "chairperson_of", "EXTRACTED", 1.0, "berkscc.org addendum Sep 3 2026 / FY2025 990", "Current Chairperson")
    edge(P["gaul"], BCC, "vice_president_of", "EXTRACTED", 1.0, "berkscc.org addendum Sep 3 2026 / FY2025 990", "Current Vice President")
    edge(P["ralph"], BCC, "treasurer_of", "EXTRACTED", 1.0, "berkscc.org addendum Sep 3 2026 / FY2025 990", "Current Treasurer")
    edge(P["plageman"], BCC, "former_chair_board_member_of", "EXTRACTED", 1.0, "FY2025 990 + Sep 3 2026 addendum", "No longer Chair; remains board member")
    edge(P["axford"], BCC, "ceo_of", "EXTRACTED", 1.0, "FY2025 990", "Chief Executive Officer")
    edge(P["little"], BCC, "cfo_of", "EXTRACTED", 1.0, "FY2025 990", "Chief Financial Officer")
    edge(KRAUSE, BCC, "director_of", "EXTRACTED", 1.0, "COMPLIANCE_SELF_DEALING_ANGLES.html B2", "Director, Edward Jones employee")
    edge(ROBINSON, BCC, "former_treasurer_board_member_of", "EXTRACTED", 1.0, "FY2025 990 + Sep 3 2026 addendum", "Treasurer per FY2025 990; replaced by Ralph on live site")
    edge(ORLANDO, BCC, "director_of", "EXTRACTED", 1.0, "COMPLIANCE_SELF_DEALING_ANGLES.html B2", "Director, United Way employee")
    edge(MALLEY, BCC, "former_ceo_of", "EXTRACTED", 1.0, "HIDDEN_HARM_INFERENCE.html H-2", "Left Jan 2019; still CMS NPI authorized official")

# ---- 3. employment / ownership / funding (EXTRACTED) ----
edge(P["plageman"], EJ, "employed_by", "EXTRACTED", 1.0, SDA, "FINRA CRD #5964768")
edge(KRAUSE, EJ, "employed_by", "EXTRACTED", 1.0, SDA, "22% board control from Edward Jones (2 of ~10 seats)")
edge(ROBINSON, RA, "owns", "EXTRACTED", 1.0, SDA, "PA entity #3967553, ACTIVE, inc. 2010-07-14")
edge(P["gaul"], FS, "owns", "EXTRACTED", 1.0, SDA, "Commercial vendor with state/municipal contracts")
edge(ORLANDO, UW, "employed_by", "EXTRACTED", 1.0, SDA, "UW granted BCC ~$685K incl. $678K MacKenzie Scott")
edge(P["gh"], COCA, "employed_by", "EXTRACTED", 1.0, RE, "Director of Planning & Resource Development, concurrent with ~20y council tenure")
edge(COCA, BCC, "funds", "EXTRACTED", 1.0, "DATA_REFERENCE.html", "$3.3M across 5 grants 2019-2023; largest non-federal funder")
if UW:
    edge(UW, BCC, "funds", "EXTRACTED", 1.0, "DATA_REFERENCE.html", "~$685K incl. MacKenzie Scott funds")

# ---- 4. person -> harm attribution edges ----
H = {
    1: "hidden_harm_inference_informed_choice_failure",
    2: "hidden_harm_inference_stale_federal_identity_harm",
    3: "hidden_harm_inference_same_payer_unadjudicated_practice_harm",
    4: "hidden_harm_inference_unaddressable_governance_harm",
    5: "hidden_harm_inference_history_reset_harm",
    6: "hidden_harm_inference_unmonitorable_influence_harm",
    7: "hidden_harm_inference_blind_cliff_harm",
    8: "hidden_harm_inference_quiet_escalation_staffing_harm",
}
if P["plageman"]:
    edge(P["plageman"], H[2], "named_in_harm_record", "EXTRACTED", 1.0, HHI,
         "H-2: NPI 1285951319 authorizes Plageman per corpus NPI trace; stale-record integrity harm")
if MALLEY:
    edge(MALLEY, H[2], "named_in_harm_record", "EXTRACTED", 1.0, HHI,
         "H-2: former CEO (left Jan 2019) still listed as authorized official on CMS NPI")
edge(P["axford"], H[8], "documented_in_harm_finding", "EXTRACTED", 1.0, HHI,
     "H-8: CEO pay inversion vs CFO documented in 990; frontline wage compression context")
edge(P["little"], H[8], "documented_in_harm_finding", "EXTRACTED", 1.0, HHI,
     "H-8: CFO out-earns CEO ($149,792 vs $145,432) with other-comp 3.2x; same finding")
edge(P["axford"], H[1], "disclosure_duty_harm", "INFERRED", 0.7, HHI,
     "H-1: rebuilt site publishes no compliance history; CEO owns disclosure surface (site, not person, is the actor)")
edge(P["seitz"], H[4], "governance_addressability_harm", "INFERRED", 0.7, HHI,
     "H-4: empty Leadership section defeats grievance first step; current Chairperson is the addressable governor")
edge(P["gaul"], H[4], "governance_addressability_harm", "INFERRED", 0.65, HHI,
     "H-4: VP; also Furniture Soup vendor status raises interested-party monitorability")
edge(P["ralph"], H[4], "governance_addressability_harm", "INFERRED", 0.65, HHI,
     "H-4: Treasurer; 403(b)/Form 5500 service-provider test sits in her/his office per H-8 cross-ref")
edge(P["plageman"], H[4], "governance_addressability_harm", "INFERRED", 0.65, HHI,
     "H-4: former Chair; Edward Jones dual role is the documented conflict H-4 asks patients to assess")
edge(P["gh"], H[6], "unmonitorable_channel_harm", "INFERRED", 0.7, HHI,
     "H-6: COCA $3.3M is the named unmonitorable channel; her dual council role is the decision-level gap")
print("harm attribution edges: 10")

# ---- 5. person -> document bipartite projection (mentioned_in, EXTRACTED) ----
def mi(person_key, doc_keys, note):
    p = P.get(person_key)
    if not p:
        return 0
    n = 0
    for dk in doc_keys:
        d = DOCS.get(dk)
        if d:
            edge(p, d, "mentioned_in", "EXTRACTED", 1.0, "semantic corpus", note)
            n += 1
    return n

mi_cnt = 0
mi_cnt += mi("plageman", ["INVESTMENT_PEOPLE", "COI_REQUEST", "HIDDEN_NETWORK",
                          "COMPLIANCE_SELF_DEALING", "Consolidated Scroll", "PEOPLE_DOSSIER",
                          "BCC_TEMPORAL_KG"], "Named subject in investigation artifact")
mi_cnt += mi("seitz", ["COI_REQUEST", "HIDDEN_NETWORK", "Consolidated Scroll",
                       "PEOPLE_DOSSIER", "BCC_TEMPORAL_KG"], "Named subject in investigation artifact")
mi_cnt += mi("gaul", ["COI_REQUEST", "HIDDEN_NETWORK", "COMPLIANCE_SELF_DEALING",
                      "Consolidated Scroll", "PEOPLE_DOSSIER"], "Named subject in investigation artifact")
mi_cnt += mi("ralph", ["COI_REQUEST", "HIDDEN_NETWORK", "Consolidated Scroll",
                       "PEOPLE_DOSSIER"], "Named subject in investigation artifact")
mi_cnt += mi("gh", ["RECUSAL_EVIDENCE", "CAMPAIGN_FINANCE", "HIDDEN_NETWORK",
                    "COMPLIANCE_SELF_DEALING", "INVESTIGATION_GAPS"], "Named subject in investigation artifact")
mi_cnt += mi("axford", ["HIDDEN_NETWORK", "EMPLOYEE_REVIEWS", "Consolidated Scroll",
                        "PEOPLE_DOSSIER"], "Named subject in investigation artifact")
mi_cnt += mi("little", ["HIDDEN_NETWORK", "EMPLOYEE_REVIEWS", "Donor Reconstruction",
                        "PEOPLE_DOSSIER"], "Named subject in investigation artifact")
# new persons
for pid, docs in [(KRAUSE, ["INVESTMENT_PEOPLE", "COMPLIANCE_SELF_DEALING"]),
                  (ROBINSON, ["COMPLIANCE_SELF_DEALING", "HIDDEN_NETWORK"]),
                  (ORLANDO, ["COMPLIANCE_SELF_DEALING", "HIDDEN_NETWORK"]),
                  (MALLEY, ["BCC_TEMPORAL_KG", "HIDDEN_HARM_INFERENCE"])]:
    for dk in docs:
        d = DOCS.get(dk)
        if d:
            edge(pid, d, "mentioned_in", "EXTRACTED", 1.0, "semantic corpus", "Named subject in investigation artifact")
            mi_cnt += 1
print(f"bipartite mentioned_in edges: {mi_cnt}")

# ---- 6. Transparency Wall join (recusal cluster <-> investment cluster) ----
edge(WALL, EJ, "conceals", "EXTRACTED", 1.0, HN,
     "Mechanism 4: investment manager identity not named in any public filing after exhaustive search")
edge(WALL, RA, "conceals", "EXTRACTED", 1.0, HN,
     "Mechanism 4: Schedule L certifies no related-party transactions; unverifiable publicly")
edge(WALL, UW, "conceals", "EXTRACTED", 1.0, HN, "Mechanism 4: recusal practices on UW funding votes unknown")
edge(WALL, COCA, "conceals", "EXTRACTED", 1.0, HN,
     "Mechanisms 3+4: COCA pass-throughs lack decision-level records; council minutes unsearchable")
edge(WALL, BCC, "conceals_governance_of", "EXTRACTED", 1.0, HN,
     "Mechanism 4: Schedule B redacted, Schedule O/J not public, staff directory unpublished")
edge(WALL, P["gh"], "conceals_record_of", "EXTRACTED", 1.0, RE,
     "Recusal/abstention record for ~20y council tenure requires manual minutes review (Gap #23)")
if "schedule_l" in nodes or SL in nodes:
    edge(SL, P["plageman"], "certifies_no_transaction_for", "EXTRACTED", 1.0, SDA,
         "Schedule L all-NO vs Edward Jones dual role: potential false IRS filing per corpus")
    edge(SL, KRAUSE, "certifies_no_transaction_for", "EXTRACTED", 1.0, SDA, "Schedule L all-NO coverage")
    edge(SL, ROBINSON, "certifies_no_transaction_for", "EXTRACTED", 1.0, SDA,
         "Schedule L all-NO vs Treasurer-owned consulting firm")
    edge(SL, P["gaul"], "certifies_no_transaction_for", "EXTRACTED", 1.0, SDA,
         "Schedule L all-NO vs Gaul-owned vendor")
    edge(SL, ORLANDO, "certifies_no_transaction_for", "EXTRACTED", 1.0, SDA,
         "Schedule L all-NO vs UW employer-grantor")
    edge(SL, EJ, "relates_to", "EXTRACTED", 1.0, SDA, "Investment-management contract existence is the Schedule L accuracy question")
    edge(SL, RA, "relates_to", "EXTRACTED", 1.0, SDA, "Any BCC contract would be a reportable interested-director transaction (15 Pa.C.S. 5728)")
    edge(SL, FS, "relates_to", "EXTRACTED", 1.0, SDA, "Monitor for BCC purchases")
    edge(SL, BCC, "filed_in", "EXTRACTED", 1.0, SDA, "FY2016-FY2025 990s certify all-NO")
print("transparency-wall join edges: 14")

# ---- merge & dedupe ----
existing = {(e.get("source"), e.get("target"), e.get("relation")) for e in edges}
added = 0
for e in new_edges:
    key = (e["source"], e["target"], e["relation"])
    if e["source"] in nodes and e["target"] in nodes and key not in existing:
        edges.append(e)
        existing.add(key)
        added += 1
for nid in new_nodes:
    nodes.setdefault(nid, nodes.get(nid))

extract = {
    "nodes": list(nodes.values()),
    "edges": edges,
    "hyperedges": g.get("hyperedges", []),
    "input_tokens": 0,
    "output_tokens": 0,
}
Path("graphify-out/.graphify_extract.json").write_text(
    json.dumps(extract, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"ADDED {added} edges ({len(new_nodes)} new nodes). "
      f"Total: {len(extract['nodes'])} nodes, {len(extract['edges'])} edges")
