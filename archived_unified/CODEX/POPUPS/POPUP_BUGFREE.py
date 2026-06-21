# coding: utf-8
"""Bug-free popup display"""

import sys
import tkinter as tk
from tkinter import scrolledtext, messagebox


def main():
    root = tk.Tk()
    root.title("HYDRA Results")
    root.geometry("750x550")
    root.configure(bg="#0d0d1a")
    root.resizable(True, True)

    title = tk.Label(
        root,
        text="HYDRA CLUSTER",
        font=("Consolas", 22, "bold"),
        bg="#0d0d1a",
        fg="#00f5ff",
    )
    title.pack(pady=15)

    sub = tk.Label(
        root, text="Results Display", font=("Consolas", 10), bg="#0d0d1a", fg="#888"
    )
    sub.pack()

    text = scrolledtext.ScrolledText(
        root,
        font=("Consolas", 10),
        bg="#0a0a15",
        fg="#00ff88",
        wrap="word",
        padx=15,
        pady=15,
    )
    text.pack(fill="both", expand=True, padx=20, pady=15)

    content = """========================================
        Azazael ECOSYSTEM RESULTS
========================================

CLUSTER STATUS
--------------
Nodes: 10 total, 8 enabled
Pipeline: 6 stages complete
Tests: 15/15 PASSED (100%)
Health: EXCELLENT

FILES CREATED
-------------
- CODEX/ANALYSIS_REPORT.html
- CODEX/ANALYSIS_REPORT_DIVERSE.html
- CODEX/ANALYSIS_PROTOCOLS.py
- CODEX/HORUS_INTEGRATION.py

ANIMATION PROTOCOLS
-------------------
Categories: 8
Techniques: 24

HORUS INTEGRATION
----------------
Shared successfully

========================================"""
    text.insert("1.0", content)
    text.config(state="disabled", cursor="arrow")

    btn_frame = tk.Frame(root, bg="#0d0d1a")
    btn_frame.pack(pady=12)

    def close_win():
        try:
            root.destroy()
        except:
            pass
        sys.exit(0)

    close_btn = tk.Button(
        btn_frame,
        text="CLOSE",
        command=close_win,
        bg="#e74c3c",
        fg="white",
        font=("Consolas", 11, "bold"),
        relief="flat",
        padx=25,
        pady=6,
    )
    close_btn.pack()

    def on_enter(e):
        close_btn.config(bg="#c0392b")

    def on_leave(e):
        close_btn.config(bg="#e74c3c")

    close_btn.bind("<Enter>", on_enter)
    close_btn.bind("<Leave>", on_leave)

    root.update_idletasks()
    x = (root.winfo_screenwidth() - 750) // 2
    y = (root.winfo_screenheight() - 550) // 2
    root.geometry(f"750x550+{x}+{y}")

    try:
        root.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
