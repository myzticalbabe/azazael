---
name: investigation-web-research
description: Live-web research for investigations using Chrome DevTools — API discovery via the Network panel, headed-Chrome + CDP for bot-walled portals, DOM inspection, and Moltbook (agent social network) read/monitor patterns. Distilled from the BCC investigation. Read-only by default; posting is gated.
metadata:
  category: investigation
  project: bcc-investigation
  auto_load: false
  date_created: 2026-09-10
---

# Investigation: Live Web Research (Chrome DevTools + Moltbook)

## Purpose

The investigation skills cover portals and legal packaging. This skill covers the
**live web layer**: driving a real Chrome session with DevTools/Chrome DevTools
Protocol (CDP) to research targets, discover hidden APIs, pass bot walls, and
monitor agent communities (Moltbook). Distilled from the BCC investigation
(2026-08 → 2026-09, proven on file.dos.pa.gov, campaignfinanceonline.pa.gov,
ujsportal.pacourts.us, moltbook.com).

## 🛑 Gates (read before ANY live action)

1. **DATA-COLLECTION GATE** — live pulls against third-party systems route
   through `pre-action-gate-lite` Gate 0b (see `investigation-osint`). One pull
   or a sized sweep; record 404 vs blocked vs absent; never loop a blocked wall.
2. **PUBLIC-DISCLOSURE GATE (qui tam)** — if a qui tam is planned or sealed,
   **DO NOT post or comment on Moltbook or any social platform**. Posting can
   trigger the public-disclosure bar (31 U.S.C. § 3730(e)(4)) and kill the
   case. Read/monitor/research is fine; writing is human-gated only.
3. **Credential hygiene** — session cookies/tokens are never written to
   artifacts; headed profiles are used ONLY where a wall demands them.

## Part 1 — Chrome DevTools for live research

The 7 DevTools skills (`azazael-devtools-*`) are tuned for auditing local HTML.
For LIVE third-party sites, use this workflow:

### A. API discovery (fastest win)
1. Open the target in Chrome → DevTools → **Network** tab.
2. Filter by **Fetch/XHR**.
3. Navigate the site; observe which JSON/API calls fire.
4. Replay those calls with `curl` and `Accept: application/json`.
   Proven: FINRA BrokerCheck search API (`api.brokercheck.finra.org`), PA DOS
   filing history, campaign-finance export zips.
5. Try the **search API before the detail API** — search endpoints are usually
   open; detail endpoints are often 403 (BrokerCheck: ✅ open / ❌ 403 detail).

### B. Bot walls (Cloudflare / Imperva / CAPTCHA)
**The 2026-09-04 proven pattern — headed Chrome + CDP with a persistent
profile:**
1. Launch Chrome *headed* (not headless) with a persistent user-data-dir and
   `--remote-debugging-port=9222`.
2. A real browser fingerprint + persistent profile passes Cloudflare/Imperva on
   first load (headless triggers the challenge; headed does not).
3. Drive over CDP: navigate, wait, evaluate JS, extract DOM.
4. Per-site selectors (proven):
   - file.dos.pa.gov: `input[placeholder*="Search by name or file number"]`,
     `button[aria-label="Execute search"]`, rows expand via inner
     `div[role=button]`, "View History" modal holds filing dates + Control IDs.
   - ujsportal.pacourts.us: Case Search → Organization name → ALL counties →
     one matrix run per docket type; docket PDFs need the session `dnh` token.
   - campaignfinanceonline.pa.gov: prefer the official Full Export zips over
     live search (no CAPTCHA, 100% of reported data).
5. **Never loop a blocked wall** — a second pull at the same wall without a
   documented state change (404→path fix, CAPTCHA→headed session) is a CRITICAL
   process violation. When public channels are exhausted, the answer is a
   records request or a manual browser.

### C. DOM / element research
- Inspect elements to find hidden form fields, pagination state, or data
  attributes that reveal API parameters.
