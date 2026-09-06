---
name: html-render-verification
description: HTML render verification via headless-Chrome CDP — structural audits cannot
  catch JS-level defects (literal-newline joins, unterminated strings, unhandled clipboard
  rejections), so every built or edited HTML must also pass a real browser render check.
  Harness verify_aoa_cdp.py, sweep scopes, trap catalog (REAL INCIDENTS 2026-09-02,
  2026-09-04), the deterministic clipboard unhandledrejection probe, and the
  fix-then-reverify loop.
metadata:
  category: process
  projects: azazael, aoa, codex, bcc
  priority: high
  audit_date: 2026-09-04
  auto_load: false
---

# HTML Render Verification — CDP Sweep Method

## Core lesson (proven twice, 2026-09-02)

**The structural HTML audit (audit_html.py) does NOT catch JS-level defects.**
It checks tag balance / strings-with-comments-stripped / viewport presence — a
file can pass 67/67 and still throw a `SyntaxError` in a real browser. ONLY a
render check (headless Chrome via CDP) proves a page actually loads. Two REAL
INCIDENTS in one day:

1. **Literal `\n` join** — `build.py` wrote `f.write('\\n'.join(H))` (double-escaped
   backslash-n) → the ENTIRE HTML became one line of literal `\n` characters →
   Chrome: `SyntaxError: Invalid or unexpected token @ :0` in the inline
   `mermaid.initialize(...)` script. Structural audit: PASS. Render: FAIL.
2. **Unterminated single-quoted string** — `Azazael_DUAL_PANE.html` had an
   `alert('...')` whose `'` string spanned lines 558–562 with plain-text lines
   inside, stranding the closing `');`. Structural audit: PASS. Render: FAIL.

## The harness

