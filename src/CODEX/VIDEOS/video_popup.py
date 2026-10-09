import tkinter as tk
from tkinter import messagebox
import subprocess
from pathlib import Path
from typing import List

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).
_SWALLOWED: List[str] = []

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        _SWALLOWED.append("%s:no-recorder" % where)

root = tk.Tk()
root.withdraw()

video_path = Path.home() / "Desktop" / "Azazael_UNIFIED" / "CODEX" / "OUTPUT" / "videos" / "azazael_educational_video_20260213_070204.mp4"
folder = Path.home() / "Desktop" / "Azazael_UNIFIED" / "CODEX" / "OUTPUT" / "videos"

result = messagebox.askokcancel(
    "Azazael Video Generated",
    "Video: azazael_educational_video_20260213_070204.mp4\n\nSize: 0.18 MB\nDuration: ~74 seconds\n\nOpen folder or play now?",
)

if result:
    subprocess.run(f'explorer /select,"{video_path}"')
else:
    vlc = r"C:/Program Files/VideoLAN/VLC/vlc.exe"
    subprocess.run([vlc, video_path])
