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
**Block:** CAPTCHA
**Workarounds tried:**
1. ❌ curl — CAPTCHA page
2. ❌ Automated browser — CAPTCHA
3. ✅ Manual browser — works, must be done by a human

### Portal: PA DOS Business Entity (file.dos.pa.gov)
**Block:** HTTP 403 on all scripted paths
**Workarounds tried:**
1. ❌ curl with various User-Agent headers
2. ❌ API paths (/api/*, /search/*)
3. ✅ Third-party mirrors: pennsylvaniadb.com/company/{entity_id}, bizapedia.com/pa/{company_name}
4. ✅ ProPublica indexing: includes entity registration data

### Portal: HHS TAGGS (taggs.hhs.gov)
**Block:** JavaScript SPA
**Workaround:** USASpending.gov API often has overlapping data. Try `api.usaspending.gov` first.

### Portal: SAM.gov
**Block:** JavaScript-heavy federal portal
**Workaround:** Check exclusion lists separately. Entity registration status is inferable from federal award drawdown data on USASpending.gov.

### Portal: PA Campaign Finance (campaignfinanceonline.pa.gov)
**Block:** Imperva CAPTCHA
**Workaround:**
1. ✅ FEC.gov (federal contributions only)
2. ✅ OpenSecrets.org
3. ✅ FollowTheMoney.org (state-level)
4. ❌ Direct PA portal — manual browser only

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
- `investigation-evidence-location` — Portal classification and gap mapping
- `investigation-regulatory-licenses` — FINRA and PALS queries
- `investigation-990-forensics` — ProPublica and IRS data extraction