`verify_aoa_cdp.py` at project root (also `emit_cdp_filelist.py` to regenerate
the auditor's file scope).

- Launches fresh headless Chrome (temp profile, port 9333,
  `--remote-allow-origins=*`), opens each file in one tab via `Page.navigate`.
- Captures `Runtime.consoleAPICalled` + `Runtime.exceptionThrown` — real events,
  not heuristics.
- **Resilient per-file**: a ws timeout or slow page fails ONE file, never the
  whole sweep (per-file try/except).
- Scope: argv files, `azazael/.cdp_filelist.txt` (newline paths), else root glob.
- Summary at end: `SWEEP: N files — X passed, Y failed` + per-fail stack frames.

## Procedure

1. **Build/edit the HTML**, then static pre-check (cheap, fast over thousands):
   ```bash
   python -c "d=open('FILE.html',encoding='utf-8').read(); \
   print('lines:', len(d.split(chr(10))), '| literal-backslash-n:', chr(92)+'n' in d)"
   # single-line + many literal \n = the join defect
   ```
2. **Render-check the file(s)** through `verify_aoa_cdp.py` — expect 0 console
   errors / 0 exceptions / 0 warnings.
3. **On FAIL**: classify by **exception ORIGIN** (codified in the harness
   2026-09-05, REPLACING the old message-heuristic): parse each exception's
   stack frames — if every frame traces to a **remote host** (`https://…`,
   `http://…`, `//…`, `file://` pointing at a third-party captured page) the
   exception is EXTERNAL; only **local-origin** exceptions (stack points at the
   audited file itself) fail the document.
   - External-only exceptions → environmental, NOT a defect: third-party CDN
     scripts (anychart, propublica, archive.org) that throw under `file://`,
     captured-portal runtime globals (`ASPx`, `$`) — the local file cannot fix
     a remote host's code.
   - Local SyntaxError / ReferenceError / TypeError → real defect in the file →
     fix + re-verify.
   - **Not-ready page with external-only errors** → the third-party-capture
     signature (its load event never fires because the CDN scripts broke under
     `file://`), NOT a silent hang — PASS as informational. A not-ready page
     with **zero** errors of any origin is the only true hang → re-check with
     a longer deadline.
   - Proof: the full 88-doc sweep went **86/88 → 88/88 ALL CLEAN** once
     origin classification replaced the message heuristic (`bcc_pp2.html`
     ProPublica + `wb_datasets.html` archive.org were the 2 excluded captures).
4. **Fix then RE-VERIFY** — the fixed file must PASS the harness (proof, not hope).
5. After the fix, confirm the class is isolated: run the static signature scan
   over the whole corpus so future sessions know the defect has no siblings.
6. **If the file has copy buttons** (`copyField`/`copyBlock`/`copyLetter`/`copyEmail`
   or any `navigator.clipboard.writeText` call), run the clipboard-defect probe
   below — the event channels alone will NOT catch raw-promise rejections
   (REAL INCIDENT 2026-09-04: 10 files passed an event-channel sweep at 0 errors
   while leaking 44 unhandled rejections).

## Clipboard-copy defect probe (deterministic, 2026-09-04)

### Why the standard channels miss it

`Runtime.exceptionThrown` and `Log.entryAdded` do **NOT** surface
`unhandledrejection` events. A page can pass a full event-channel render sweep
with 0 errors and still leak unhandled rejections from raw clipboard promises.
Only an **in-page `unhandledrejection` listener** sees them.

### The probe — in-page listener + no-user-gesture clicks

```js
// 1) Inject BEFORE any interaction. RE-INJECT after every reload — a reload
//    wipes in-page listeners (the 0-count false pass on 2026-09-04 was exactly
//    a probe reusing a pre-fix tab without reloading).
window.__rej = [];
window.addEventListener('unhandledrejection', function (e) {
  window.__rej.push(String(e.reason && e.reason.message || e.reason));
});
```

```js
// 2) Click every copy button WITHOUT a user gesture (plain .click() or CDP
//    Input.dispatchMouseEvent is fine). No user gesture =>
//    navigator.clipboard.writeText() rejects deterministically with
//    'NotAllowedError: Document is not focused' — the trip wire.
//    NOTE: navigator.clipboard is READ-ONLY — you cannot mock writeText;
//    the injected listener is the only reliable channel.
```

```python
# 3) Read the tally — must be 0:
cmd('Runtime.evaluate', {'expression': 'window.__rej', 'returnByValue': True})
```

### The defect and the canonical safe handler

**Defect:** `navigator.clipboard.writeText(t).then(ok)` with no `.catch` and no
fallback — on `file://` (non-secure context) or without a user gesture the
promise rejects into an **uncaught exception / unhandled rejection**, and the
intended textarea fallback is unreachable because the branch only ran when
clipboard existed.

**Safe handler (all shapes: `copyField`/`copyBlock`/`copyLetter`/`copyEmail`):**

```js
function copyField(id) {
  var el = document.getElementById(id);
  var txt = el && (el.value !== undefined ? el.value : el.innerText);
  if (!txt) return;
  function legacy() {
    var ta = document.createElement('textarea');
    ta.value = txt;
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta);
  }
  if (window.isSecureContext && navigator.clipboard) {
    navigator.clipboard.writeText(txt).catch(legacy);   // .catch absorbs the rejection
  } else {
    legacy();                                            // file:// routes straight here
  }
}
```

Properties that matter: `.catch(legacy)` absorbs the rejection and falls back;
the `isSecureContext` guard sends `file://` straight to the execCommand path;
no promise is ever left unhandled.

### Verify loop

1. Static pre-scan: `grep -l "navigator.clipboard.writeText" *.html` then drop
   handlers that already carry `.catch(` or `execCommand` — the rest are suspects.
   (`.then(onOk, onErr)` two-arg form also absorbs rejections — e.g.
   COMPLIANCE_SELF_DEALING_ANGLES.html — so only a writeText with NO rejection
   path is the defect class.) **Extend the scan beyond the root corpus** to the
   repo copies and G: archive mirrors (root + repo + mirrors clean = no copy
   lagged). Archive generations found RAW/PARTIAL (e.g. G: AZAZAEL archived
   EveUnleashed, 2026-09-04) stay INTACT per the historical-archive directive
   — flag, don't edit.
2. Inject the listener, reload the page, re-inject, click every copy button
   (no gesture), read `window.__rej` — expect `[]`.
3. On FAIL: fix to the safe handler (preserve the function's name and text
   semantics), then re-probe on a **fresh reload** — proof, not hope.

## Trap catalog (byte-exact forms)

| Defect | Buggy source | Symptom | Safe form |
|---|---|---|---|
| Literal-`\n` join | `f.write('\\n'.join(H))` | One-line HTML, literal `\n` text, `SyntaxError @ :0` | `f.write('\n'.join(H))` |
| Multi-line single-quote | `alert('line1\nline2…')` with real newlines inside `'...'` | `SyntaxError @ :N` — string unterminated | Backtick template literal ``alert(`line1\n…`)`` |
| Raw `.then()` clipboard | `navigator.clipboard.writeText(t).then(ok)` — no `.catch`, no fallback | Unhandled `NotAllowedError: Document is not focused` on `file://` / no gesture — **invisible to exceptionThrown/Log channels** | `.catch(legacy)` + textarea/`execCommand('copy')` fallback under an `isSecureContext` guard |

Detection rule of thumb: **if Chrome throws a JS SyntaxError but audit_html.py
passes, the bug is in how the file was WRITTEN (joins, quoting), not in its
structure.** A syntax-checking pass over the generator (`python -m py_compile`)
plus this render harness is the complete gate. And if the event channels show
0 errors but a copy button still fails, **the rejection channel is the missing
sensor** — run the in-page `unhandledrejection` probe before judging a letter
clean.

## Origin-aware classification (the rule, 2026-09-05)

**Judge an exception by WHERE ITS STACK POINTS, not what it says.** A CDN
script that dies under `file://` reports an error whose message is about the
CDN's own code — message heuristics are fragile (they mutate across CDN
versions). The harness keeps two buckets per file:

- `local` — any frame resolves to the audited file (its path/name appears in
  the stack). These FAIL the doc.
- `external` — frames point only at remote hosts or captured third-party
  pages. These are informational.

Verdict matrix (as implemented in verify_aoa_cdp.py):

| Local errors | External errors | Page ready | Verdict |
|---|---|---|---|
| 0 | any | any | PASS (external = environmental) |
| ≥1 | any | any | FAIL (real defect) |
| 0 | 0 | no | FAIL (silent hang — nothing fired at all) |
| 0 | >0 | no | PASS (capture signature — CDN broke the load event) |
| 0 | 0 | yes | PASS |

The third-party whole-page capture class is ALSO exempt from the fragment
resolver in the dead-link auditor (`audit_links_refined.py` keeps
`wb_datasets.html`/`bcc_pp2.html` fragments informational — their ids are
JS-set at runtime by the captured site).

## Cross-reference

- `investigation-document-construction` — the canonical safe copy-button handler
  (REQUIRED section) + the CDP 0-rejections verification requirement for every
  send-ready letter; this skill's clipboard probe is how that requirement is
  enforced.
- `aoa-html-builder` — registry-driven build.py / build_disclosure.py, builder
  status map (which producer is canonical), the same two traps documented there.
- `azazael-devtools-index` — DevTools skills; this harness is the automated
  equivalent (0 console errors = the DevTools Console panel verdict).
- Root harnesses kept as shared tooling: `verify_aoa_cdp.py` (+
  `emit_cdp_filelist.py`), `sweep_corpus_refs.py` (see
  `corpus-reference-integrity`).