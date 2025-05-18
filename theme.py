import tkinter as tk
from tkinter import ttk
import platform

# Basic theme definitions: colors, fonts, etc.
THEMES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#222222",
        "button_bg": "#e1e1e1",
        "button_fg": "#222222",
        "entry_bg": "#ffffff",
        "entry_fg": "#000000",
        "highlight": "#007acc",
        "font": ("Helvetica", 11),
    },
    "dark": {
        "bg": "#1e1e1e",
        "fg": "#d4d4d4",
        "button_bg": "#3c3c3c",
        "button_fg": "#d4d4d4",
        "entry_bg": "#252526",
        "entry_fg": "#d4d4d4",
        "highlight": "#569cd6",
        "font": ("Helvetica", 11),
    }
}

current_theme = "dark"
_sound_enabled = True

# Sound feedback helpers
def play_click_sound():
    if not _sound_enabled:
        return
    if platform.system() == "Windows":
        import winsound
        winsound.MessageBeep(winsound.MB_OK)
    else:
        # Cross-platform fallback - no sound or add playsound lib
        pass

def toggle_sound(enabled: bool):
    global _sound_enabled
    _sound_enabled = enabled

# Apply theme styles to a Tk or Toplevel window and its widgets recursively
def apply_theme(window: tk.Tk | tk.Toplevel):
    theme = THEMES[current_theme]
    cls_name = window.winfo_class()

    # Only set bg on classic Tk widgets (e.g., Tk, Toplevel, Frame, LabelFrame)
    if cls_name in ("Tk", "Toplevel", "Frame", "Labelframe"):
        window.configure(bg=theme["bg"])

    # For ttk widgets, rely on styles, so don't set bg directly here

    for child in window.winfo_children():
        _apply_widget_theme(child, theme)

from tkinter import ttk

import tkinter as tk
from tkinter import ttk

def _apply_widget_theme(widget, theme):
    cls_name = widget.winfo_class()

    if cls_name == "TEntry":
        style = ttk.Style()
        style.configure("Dark.TEntry",
                        fieldbackground=theme["entry_bg"],
                        foreground=theme["entry_fg"],
                        insertcolor=theme["fg"],
                        font=theme["font"])
        widget.configure(style="Dark.TEntry")

    elif cls_name == "TLabel":
        style = ttk.Style()
        style.configure("Dark.TLabel",
                        background=theme["bg"],
                        foreground=theme["fg"],
                        font=theme["font"])
        widget.configure(style="Dark.TLabel")

    elif cls_name == "TButton":
        style = ttk.Style()
        style.configure("Dark.TButton",
                        background=theme["button_bg"],
                        foreground=theme["button_fg"],
                        font=theme["font"])
        widget.configure(style="Dark.TButton")

    elif cls_name == "TCombobox":
        style = ttk.Style()
        style.configure("Dark.TCombobox",
                fieldbackground=theme["entry_bg"],
                background=theme["entry_bg"],
                foreground=theme["entry_fg"],
                arrowcolor=theme["fg"],
                font=theme["font"])
        style.map("Dark.TCombobox",
                fieldbackground=[('readonly', theme["entry_bg"])],
                background=[('readonly', theme["entry_bg"])],
                foreground=[('readonly', theme["entry_fg"])])
        widget.configure(style="Dark.TCombobox")

    else:
        try:
            widget.configure(background=theme["bg"], foreground=theme["fg"], font=theme["font"])
        except tk.TclError:
            pass

    for child in widget.winfo_children():
        _apply_widget_theme(child, theme)

# Switch theme globally
def set_theme(name: str, windows: list[tk.Tk | tk.Toplevel]):
    global current_theme
    if name not in THEMES:
        raise ValueError(f"Theme {name} not found")
    current_theme = name
    for win in windows:
        apply_theme(win)
