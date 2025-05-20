import tkinter as tk
from tkinter import ttk
import os
# Map of tool names to functions that accept preload input
CHAINABLE_TOOLS = {}  # ← leave this empty, it'll be injected

import datetime

def log_chain(text):
    with open("chainmode_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {text}\n")

def get_recent_log_outputs(log_path="calchub_log.txt", limit=20):
    if not os.path.exists(log_path):
        return []

    entries = []
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in reversed(lines):
        if "Input:" in line:
            parts = line.strip().split("Input:")
            if len(parts) == 2:
                meta, rest = parts
                if "Output:" in rest:
                    input_part, output = rest.split("Output:", 1)
                    entries.append((meta.strip(), output.strip()))
                else:
                    entries.append((meta.strip(), rest.strip()))
                if len(entries) >= limit:
                    break
    return entries

def open_chain_mode(tool_map):
    global CHAINABLE_TOOLS
    CHAINABLE_TOOLS = tool_map
    def launch_chain():
        selection = log_listbox.curselection()
        tool_name = tool_var.get()

        if not selection or tool_name not in CHAINABLE_TOOLS:
            return

        _, output = recent_logs[selection[0]]
        tool_func = CHAINABLE_TOOLS[tool_name]
        tool_func(preload=output)

    win = tk.Toplevel()
    win.title("Chain Mode")

    tk.Label(win, text="Select a recent result:").pack(pady=5)
    log_frame = tk.Frame(win)
    log_frame.pack(padx=10, pady=5)

    log_scroll = tk.Scrollbar(log_frame)
    log_scroll.pack(side="right", fill="y")

    log_listbox = tk.Listbox(log_frame, height=10, width=80, yscrollcommand=log_scroll.set)
    log_listbox.pack(side="left", fill="both", expand=True)
    log_scroll.config(command=log_listbox.yview)

    recent_logs = get_recent_log_outputs()
    for meta, output in recent_logs:
        log_listbox.insert(tk.END, f"{meta} → {output}")

    tk.Label(win, text="Select destination tool:").pack(pady=5)
    tool_var = tk.StringVar()
    tool_menu = ttk.Combobox(win, textvariable=tool_var, values=list(CHAINABLE_TOOLS.keys()), state="readonly")
    tool_menu.pack(pady=5)
    if CHAINABLE_TOOLS:
        tool_menu.set(list(CHAINABLE_TOOLS.keys())[0])

    tk.Button(win, text="Chain to Tool", command=launch_chain).pack(pady=10)

    def refresh_log():
        log_listbox.delete(0, tk.END)
        nonlocal recent_logs
        recent_logs = get_recent_log_outputs()
        for meta, output in recent_logs:
            log_listbox.insert(tk.END, f"{meta} → {output}")

    tk.Button(win, text="Refresh", command=refresh_log).pack(pady=5)
