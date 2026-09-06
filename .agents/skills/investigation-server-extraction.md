---
name: investigation-server-extraction
description: Server-rendered website text extraction when automated fetchers fail — sitemap-first page inventory with lastmods, curl + Python strip-script/style, browser fallback only when the fetched HTML genuinely lacks content, post-extraction identity verification. Distilled from the BCC investigation.
metadata:
  category: investigation
  project: bcc-investigation
  auto_load: false
  date_created: 2026-09-02
---

# Investigation: Server Extraction

## Overview
Extracting text from sites when an automated read_url/render fetch returns empty or boilerplate — usually a
fetcher problem, not a site problem, when the site is server-rendered (e.g., Duda CMS).

## Core Technique
1. **Recognize the platform** — a server-rendered CMS delivers the full HTML in the initial response; if the fetch
   comes back empty, fix the fetch, don't add a renderer.
2. **Sitemap-first inventory** — fetch `/sitemap.xml` for the page list **with lastmod dates**; use it to decide
   the crawl set (and to spot dates of interest).
3. **curl + strip** — fetch with a desktop user agent, then strip `<script>`/`<style>` with Python to isolate
   content text.
4. **Browser fallback** (Chrome CDP) only if the fetched HTML genuinely lacks the content.
5. **Post-extraction identity check** — confirm the page is on the target domain and matches its sitemap URL
   (template-heavy CMSes can serve near-identical pages).

## Case Example
- `bcc-website-extraction` (case-scoped) — BCC Duda CMS site; sitemap inventory with July 17–25, 2026 lastmods;
  hidden-surface findings in HIDDEN_ASPECTS_SWEEP.html.