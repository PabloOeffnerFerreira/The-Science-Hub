session_counter = 0

import datetime

def log_event(tool_name, entry, result):
    global session_counter
    session_counter += 1
    with open("calchub_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {tool_name} | Input: {entry} | Output: {result}\n")

import tkinter as tk
from tkinter import ttk

global_launcher = None  # Global reference to the launcher window

def open_global_launcher(root, tool_registry):
    global global_launcher
    if global_launcher and global_launcher.winfo_exists():
        global_launcher.lift()
        return

    global_launcher = tk.Toplevel(root)
    global_launcher.title("Tool Launcher")
    global_launcher.geometry("500x250")
    global_launcher.transient(root)
    global_launcher.grab_set()
    global_launcher.resizable(False, False)

    tk.Label(global_launcher, text="Search for a tool:", font=("Helvetica", 14, "bold")).pack(pady=(15, 5))

    search_var = tk.StringVar()
    entry = tk.Entry(global_launcher, textvariable=search_var, font=("Helvetica", 14), width=50)
    entry.pack(pady=5)
    entry.focus()

    listbox = tk.Listbox(global_launcher, height=10, font=("Helvetica", 12), activestyle='dotbox')
    listbox.pack(pady=(5, 15), padx=10, fill="both", expand=True)

    recursion_guard = False

    def update_listbox(*args):
        nonlocal recursion_guard
        if recursion_guard:
            return
        recursion_guard = True
        try:
            query = search_var.get().lower()
            listbox.delete(0, tk.END)
            for name in sorted(tool_registry.keys()):
                if query in name.lower():
                    listbox.insert(tk.END, name)
            if listbox.size() > 0:
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(0)
                listbox.activate(0)
        finally:
            recursion_guard = False

    trace_id = search_var.trace_add("write", update_listbox)

    def launch_selected(event=None):
        try:
            selected = listbox.get(listbox.curselection())
            global_launcher.destroy()
            tool_registry[selected]()
        except Exception:
            pass

    listbox.bind("<Return>", launch_selected)
    listbox.bind("<Double-1>", launch_selected)
    entry.bind("<Return>", lambda e: launch_selected())

    def select_first(event=None):
        if listbox.size() > 0:
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(0)
            listbox.activate(0)

    entry.bind("<KeyRelease>", select_first)

    def on_close():
        global global_launcher
        nonlocal trace_id
        if global_launcher and global_launcher.winfo_exists():
            # Remove trace callback before destroying window
            search_var.trace_remove("write", trace_id)
            global_launcher.destroy()
        global_launcher = None
    
        global_launcher.protocol("WM_DELETE_WINDOW", on_close)
# Universal Helper

open_windows = {}

def register_window(name, create_window_func):
    clean_open_windows()
    if name in open_windows and open_windows[name].winfo_exists():
        open_windows[name].lift()
        return open_windows[name]

    win = create_window_func()
    open_windows[name] = win
    return win 

def clean_open_windows():
    dead = []
    for name, win in list(open_windows.items()):
        try:
            if not win.winfo_exists():
                dead.append(name)
        except tk.TclError:
            # Happens when the app is already destroyed
            dead.append(name)
    for name in dead:
        del open_windows[name]