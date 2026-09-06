---
name: investigation-osint
description: Open-source intelligence techniques for investigations — web scraping patterns, API discovery, blocked portal workarounds, CAPTCHA bypass documentation, OSINT toolkit. Distilled from the BCC investigation.
metadata:
  category: investigation
  project: bcc-investigation
  auto_load: false
  date_created: 2026-08-01
---

# Investigation: OSINT Techniques

## 🛑 DATA-COLLECTION GATE — assertion before live collection

**Gate owner for LIVE WEB COLLECTION / NETWORK DATA PULLS** (web scraping,
curl/API fetches, headed-browser/CDP pulls, bulk export sweeps against
THIRD-PARTY systems). The pre-action gates gate FILE-EDIT actions; collection
against live external systems is a separate action class that was outside
every gate until 2026-09-04 — exactly how repeated or unproven pulls wasted
hours (portal CAPTCHA walls, 404 deep-link confusion, headless-session
artifacts). Route: `pre-action-gate-lite` **Gate 0b**.

**Before launching ANY live collection (curl/API/headed-browser/sweep against
an external system — not a one-off `read_url`/`web_search`), print this
assertion in response text (NOT thinking):**

```text
🛑 [DATA-COLLECTION GATE]
- Source authorized/appropriate? (public channel, official export, or
  third-party mirror — is this pull within the user's standing scope?)
- One pull or sweep? (sweep = sized + logged + resumable per
  background-sweep-resilience — estimated duration known before launch)
- 404 ≠ blocked ≠ absent? (deep-link 404 may be a path fix; CAPTCHA may be a
  headless-session artifact; record WHICH state and move on — do not loop)
- Session/credential hygiene? (headed profile used ONLY where the wall
  demands it; cookies/session tokens never written to artifacts)
- Evidence preserved? (responses saved with retrieval date so a negative
  result is provable later — controlling full-export sweeps kept)
- GATE DECISION: [PROCEED / HALT — re-scope, size, or document first]
```

HALT rule: **a second pull at the same wall without a documented state change
(404→path fix, CAPTCHA→headed-session, blocked→public-records-request) =
CRITICAL** — looping a blocked channel is the exact 2026-09-04 waste this gate
prevents. When public channels are exhausted, the answer is a records request
or manual browser, not another automated attempt.

## API Discovery Pattern

Many government databases expose JSON APIs that are not documented publicly. The pattern for discovering them:

### Step 1: Check for API from the browser
Open DevTools → Network tab → filter by XHR/Fetch. Navigate the site and observe API calls.

### Step 2: Try common API paths
```bash
# FINRA
curl -H "Accept: application/json" "https://api.brokercheck.finra.org/search/individual/{ID}"

# ProPublica (no API needed — direct URL)
# https://projects.propublica.org/nonprofits/organizations/{EIN}

# USASpending
# https://api.usaspending.gov/api/v2/...

# IRS TEOS (Akamai-blocked but try)
curl -H "Accept: application/json" "https://apps.irs.gov/app/eos/..."
```

### Step 3: Try the search API first, detailed API second
- Search APIs are usually open (BrokerCheck: ✅)
- Detailed/individual APIs are often restricted (BrokerCheck detailed: ❌ 403)
- If search API returns data, use it. Document the detailed API as manual-only.

### Step 4: For JavaScript SPAs — try the underlying API
Many JS portals (React, Angular, Vue) call REST/GraphQL APIs. Find them in DevTools → Network.

## Blocked Portal Workaround Playbook

### Portal: PA PALS (pals.pa.gov)
**Block:** JavaScript SPA + CAPTCHA
**Workarounds tried:**
1. ❌ curl — returns empty HTML shell
2. ❌ headless browser — CAPTCHA triggers
3. ❌ API endpoint probing — no endpoints found
4. ⚠️ Third-party mirrors: pennsylvaniadb.com, bizapedia.com (partial data)
5. ✅ Manual browser — always works, just not scriptable