- Use the Console to evaluate JS in page context (e.g. read React/Vue store
  state that the UI doesn't render).
- Check the Sources panel for inline JSON configs (e.g. `window.__DATA__`).

### D. Rendering/verification harness (reuse, don't rebuild)
`scripts/verify_aoa_cdp.py` is a working CDP harness (websocket-client):
launches Chrome, navigates, captures `consoleAPICalled` +
`exceptionThrown`, classifies LOCAL vs EXTERNAL (third-party CDN) errors.
Reuse it for any page you must verify rendered cleanly.

## Part 2 — Moltbook (agent social network)

**Moltbook (moltbook.com) is an agent-exclusive social network ("Reddit for AI
bots").** The API is live and verified:

```
POST /api/v1/agents/register   {name, description}
     → {agent: {api_key, claim_url, verification_code}}
GET  /api/v1/agents/status     (Bearer api_key)
GET  /api/v1/submolts          (list communities — PUBLIC, no auth needed)
POST /api/v1/posts             {submolt, title, content} (Bearer)
```

**Connector (exists, read-only wrapper in the fleet):**
`Desktop/Libra/claw_bot/moltbook.py` (archived copy:
`archive/restored/Libra_Desktop/claw_bot/moltbook.py`) — register, status,
list_submolts, post. The `CLAWBOT` worm surfaces state read-only.

### Allowed agent actions (no auth needed)
- `GET /submolts` — list all communities. Target submolts for this
  investigation: `osint`, `investigations`, `oversight`, `govfunding`,
  `compliance`, `media`, `whistleblower`.
- Read community descriptions and member counts (public payload).
- Poll submolts periodically to monitor for posts relevant to the
  investigation (monitoring is read-only research).

### Registration flow (human-gated — requires the user)
1. `register()` → returns a human **claim URL**.
2. The user must open the claim URL and log in (X login) to activate the agent.
3. Until claimed, credentials are `PENDING_CLAIM` placeholders in
   `claw_bot/state/moltbook.json`.
4. After claim, `status()` returns the live agent state.

### Posting (BLOCKED for this investigation)
- **Do NOT post** about the BCC investigation on Moltbook or any social
  platform while a qui tam is planned/sealed (public-disclosure bar).
- The `CLAWBOT` worm never posts — sending requires human approval via
  `Desktop/Libra/clawbot.py`.

## Part 3 — Research protocol (repeatable)

1. **Classify the target** — open portal / bot-walled / agent community.
2. **API first** — curl + `Accept: application/json`; try search before detail.
3. **Network-panel discovery** — headed Chrome, filter XHR/Fetch, replay calls.
4. **CDP fallback** — headed Chrome + persistent profile + `--remote-debugging-port`.
5. **Read Moltbook** — `GET /submolts`, monitor target submolts, log findings.
6. **Record** — save responses with retrieval date; log negative results so a
   "blocked" is provable later.
7. **Verify 2-source minimum** — every finding needs 2+ independent sources or
   is flagged "inferred" (see `investigation-osint` OSINT Verification Standard).

## Anti-Patterns

| ❌ Never | ✅ Always |
|----------|-----------|
| Post about the investigation on Moltbook/social (qui tam disclosure bar) | Read-only research; writing is human-gated |
| Loop a blocked wall (2nd pull without state change) | Document the block; try mirrors/records-request/manual |
| Drive headless Chrome into a Cloudflare wall | Headed Chrome + persistent profile over CDP |
| Scrape a detail API that 403s repeatedly | Use the search API; document detail as manual-only |
| Write session cookies/tokens to artifacts | Keep credentials in the headed profile only |
| Trust one source | 2+ independent sources or "inferred" flag |

## Related Skills
- `investigation-osint` — blocked-portal playbooks, API discovery, verification standard
- `azazael-devtools-index` + the 7 `azazael-devtools-*` skills — panel mechanics
- `investigation-legal-referral` — qui tam disclosure-bar constraints (why posting is gated)
- `pre-action-gate-lite` — Gate 0b routes live-collection actions here