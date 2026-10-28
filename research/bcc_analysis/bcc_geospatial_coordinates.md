# BCC Holdings — Geospatial Coordinates Report

**Task:** KILO-GEO-001 — BCC geospatial coordinates
**Date:** 2026-10-27
**Source:** US Census Bureau Geocoder (Public AR Current Benchmark)
**Method:** Census TIGER/Line address ranges — exact address match

---

## BCC Holdings — Verified Coordinates

### 1. 645 Penn St, Reading, PA 19601
**BCP/BCAP Office Location** — Berks Community Action Program, Rep. Guzman's office

| Field | Value |
|-------|-------|
| **Address** | 645 Penn St, Reading, PA 19601 |
| **Matched Address** | 645 PENN ST, READING, PA, 19601 |
| **Latitude** | 40.335329072021 |
| **Longitude** | -75.925068419143 |
| **TIGER Line ID** | 80445065 |
| **Side** | L (Left) |
| **Address Range** | 601–699 Penn St |
| **Census Benchmark** | Public AR Current |

**Notes:** 
- BCAP (Berks Community Action Program) headquarters at this address
- Rep. Manuel Guzman's Reading office on 5th floor
- Multiple NPI-registered healthcare providers at this address

---

### 2. 1800 N 12th St, Reading, PA 19604
**BCC/BCAP/TASC/Community Care Facility** — Former industrial (Stichler/Mega Candy), now Berkshire Psychiatric, Berkshire Wellness

| Field | Value |
|-------|-------|
| **Address** | 1800 North 12th Street, Reading, PA 19604 |
| **Matched Address** | 1800 N 12TH ST, READING, PA, 19604 |
| **Latitude** | 40.36213262106 |
| **Longitude** | -75.913540396939 |
| **TIGER Line ID** | 80377578 |
| **Side** | L (Left) |
| **Address Range** | 1800–1998 N 12th St |
| **Census Benchmark** | Public AR Current |

**Notes:**
- 5.32 acre industrial property, built 1930 (Stichler Products / Mega Candy)
- Current tenants: Berkshire Psychiatric, Berkshire Wellness Center (Oceans Healthcare), TASC
- BCC v Community Care docket (CCP 15-14644) involves this property
- Across from Albright College, behind Giant Food

---

### 3. 716 N Park Rd, Wyomissing, PA 19610
**Berkshire Psychiatric & Behavioral Health** — Multiple NPI-registered providers

| Field | Value |
|-------|-------|
| **Address** | 716 N Park Rd, Wyomissing, PA 19610 |
| **Matched Address** | 716 N PARK RD, WYOMISSING, PA, 19610 |
| **Latitude** | 40.344642872503 |
| **Longitude** | -75.957825285159 |
| **TIGER Line ID** | 80444133 |
| **Side** | R (Right) |
| **Address Range** | 700–798 N Park Rd (note: TIGER range direction reversed) |
| **Census Benchmark** | Public AR Current |

**Notes:**
- Located in Wyomissing borough (not Reading proper), ZIP 19610
- Berkshire Psychiatric & Behavioral Health Services, PC at this address
- Multiple NPI-registered providers: Melissa Conti PsyD, Christine Katzaman LPC, Carl Cesarz LPC, Nancy Hanley-Moyer LCSW, Janice Reichert CRNP
- Phone: 610-375-0544

---

## Summary Table

| # | Address | City | ZIP | Latitude | Longitude | TIGER Line ID |
|---|---------|------|-----|----------|-----------|---------------|
| 1 | 645 Penn St | Reading | 19601 | 40.335329072021 | -75.925068419143 | 80445065 |
| 2 | 1800 N 12th St | Reading | 19604 | 40.362132621060 | -75.913540396939 | 80377578 |
| 3 | 716 N Park Rd | Wyomissing | 19610 | 40.344642872503 | -75.957825285159 | 80444133 |

---

## Verification

All coordinates obtained via **US Census Bureau Geocoding API** (Public Address Ranges - Current Benchmark), which uses TIGER/Line shapefiles — the authoritative source for US address geocoding.

**API Endpoint:** `https://geocoding.geo.census.gov/geocoder/locations/onelineaddress`
**Benchmark:** Public_AR_Current
**Format:** JSON

**Query timestamp:** 2026-10-27T20:45:00Z

---

## Next Steps for KILO-GEO-001

- [x] Geocode all three BCC holdings addresses
- [x] Verify matches against known BCC entities (BCAP, TASC, Berkshire Psychiatric)
- [x] Document TIGER Line IDs for parcel linkage
- [ ] Cross-reference with Berks County GIS parcel data (PIN lookup)
- [ ] Cross-reference with Eagle mapping / property records
- [ ] Add to BCC network graph (nodes.csv/edges.csv) as geospatial attributes
- [ ] Feed into Gephi visualization for spatial layout

---

## Source Attribution

```
Source: US Census Bureau TIGER/Line Geocoder
Benchmark: Public Address Ranges - Current (Public_AR_Current)
Accessed: 2026-10-27
License: Public domain (US Government work)
```