## FLOCK-CANON-v1.3 — flocking + ultra-loose sources (canonical, all lanes; mirrors /root/BCC-REINVESTIGATION/AGENTS.md)

- Flocks (exactly one per edge, all grades): `MONEY` dollar flows; `GOVERN` board/officer/exit/dual-board;
  `CLINIC` prescribers/panels/NPI/medical-director/EHR/DCO; `SITE` parcels/tenancies/co-tenants;
  `COURT` dockets/appeals/LT+CV/adjudications/counsel/venues; `SFI_NEG` ethics zeros + Schwank
  legislative-conduct; `UJS_NEG` participant/org zeros with CP-civil-blind caveat; `FUNDER`
  funders/regulators/auditors; `PIPE` intake-first `JAIL->TREATCT->TASC->BCC` + SOS/MHDD/CYS/CAC;
  `LEAD` name-only/snippet-only/unresolvable = next-sweep queue, never dropped.
- Sources ultra-loose (any lawful source; tier decides grade): portals re-query (UJS/Ethics/IRS/DOS/
  Socrata/property/campfin/FTM/OpenSecrets); minutes/bios, LinkedIn/FB/X/YT, NPI/license, voter-age,
  people-search, obits/yearbooks; Wayback/cache/archive.today, DocumentCloud, agenda packets, Eagle/
  Daily Review/Patch, BCTV, deal pages, AG/DOH dockets, Joint Commission, SAMHSA/FAC/Census,
  CourtListener, audits/990s beyond TY2024, Guidestar; RTK/FOIA drafts + prothonotary/recorder notes
  + phone/email confirmations (log who/when/what, no non-public PII). Old-tree + AI snippets = POINTERS only.
- Tiers: `A` primary doc (VERIFIED-eligible); `B` official index (identity/universe VERIFIED only);
  `C` credible secondary (VERIFIED only paired with A/B, else LEAD); `D` snippet/social/hearsay (LEAD-only, still log).
- Proof: raw+sha (`FETCH_LOG`|`FETCH_LOG-missing/direct`|`beam1-new`+url/fetched/tier) + granular quote
  (amount+date+names) + 2 identity keys (persons) / EIN-objectID (orgs), name-only=LEAD + universe label
  on every negative (universe-free=CUT). `edge_idx` 0-117 is identity; `flock` required on every edge.
- New-fetch rules: save to `00_raw/<beam>_<slug>.<ext>`, never overwrite; cite
  `{"raw","sha","sha_source","url","fetched","tier"}` (+transcribe screenshots); URL-only caps at LEAD
  `unsaved-browser-view-<date>`; gated-only=LEAD `gated-unverified` after free-mirror try; log all in
  `new_sources_log.md` (URL|UTC|tier|bytes|sha|raw-path|edge_idx|next-step). No FETCH_LOG.md edits outside Linux lane.
