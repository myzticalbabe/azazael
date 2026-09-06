---
name: investigation-provider-registry
description: Regulated-provider registry lookups — keyless API direct queries (CMS NPI), provider-identity hygiene audits (stale authorized official, address drift, taxonomy gaps), org-vs-practitioner record distinction. Distilled from the BCC investigation.
metadata:
  category: investigation
  project: bcc-investigation
  auto_load: false
  date_created: 2026-09-02
---

# Investigation: Provider Registry

## Overview
Direct API lookups against regulated-provider registries (healthcare, licenses, etc.) plus the provider-identity
hygiene audit that turns a registry row into a finding.

## Core Technique
- **Keyless API query (CMS NPI example):**
  `https://npiregistry.cms.hhs.gov/api/?version=2.1&organization_name=<Name>` — returns JSON
  (`results[]` with NPI, status, taxonomy, address, authorized official).
- **Hygiene audit axes:**
  - **Stale authorized official** — registered official vs current filings
  - **Address drift** — registered address vs current website/filings
  - **Taxonomy gaps** — registered taxonomies vs the entity's actual multi-program/multi-site footprint
- **Org vs practitioner:** distinguish the organization record (NPI-2) from practitioner records (NPI-1); a
  decades-old record with no updates is itself a finding (status ≠ currency).

## Case Example
- `bcc-npi-registry` (case-scoped) — 16-year-old NPI record, stale authorized official, address drift, taxonomy
  gaps vs the multi-site CCBHC footprint. Evidence: HIDDEN_ASPECTS_SWEEP.html.