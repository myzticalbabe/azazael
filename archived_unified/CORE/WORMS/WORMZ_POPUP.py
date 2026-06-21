# coding: utf-8
"""
WORMZ POPUP LAUNCHER
Simple tkinter popup for WORMZ BIBL crawler
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
import subprocess
import sys
import os


def run_wormz_popup():
    """Run WORMZ with full popup GUI."""

    root = tk.Tk()
    root.title("WORMZ - BIBL Crawler")
    root.geometry("900x700")
    root.configure(bg="#1a1a2e")

    def log(msg):
        text_area.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        text_area.see("end")
        root.update_idletasks()

    # Header
    header = tk.Frame(root, bg="#16213e", pady=10)
    header.pack(fill="x")

    tk.Label(
        header,
        text="WORMZ",
        font=("Consolas", 28, "bold"),
        bg="#16213e",
        fg="#00d4ff",
    ).pack()

    status_label = tk.Label(
        header,
        text="Initializing...",
        font=("Consolas", 12),
        bg="#16213e",
        fg="#7c3aed",
    )
    status_label.pack()

    # Progress bar
    progress = ttk.Progressbar(root, mode="determinate", length=850)
    progress.pack(pady=10, padx=25)

    # Text area
    text_area = scrolledtext.ScrolledText(
        root, wrap="word", font=("Consolas", 10), bg="#0f0f1a", fg="#00ff88", height=35
    )
    text_area.pack(fill="both", expand=True, padx=10, pady=10)

    log("=" * 60)
    log("WORMZ - BIBL Crawler Popup")
    log("=" * 60)
    log("")

    def execute_crawl():
        status_label.config(text="Running...")
        progress["value"] = 0
        root.update_idletasks()

        # Run WORMZ
        cmd = [sys.executable, "C:/Users/clint/Desktop/Azazael_UNIFIED/ORCHESTRATION_UNIFIED/CORE/WORMS/WORMZ.py", "--all"]

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )

        for line in iter(process.stdout.readline, ""):
            line = line.strip()
            if line:
                log(line)
                if "Crawl complete" in line or "COMPLETE" in line:
                    progress["value"] = 100

        process.wait()

        log("")
        log("=" * 60)
        log("CRAWL FINISHED - Popup will close in 5 seconds")
        log("=" * 60)

        status_label.config(text="Complete!")
        root.after(5000, root.destroy)

    log("Starting WORMZ crawl...")
    root.after(1000, execute_crawl)
    root.mainloop()


if __name__ == "__main__":
    run_wormz_popup()


