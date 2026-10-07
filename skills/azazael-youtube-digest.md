---
name: azazael-youtube-digest
description: Fetch YouTube transcripts and turn videos into structured digests (TL;DR, key theses, timestamped timeline, quotes). Use when the user shares a YouTube link, asks to summarize a video, or wants channel/playlist research. Batch mode handles whole link lists with caching.
compatibility: Windows 11 + Python 3.14t + yt-dlp 2026.08.19 + node 24 (EJS runtime). Network access to YouTube required. No API keys, no paid services.
metadata:
  category: tools
  project: azazael
  priority: medium
  auto_load: false
  version: 1.0.0
  created: 2026-10-05
  adapted_from: Claude Agent Skills open standard (SKILL.md + frontmatter + scripts layout); workflow debt to didntwatch (batch/cache design) and youtube-digest (digest structure)
---

# YouTube Digest — Transcript Fetch + Structured Summary

Turn any YouTube video into a structured digest without watching it. Transcript-first pipeline: the engine (`tools/youtube_transcript.py`, stdlib-only) fetches subtitles; the agent writes the digest. Never fabricate transcript content.

## When to use

- User shares a YouTube URL (`watch?v=`, `youtu.be`, `/shorts/`, `/embed/`, `/live/`) or a bare 11-char video id and wants a summary, key points, quotes, or chapter breakdown.
- User hands over a list of links or a bookmarks file → batch mode.
- Channel/playlist research: fetch each video, then synthesize across the cache.

## Single video

```bash
python azazael/tools/youtube_transcript.py fetch "<url-or-id>" [--lang en] [--format text|json]
```

Output is timestamped Markdown with `youtu.be/?t=` deep links. If `--format json`, the agent formats the digest itself. Keep the transcript in context for follow-up questions, quotes, and re-formatting.

## Batch mode (link lists)

```bash
python azazael/tools/youtube_transcript.py batch --input urls.txt [--out .cache/yt] [--manifest manifest.json] [--delay 1.0]
```

- One URL/id per line; `#` comments and duplicates ignored.
- Prints one slim JSON record per video; full transcripts stay cached in `--out/<id>.json` and OUT of context.
- Build the numbered report over the cache/manifest. Drill into any video by reading its cached file — never re-fetch.
- Polite by default: 1 s delay, 3 retries with backoff. Raise `--delay` on rate limits.

## Digest structure (agent-written)

Default format is **key theses**; user picks otherwise.

1. **TL;DR** — 1–2 sentences.
2. **Key theses** — bulleted main points.
3. **Topic timeline** — sections with `mm:ss` + deep links.
4. **Notable quotes** — verbatim, with timestamps.
5. **Triage verdict** (on request) — worth watching?

Summary language defaults to the user's language, else the transcript language. Length default: medium.

## Failure modes (honest, always)

| Engine status | Meaning | Agent behavior |
|---|---|---|
| `no-subtitles` | No caption tracks | Ask user to paste transcript text; summarize that with the same no-fabrication rule |
| `blocked` | 403/429/SABR/bot-check | Retry once with higher `--delay`; then suggest cookies (`--cookies-from-browser`) or the client workarounds in `azazael-chrome-url-download`; never claim content you did not fetch |
| `unavailable` | Private/removed/deleted | Say so, stop |
| Mixed bilingual subs | Both languages present | Ask: bilingual or English-only output |

## YouTube 403 / SABR / PO-token reality

Documented in `azazael-chrome-url-download`: YouTube increasingly demands sign-in/bot-checks. The engine surfaces `blocked` instead of guessing. Escalation order: retry → `--delay` up → browser cookies → alternate clients. Record new workarounds there, not here.

## Related skills

- `azazael-chrome-url-download` — active-tab URL capture + yt-dlp download workarounds.
- `azazael-pkg314t-yt-dlp` — yt-dlp package reference for the 3.14t env.
