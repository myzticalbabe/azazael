---
name: desktop-automation-safety
description: Safe desktop GUI automation rules for Windows sessions where other
  apps (terminal client, Chrome/Facebook, modal dialogs) fight for foreground
  focus. Single-process execution, content-verified focus before ANY keystroke,
  window-minimize discipline, physical-DPI coordinate handling, keystroke-leak
  incident protocol. Proven 2026-09-04 (Gephi end-to-end verify; Facebook leak
  incident Sep-4(55)).
metadata:
  category: process
  projects: azazael, bcc
  priority: high
  audit_date: 2026-09-04
  auto_load: false
---

# Desktop Automation Safety (GUI Focus Discipline)

Rules for driving desktop GUI apps (Gephi, Chrome, native dialogs) by
synthetic input on a Windows desktop where **other windows keep taking the
foreground**. Derived from the 2026-09-04 Gephi ForceAtlas2 verification
(Sep-4(54)/(55)), where blind automation leaked keystrokes into a
Facebook/Messenger window.

## The core hazards (observed on this desktop)

1. **The terminal/agent client re-foregrounds on every tool command.** Each new
   command you run restores + activates the client window, hiding the target
   app again. → All GUI automation must live in **ONE script run via ONE
   command**; between-command automation is impossible.
2. **Other apps interpose at any moment** — Chrome (Facebook/Messenger,
   ProPublica), modal dialogs (class `#32770`, e.g. an un-dismissed File→Open
   dialog silently steals every keystroke), Settings, Audio consoles. A modal
   dialog can sit open for the whole session and swallow input.
3. **Minimized windows can come back** (client auto-restore; minimizing an
   owned dialog also minimizes its owner). Never assume the desktop state
   persists between commands — or even within one script.
4. **DPI/coordinate traps.** Screens are often 1440×900 logical at 200 % →
   2880×1800 physical. `pyautogui` import makes the process DPI-aware
   (physical px); code that does NOT import it sees logical rects. Mixing the
   two silently doubles/quarters every coordinate.

## Rule 1 — One process, minimize the world

At script start (before touching the target):

- Enumerate top-level windows (`EnumWindows` + `IsWindowVisible`) and
  **minimize everything except the target app and system classes**
  (`Progman`, `WorkerW`, `Shell_TrayWnd`, `Windows.UI.Core.CoreWindow`,
  `AsusFocusModeClass`). Do NOT minimize the terminal client you need to
  restore at the end — or do, but restore it in the same script.
- Activate the target with the Win32 foreground dance:
  `AttachThreadInput(cur→fg) → BringWindowToTop → SetForegroundWindow →
  detach`, preceded by `ShowWindow(SW_RESTORE)`.
- Restore minimized windows at script end (SW_RESTORE) so you leave the
  desktop as you found it.

## Rule 2 — Content-verified focus before ANY keystroke (the hard rule)

**Never send text/Enter/accelerator keys unless you have just verified, from
pixels, that the target app is the one that will receive them.**

- After activating, screenshot the window region and OCR the top strip; loop
  until it contains the target's chrome (e.g. `workspace`/`overview`/tab
  names) — retry activation on failure. A foreground-window title check is NOT
  enough; screenshots can show a different app over the same rect.
- Re-verify before every input burst (focus can drift mid-script).
- Prefer **keyboard mnemonics** (`Alt+W`, type-ahead) over OCR-clicking tiny
  chrome text, which OCR reads poorly.

## Rule 3 — Keystroke-leak incident protocol

If a leak happens (target lost focus, input went to another app — especially a
social/messaging app):

1. **Stop the automation immediately** (kill the script; fail-safe exception is
   your friend — keep `pyautogui.FAILSAFE = True`).
2. Screenshot the affected state for the record and keep the captures.
3. Assess what the leaked input could have done (e.g. Facebook `l` = like;
   Enter in a Messenger composer = send). OCR the captures for the leaked
   strings. Absence of evidence is NOT proof — say so honestly.
4. **Tell the user what to check** (feed / chats for stray text) — never hide
   it. Then kill the target app and delete the helper scripts.
5. Record the incident in the session milestone (transparency keeps it
   reproducible and prevents repeat).

## Rule 4 — Coordinates: one DPI space, live rects

- Import `pyautogui` at the TOP of the process so everything is physical px.
- Read the window rect fresh via `GetWindowRect` before every click/screenshot
  — never trust cached `.left/.top/.width/.height` (they can report
  `(-32000,-32000)` for minimized windows, or stale geometry).
- OCR on upscaled crops (2× LANCZOS) and divide coordinates back; convert
  window-local OCR hits to screen-absolute by adding the window origin.
- Screenshot region = `(x, y, w, h)` from that same live rect.

## Rule 5 — Evidence discipline

- Screenshot every stage to `evidence/`, then OCR-verify the keepers and write
  a README stating exactly what each capture proves. Move ambiguous/failed
  captures to `_noise/` or an incident folder rather than deleting.

## Rule 6 — Empirically verify protocol claims

Claims like "tool X can't do Y" must be re-tested when a run contradicts them.
The Gephi CLI claim ("file-arg only opens .gephi projects") was wrong — the
graphml argument works; the app just needs 20–25 s to boot before the Import
report appears. Correct the recorded claim and update the tooling when proven.

## Gate integration (enforcement)

The pre-action gates (`pre-action-gate-lite`, `azazael-pre-action-gate`) gate
FILE-EDIT actions (str_replace / write_file / scripts). Synthetic GUI input
(pyautogui clicks / typewrite / hotkeys on LIVE windows) was previously outside
every gate — that coverage hole is how the 2026-09-04 Facebook leak happened.
This skill IS the gate for that action class:

**Before launching ANY synthetic-input GUI automation, print this assertion in
response text (not thinking):**

```text
🛑 [GUI-AUTOMATION GATE]
- Single process? (all steps inside ONE script run via ONE command — the client
  re-foregrounds on every new command)
- World minimized? (all visible non-target top-level windows minimized at start)
- Content-verified focus? (pixel/OCR proof the target app is receiving input —
  screenshot + OCR of top strip, not just the foreground-window title)
- No keystroke without proof? (typing/hotkeys only after the check above)
- Restore-at-end planned? (target + minimized windows restored)
- GATE DECISION: [PROCEED / HALT — verify focus first]
```

HALT rule: **any keystroke without content-verified focus = CRITICAL violation**
(social apps are one lost-focus event from receiving input).

## When to prefer headless/deterministic over GUI

If the goal is an engine-level result (layout render, import, export), prefer a
headless deterministic path (CLI file arguments, engine jars, scripted
pipelines) over synthetic GUI input. Reserve GUI automation for cases that
genuinely need the rendered UI, and only with the rules above.

## Related skills

- `pre-action-gate-lite` — the lite gate; Gate 0 routes GUI-automation actions here.
- `azazael-pre-action-gate` — the permanent 13-assertion gate (auto_load); GUI-automation routing note appended.
- `azazael-sentinel-gate` — the heavy 25-item authorization checklist (sibling of this skill in the compliance stack).

## Proven context

- 2026-09-04: Gephi 0.11.2 end-to-end verify — graphml CLI import proven
  (48 nodes/91 edges, Import report, Data Lab rows); ForceAtlas2 GUI run
  abandoned after repeated focus interference; keystroke leak into
  Facebook/Messenger assessed, captures kept in
  `gephi_export_bcc/evidence/_facebook_leak_incident/`, user notified,
  automation stopped. Milestone Sep-4(54)/(55).
