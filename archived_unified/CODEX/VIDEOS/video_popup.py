import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import os

root = tk.Tk()
root.withdraw()

video_path = r"C:\Users\clint\Desktop\Azazael_UNIFIED\CODEX\OUTPUT\videos\azazael_educational_video_20260213_070204.mp4"
folder = r"C:\Users\clint\Desktop\Azazael_UNIFIED\CODEX\OUTPUT\videos"

result = messagebox.askokcancel(
    "Azazael Video Generated",
    f"Video: azazael_educational_video_20260213_070204.mp4\n\nSize: 0.18 MB\nDuration: ~74 seconds\n\nOpen folder or play now?",
)

if result:
    subprocess.run(f'explorer /select,"{video_path}"')
else:
    vlc = r"C:/Program Files/VideoLAN/VLC/vlc.exe"
    subprocess.run([vlc, video_path])