### Portal: PA UJS Portal (ujsportal.pacourts.us)
**Block (historical):** CAPTCHA — **SOLVED Sep 4, 2026** — same class as DOS/campaign finance: the "CAPTCHA" was a headless-session artifact.
**Working route (headed Chrome + CDP, persistent profile):**
1. Load `ujsportal.pacourts.us` in a headed Chrome with a persistent user-data-dir, drive over CDP (no challenge fires).
2. Case Search → Search By = **Organization** → OrganizationName = entity name → county = **ALL counties** (a satellite location can file elsewhere) → docket type.
3. Search each docket type separately (Civil / Landlord-Tenant / Criminal / etc.) — one matrix run per organization.
4. Result tables + pagination enumerate all cases; Court Summary / Docket Sheet links are PDFs served with the session's `dnh` token — fetch with the session cookies and extract with pypdf.
5. **CP-civil limit:** the public Case Information menu exposes only Appellate · Criminal CP · MDJ · Phila Municipal — Court of Common Pleas civil dockets are NOT publicly searchable; that slice needs the secure portal or a direct pacourts.us records request.
6. ✅ Manual browser — still always works

### Portal: PA DOS Business Entity (file.dos.pa.gov)
**Block:** HTTP 403 on all scripted paths; headless Chrome hits a Cloudflare wall (challenge unresolved after 180s)
**Workarounds tried:**
1. ❌ curl with various User-Agent headers
2. ❌ API paths (/api/*, /search/*)
3. ✅ Third-party mirrors: pennsylvaniadb.com/company/{entity_id}, bizapedia.com/pa/{company_name}
4. ✅ ProPublica indexing: includes entity registration data
5. ✅ **Headed (non-headless) Chrome + CDP with a persistent profile — PROVEN Sep 4, 2026** (real browser fingerprint passes Cloudflare on first load; see investigation-regulatory-licenses skill for the full step sequence: navigate → type entity into `input[placeholder*="Search by name or file number"]` → click `button[aria-label="Execute search"]` → expand row via inner `div[role=button]` → "View History" modal for filing dates + Control IDs).

### Portal: HHS TAGGS (taggs.hhs.gov)
**Block:** JavaScript SPA
**Workaround:** USASpending.gov API often has overlapping data. Try `api.usaspending.gov` first.

### Portal: SAM.gov
**Block:** JavaScript-heavy federal portal
**Workaround:** Check exclusion lists separately. Entity registration status is inferable from federal award drawdown data on USASpending.gov.

### Portal: PA Campaign Finance (campaignfinanceonline.pa.gov)
**Block (historical):** Imperva CAPTCHA — **SOLVED Sep 4, 2026** two ways.
**Working route 1 — official Full Export zips (CONTROLLING):**
1. pa.gov data-download page → official yearly **Full Campaign Finance Export zips** (contrib/filer/expense/receipt/debt tables).
2. Sweep locally with **first-name-qualified regexes** (the 200 MB+ tables otherwise flood common-surname false positives); join FilerID to isolate county-specific recipient committees (filer county 06 = Berks).
3. Covers 100% of reported contributions for the year — no CAPTCHA, no limits, no portal.
**Working route 2 — headed Chrome + CDP:** a headed session with a persistent profile passes the Imperva wall if live search is ever needed.
**Fallbacks (still useful for federal / third-party views):**
1. ✅ FEC.gov (federal contributions only)
2. ✅ OpenSecrets.org
3. ✅ FollowTheMoney.org (state-level)

## Web Search Patterns for Investigation

### Finding board member professional histories
```
Search: "[Name]" + "[Employer]" + "[City]" + LinkedIn
Search: "[Name]" + CRD + FINRA
Search: "[Name]" + CPA + Pennsylvania
Search: "[Name]" + "[Company]" + ZoomInfo
Search: "[Name]" + obituary (for family business connections)
```

### Finding organization relationships
```
Search: "[Org Name]" + "[Vendor Type]" + contract
Search: "[Org Name]" + lawsuit + Pennsylvania
Search: "[Org Name]" + grant + "[Funder Name]"
Search: "site:readingeagle.com [Org Name]"
Search: "[Org Name]" + review + complaint
```

## Critical API Commands

### FINRA BrokerCheck — Full Data Pull
```bash
# Basic search (always works)
curl -s -H "Accept: application/json" \
  -H "User-Agent: Mozilla/5.0" \
  "https://api.brokercheck.finra.org/search/individual/5964768"

# Extract key fields with Python
curl -s -H "Accept: application/json" \
  "https://api.brokercheck.finra.org/search/individual/5964768" | \
  python3 -c "  # On Windows bash, use 'python' not 'python3'
import sys, json
d = json.load(sys.stdin)
print('Name:', d.get('firstName'), d.get('lastName'))
print('Employer:', d.get('currentEmployments',[{}])[0].get('firmName'))
print('Disclosure:', d.get('disclosureFlag'))
print('OBA Comments:', d.get('brokerDetails',{}).get('hasBCComments'))
"
```

### USASpending.gov — Federal Award Search
```bash
# Search by recipient EIN
curl -s "https://api.usaspending.gov/api/v2/search/spending_by_award/" \
  -H "Content-Type: application/json" \
  -d '{"filters":{"recipient_search_text":["232043478"]},"fields":["Award ID","Award Amount","Action Date","Awarding Agency"]}'
```

### ProPublica Nonprofit Explorer
No API needed — direct URL pattern:
```
https://projects.propublica.org/nonprofits/organizations/{EIN}
```

## OSINT Verification Standard

Every finding must be verified by at least 2 independent sources:

| Finding | Source 1 | Source 2 | Source 3 | Confidence |
|---------|----------|----------|----------|------------|
| Robinson owns Robinson & Associates | LinkedIn | PA DOS Registry #3967553 | jrassociatesconsulting.com | ✅ Confirmed (3 sources) |
| Plageman CRD clean record | FINRA API | BrokerCheck web | N/A | ✅ Confirmed (2 sources) |
| Jeffrey Ralph at GSK | Name match | Regional proximity | Outreach profile | ⚠️ Inferred (circumstantial) |

**Confidence levels:**
- ✅ **Confirmed** — 2+ independent primary sources agree
- ⚠️ **Inferred** — circumstantial evidence, single source, or name/proximity match only
- ❌ **Unverified** — no independent confirmation

## Anti-Patterns

| ❌ Never | ✅ Always |
|----------|----------|
| Assume a web portal can be automated | Try API paths first; assume JavaScript SPAs need manual access |
| Use a single search engine or source | Google + Bing + DuckDuckGo for different indexing coverage |
| Accept a "no results" from one search method | Try: web search, API, third-party mirrors, manual browser |
| Confuse "not accessible remotely" with "doesn't exist" | Document: "PALS portal blocks scripted access — manual lookup required" |
| Publish findings with single-source verification | Every claim needs 2+ independent sources or is flagged as "inferred" |
| Scrape aggressively or evade CAPTCHAs | Respect rate limits. Document blocked paths. Use manual browser as fallback. |

## Tool Arsenal

| Tool | Purpose | Access Pattern |
|------|---------|---------------|
| `curl` + `Accept: application/json` | API probing | Always try first |
| `python3 -c "import json..."` (or `python` on Windows) | JSON extraction | Pipe curl output |
| `browser-use` agent | JavaScript SPA navigation | When curl fails |
| `researcher-web` agent | Web search | Broad OSINT queries |
| `researcher-docs` agent | Technical documentation | API docs, regulatory guidance |
| `basher` agent | Shell commands | curl, file ops, json parsing |
| Third-party mirrors | Blocked portal fallback | bizapedia, pennsylvaniadb, opencorporates |
| Manual browser | CAPTCHA-gated portals | Last resort — human required |

## Related Skills
- `pre-action-gate-lite` — Gate 0b routes live-collection actions to this skill's DATA-COLLECTION GATE.
- `investigation-evidence-location` — Portal classification and gap mapping
- `investigation-regulatory-licenses` — FINRA and PALS queries
- `investigation-990-forensics` — ProPublica and IRS data extraction
