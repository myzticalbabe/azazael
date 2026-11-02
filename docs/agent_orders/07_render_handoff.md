## RENDER + SESSION HANDOFF (2026-10-30, all lanes)

**Promoted to a block on 2026-11-02.** This section was hand-copied into six
instruction files and existed in no source, so its figures had no owner and no
check: the shard counts below were three days stale and nothing could notice. One
source now, generated into every lane, verified by `orders-in-sync`.

- **Any moving picture, clip or multi-frame render:** read
  `C:\Users\clint\YGGDRASIL_RENDER_PLAYBOOK_2026-10-30.md` before writing a
  renderer. Frame index from the URL (never the clock), one Chrome profile per
  frame, absolute output paths, never edit a running bash script, verify frame
  count + 3 distinct hashes + read the decoded frames. Chrome/Puppeteer capture,
  never PIL.
- **Forest clips (built, on disk):** `C:\Users\clint\yggdrasil_forest\YGGDRASIL_FOREST_{WINDOWS,UBUNTU,KALI}.mp4`;
  per-environment measurements in `atlas_<env>.json` (1395 shards / 894 public — measured 2026-10-30). Ubuntu has no browser, so its clip was rendered by Kali's
  chromium against Ubuntu's own data — the clip states this.
- **Kilo session history is archived and cleared.** Archive:
  `G:\KILO_SESSION_ARCHIVE_2026-10-30\` (`MANIFEST.json`, per-table
  `.jsonl.gz`, `schema.sql`, `dirs/*.tar.gz`; 561 282 rows, all hashes verified,
  measured 2026-10-30). Kilo now starts with **zero sessions** and builds new
  contexts.
- **Board is the delivery plane:** status to `lane.all.announce`, queue to
  `lane.<lane>.tasks`, and read the row back — a post you cannot read back did
  not land.
