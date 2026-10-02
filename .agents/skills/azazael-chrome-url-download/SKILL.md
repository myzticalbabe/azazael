---
name: azazael-chrome-url-download
description: Capture the active Chrome tab URL (UI Automation, no DevTools needed) or the clipboard URL, then download it with yt-dlp — including the YouTube 403/SABR/PO-token reality and the client/EJS workarounds.
metadata:
  category: tools
  project: azazael
  priority: medium
  auto_load: false
  version: 1.0.0
  created: 2026-09-24
---

# Chrome Active-URL Capture → yt-dlp Download

End-to-end recipe for "download the page/video that is currently open in Chrome".
Proven 2026-09-24 on Windows 11 (Git Bash), Chrome 154, yt-dlp 2026.07.04, node v24.

## When to use

- User says "download the current URL from Chrome" / "grab this tab" / "download what I'm looking at".
- User copies a link to the clipboard and expects the agent to fetch it.

---

## Step 1 — Get the active tab URL (no DevTools required)

**Do not assume remote debugging is available.** Even when the user believes Chrome was
started with `--remote-debugging-port`, verify first — it is frequently absent:

```bash
curl -s --max-time 5 http://127.0.0.1:9222/json/version   # empty => no debug port
netstat -ano -p tcp | grep -i listen | grep -E '9222|9223'
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | Select-Object -ExpandProperty CommandLine" | grep -i remote-debugging
```

Note: `read_url` refuses `localhost`/private addresses, so use `curl` for these local probes.

If no debug port exists, read the omnibox directly with **Windows UI Automation** (non-invasive,
no restart, no elevation). Write `.tmp_geturl.ps1` in the project root, run it, then delete it:

```powershell
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$root = [System.Windows.Automation.AutomationElement]::RootElement
$cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ClassNameProperty, "Chrome_WidgetWin_1")
foreach ($w in $root.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)) {
  $ec = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Edit)
  foreach ($e in $w.FindAll([System.Windows.Automation.TreeScope]::Descendants, $ec)) {
    try {
      $v = $e.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value
      if ($v) { Write-Output ("WIN=[" + $w.Current.Name + "] ID=[" + $e.Current.AutomationId + "] VAL=[" + $v + "]") }
    } catch {}
  }
}
```

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File ./.tmp_geturl.ps1
rm -f ./.tmp_geturl.ps1
```

The active tab's omnibox is the Edit element named **`Address and search bar`** (AutomationId
`view_*`). Ignore the browser chrome's other edit fields.

### Traps

- **Multiple browsers.** Windows holds Edge *and* Chrome windows; filter on `WIN=[... Google Chrome]`.
- **Omnibox elides.** Chrome displays `youtube.com/watch?v=ID` — it hides the scheme and often
  drops extra query params (`list=`, `si=`). Do not treat the omnibox string as the canonical URL.
- **`iconv` is absent on Git Bash**, so `-EncodedCommand` via `iconv | base64` fails. Use a
  temp `.ps1` file instead of base64-encoding the script.

## Step 2 — Clipboard fallback

The user pasting a copied link is the most reliable source (full URL, params intact):

```bash
powershell -NoProfile -Command "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; Get-Clipboard -Raw"
```

## Step 3 — Download with yt-dlp

Tooling check: `yt-dlp --version`, `python --version`, `ffmpeg -version`, `node --version`.
ffmpeg is required for merging separate video+audio streams.

Resolve the Downloads folder in Windows form (a Windows `yt-dlp.exe` will not understand `/c/Users/...`):

```bash
UP=$(powershell -NoProfile -Command "[Environment]::GetFolderPath('UserProfile')" | tr -d '\r\n')
DL="${UP//\\//}/Downloads"
```

### The YouTube 403 reality (2026)

YouTube now applies **SABR-only streaming** and requires **PO tokens** on most clients. Symptoms:
`ERROR: unable to download video data: HTTP Error 403: Forbidden`, or only `18` (360p) listed.

| Client | Result (proven 2026-09-24) |
|--------|----------------------------|
| `android` | ✅ works, but exposes **only format 18 (360p)** |
| `android_vr` | lists 144p–1080p, but every download **403s** |
| `tv` | `The page needs to be reloaded.` |
| `tv_simply`, `mweb`, `ios` | https formats skipped — "require a GVS PO Token" |
| `web`, `web_safari`, `web_embedded` | no downloadable formats |

**Always add a JS runtime and the EJS challenge solver** — without these you lose the DASH
formats entirely:

```bash
yt-dlp --js-runtimes node --remote-components ejs:github -F "<URL>"
```

Working download for the formats that stream without a token (auto-degrades to 360p):

```bash
yt-dlp --js-runtimes node --remote-components ejs:github \
  --extractor-args "youtube:player_client=android" \
  -f "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720][ext=mp4]/b" \
  --merge-output-format mp4 -o "$DL/%(title)s.%(ext)s" --no-playlist --newline "<URL>"
```

### Getting 720p / 1080p (escalation, requires user consent)

A **PO token** is required. Options, in order of preference:

1. **PO token provider plugin** (no need to close the browser):
   `python -m pip install bgutil-ytdlp-pot-provider` plus its provider server
   (`npx bgutil-ytdlp-pot-provider` or the built script mode), then re-run the normal command.
2. **Browser cookies** — `--cookies-from-browser chrome`. Fails while Chrome is running
   (`ERROR: Could not copy Chrome cookie database`) and may fail anyway on Chrome 127+
   due to App-Bound Encryption (see yt-dlp issue #7271).

Do **not** silently install packages or close the user's browser — surface the tradeoff.

## Verification

```bash
ls -la "$DL"/*.mp4
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,codec_name -of csv=p=0 "$DL/<file>.mp4"
```

Confirm resolution actually matches the request — the auto-degrading `-f` ladder can quietly
land on 360p; never report "720p" from the command alone.

## Related

- `azazael-bin-ffmpeg` — merging/transcoding
- `azazael-tool-qwythos-proxy` — proxy-mediated downloads
- `azazael-crossplat-fileops` — safe Windows path handling from Git Bash
