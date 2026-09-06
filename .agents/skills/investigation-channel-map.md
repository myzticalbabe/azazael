---
name: investigation-channel-map
description: Master channel register for investigations — which portals/APIs work, which are blocked, and the exact workaround for each (search-engine failures, government portal 503 recovery, CAPTCHA-gated ports, keyless JSON APIs). Distilled from the BCC investigation.
metadata:
  category: investigation
  project: bcc-investigation
  auto_load: false
  date_created: 2026-09-02
---

# Investigation: Channel Map

## Overview
Maintain a living register of every data channel used in an investigation: what works, what is blocked, and the
exact workaround for each. A channel map converts repeated trial-and-error into one deterministic lookup.

## Register Template

| Channel | State | Workaround |
|---------|-------|------------|
| *(API/portal/search engine)* | ✅ Works / ⚠ Flaky / ❌ Blocked | *(what to do instead)* |

## Known Channel Failure Classes
- **Search-engine failures (DDG/Bing/Mojeek):** unreliable for discovery — prefer sitemap-first extraction and
  direct API/keyed lookups over search results.
- **WAF/anti-bot blocks (e.g., Akamai 403):** automated fetch fails but manual browser works — use a browser
  fallback rather than hammering the endpoint.
- **5xx with recovery (e.g., DDAP 503):** back off + retry with delay and resume from a stable anchor (detail-page
  URLs), never restart from zero.
- **CAPTCHA-gated portals:** document the breaker status; provide a manual verification path.
- **JS-rendered views:** pages whose content renders client-side (e.g., ProPublica `/full`) look empty to plain
  fetches — use the JSON API or the static asset instead.

## Rules
- Record outages/workarounds **the moment they are hit** — a recovered channel is still a data point.
- Never silently re-try a known-failed channel in a loop; jump to its documented workaround.
- Keep the register inside the investigation (or a skill), so later sessions inherit it.

## Case Example
- `bcc-channel-register` (case-scoped) holds the BCC instance: ProPublica ✅, IRS TEOS ⚠ Akamai, USASpending ✅,
  PA DOS mirrors ⚠, DDAP ⚠ 503, DDG/Bing/Mojeek ❌, CMS NPI ✅, PA UJS ✅ headed-Chrome route works (Sep 4, 2026),
  PA Campaign Finance ✅ full-export route works (Sep 4, 2026).