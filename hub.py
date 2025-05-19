import tkinter as tk
from tkinter import ttk
import json
import utils
import os
from gallery import GalleryTool
from ai_assistant import open_ai_assistant

from utils import log_event
from chain_mode import open_chain_mode  
from mol_assembler import open_molecule_assembler
from library import ScienceLibrary

# Tool category hubs
from bio_tools_1 import open_bio_tools_hub
from geo_tools_1 import open_geology_tools_hub
from phys_tools_1 import open_physics_tools_hub
from math_tools_1 import open_math_tools_hub
from utils import open_global_launcher
from math_tools_1 import (
    open_function_plotter,
    open_quadratic_solver,
    open_triangle_solver
)

from phys_tools_1 import (
    open_unit_converter,
    open_terminal_velocity_calculator,
    open_projectile_motion_tool,
    open_ohms_law_tool,
    open_lens_calculator,
    open_acceleration_calculator,
    open_drag_force_calculator,
    open_force_calculator,
    open_kinetic_energy_calculator,
    open_speed_calculator
)

from chemtools import (
    open_mass_calculator,
    open_shell_visualizer,
    open_property_grapher,
    open_isotope_tool,
    open_phase_predictor,
    open_comparator,
    open_unit_multiplier,
    open_element_viewer,
    open_chemistry_tools_hub
)

from bio_tools_1 import (
    open_transcription_tool,
    open_codon_lookup_tool,
    open_osmosis_tool,
    open_molecular_weight_calculator,
    open_ph_calculator,
    open_population_growth_calculator,
)

from bio_tools_2 import (
    open_reverse_complement_tool,
    open_translate_dna_tool,
    open_gc_content_tool,
    open_seq_file_parser_tool,
    open_pairwise_align_tool,
)

from geo_tools_1 import (
    open_mineral_id_tool,
    open_radioactive_dating_tool,
    open_plate_boundary_tool,
    open_mineral_explorer,
    open_plate_velocity_calculator,
    #open_geo_model_tool <-- Commented out, because the FRICKING TOOL WONT WORK AND I WORKED ON IT FOR AN HOUR WITHOUT RESULTS AAAAAHHHH
)
from utils import register_window
from utils import open_windows
import theme
from tkinterdnd2 import TkinterDnD
root = TkinterDnD.Tk()

def initialize_gui():
    global root
    if root is None:
        root = tk.Tk()
        root.title("The Science Hub")
        root.geometry("1000x700")
        root.configure(bg="#f4f4f4")

# ----------------- UTILITY FUNCTIONS -----------------

def show_window_manager():
    win = tk.Toplevel()
    win.title("Window Manager")
    win.geometry("400x400")

    tk.Label(win, text="Currently Open Tools:", font=("Helvetica", 12, "bold")).pack(pady=10)

    frame = tk.Frame(win)
    frame.pack(fill="both", expand=True, padx=10)
    frame.configure()


    # Force frame bg color to be consistent (sometimes needed)
    frame.configure(background=theme.THEMES["dark"]["entry_bg"])


    def refresh():
        for widget in frame.winfo_children():
            widget.destroy()

        for name, window in open_windows.items():
            if not window.winfo_exists():
                continue  # skip closed

            row = tk.Frame(frame)
            row.pack(fill="x", pady=2)

            tk.Label(row, text=name, anchor="w", width=25).pack(side="left")
            tk.Button(row, text="Focus", command=window.lift).pack(side="left", padx=5)
            tk.Button(row, text="Close", command=lambda w=window: (w.destroy(), refresh())).pack(side="left")

    refresh()
    tk.Button(win, text="Refresh", command=refresh).pack(pady=10)

def clean_windows():
    dead = [key for key, win in open_windows.items() if not win.winfo_exists()]
    for key in dead:
        del open_windows[key]

def open_log():
    in_filter = False
    from PIL import Image, ImageTk
    import os

    def load_log():
        try:
            with open("calchub_log.txt", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "No logs found."

    def insert_tagged_log(content):
        logbox.config(state="normal")
        logbox.delete("1.0", tk.END)
        for line in content.splitlines():
            if line.startswith("[") and "]" in line:
                time_end = line.index("]") + 1
                timestamp = line[:time_end]
                rest = line[time_end:]
                logbox.insert(tk.END, timestamp + " ", "timestamp")

                if "Input:" in rest:
                    before, after = rest.split("Input:")
                    logbox.insert(tk.END, before + "Input: ", "input")
                    if "Output:" in after:
                        inputs, outputs = after.split("Output:")
                        if "[IMG:" in outputs:
                            img_start = outputs.index("[IMG:") + 5
                            img_end = outputs.index("]", img_start)
                            img_path = outputs[img_start:img_end]
                            before_img = outputs[:img_start-5]
                            logbox.insert(tk.END, inputs + "Output: " + before_img, "output")
                            logbox.insert(tk.END, f"[IMG:{img_path}]", img_path)
                            logbox.insert(tk.END, "\n")

                            # tag it and bind hover
                            logbox.tag_bind(img_path, "<Enter>", lambda e, p=img_path: show_image_tooltip(e, p))
                            logbox.tag_bind(img_path, "<Leave>", hide_image_tooltip)
                        else:
                            logbox.insert(tk.END, inputs + "Output: " + outputs + "\n", "output")
                    else:
                        logbox.insert(tk.END, after + "\n", "input")
                else:
                    logbox.insert(tk.END, rest + "\n")
            else:
                logbox.insert(tk.END, line + "\n")
        logbox.config(state="disabled")
        logbox.see(tk.END)

    def refresh_log():
        insert_tagged_log(load_log())

    def clear_log():
        with open("calchub_log.txt", "w", encoding="utf-8") as f:
            f.write("")
        refresh_log()

    in_filter = False

    def filter_log(*args):
        nonlocal in_filter
        if in_filter:
            return
        in_filter = True
        try:
            keyword = search_var.get().strip().lower()
            full_log = load_log()
            lines = full_log.splitlines()
            if keyword == "":
                filtered = lines
            else:
                filtered = [line for line in lines if keyword in line.lower()]
            insert_tagged_log("\n".join(filtered))
        finally:
            in_filter = False





    def show_image_tooltip(event, path):
        if not os.path.exists(path):
            return
        top = tk.Toplevel()
        top.overrideredirect(True)
        top.geometry(f"+{event.x_root+10}+{event.y_root+10}")
        img = Image.open(path)
        img.thumbnail((300, 250))
        img_tk = ImageTk.PhotoImage(img)
        label = tk.Label(top, image=img_tk, borderwidth=1, relief="solid")
        label.image = img_tk
        label.pack()
        logbox.image_tooltip = top

    def hide_image_tooltip(event):
        if hasattr(logbox, "image_tooltip"):
            logbox.image_tooltip.destroy()
            del logbox.image_tooltip

    logwin = tk.Toplevel()
    logwin.title("Session Log")

    # White background for log window
    logwin.configure(bg="white")

    # Search frame with white bg
    search_frame = ttk.Frame(logwin)
    search_frame.pack(padx=10, pady=10, fill="x")

    ttk.Label(search_frame, text="Search:").pack(side="left")

    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side="left", fill="x", expand=True, padx=(5,10))
    trace_id = search_var.trace_add("write", filter_log)
    clear_btn = ttk.Button(search_frame, text="Clear Log", command=clear_log)
    clear_btn.pack(side="left", padx=5)

    reload_btn = ttk.Button(search_frame, text="Reload", command=refresh_log)
    reload_btn.pack(side="left")

    # Log display with white bg and black fg
    logbox = tk.Text(logwin, wrap="word", width=100, height=30, bg="white", fg="black")
    logbox.pack(padx=10, pady=(0,10), fill="both", expand=True)

    logbox.tag_config("timestamp", foreground="red")
    logbox.tag_config("input", foreground="blue")
    logbox.tag_config("output", foreground="darkgreen", font=("Helvetica", 10, "bold"))

    refresh_log()

# ----------------- LIBRARY ------------------------

def open_science_library():
    initialize_gui()
    ScienceLibrary(root)

# ----------------- EXPORT LOG ---------------------

def export_log_to_md():
    import os
    import datetime

    try:
        with open("calchub_log.txt", "r", encoding="utf-8") as f:
            log = f.readlines()
    except FileNotFoundError:
        return

    if not os.path.exists("exports"):
        os.makedirs("exports")

    date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"exports/session_log_{date_str}.md"

    with open(filename, "w", encoding="utf-8") as out:
        out.write(f"# Science Hub Log Export\n**Date:** {date_str}\n\n---\n\n")

        for line in log:
            if line.strip() == "":
                continue
            if line.startswith("[") and "]" in line:
                # Parse timestamp
                time_end = line.index("]") + 1
                timestamp = line[:time_end]
                rest = line[time_end:].strip()

                out.write(f"### {timestamp}\n")

                if "Input:" in rest and "Output:" in rest:
                    before_input, after_input = rest.split("Input:")
                    input_part, output_part = after_input.split("Output:")

                    out.write(f"**Tool:** {before_input.strip()}\n\n")
                    out.write(f"**Input:** `{input_part.strip()}`\n\n")

                    if "[IMG:" in output_part:
                        pre, img = output_part.split("[IMG:")
                        img = img.strip(" ]\n")
                        out.write(f"**Output:** {pre.strip()}\n\n")
                        out.write(f"![Graph]({img})\n\n")
                    else:
                        out.write(f"**Output:** {output_part.strip()}\n\n")
                else:
                    out.write(f"{rest}\n\n")
            else:
                out.write(line + "\n")

    # Optional: open the folder after export
    os.startfile("exports")  # Windows only — remove if you're not on Windows

# ----------------- OPEN SIMPLE CALCULATOR----------

def open_simple_calculator(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Simple Calculator")

        tk.Label(win, text="Enter expression:").pack(pady=5)
        expr_entry = tk.Entry(win, width=40)
        expr_entry.pack(pady=5)

        # Preload from chain mode if given
        if preload:
            expr_entry.insert(0, preload)
        log_event("Simple Calculator (Chain)", preload, "Waiting for confirmation")

        result_label = tk.Label(win, text="", font=("Arial", 12))
        result_label.pack(pady=5)

        def compute():
            try:
                expr = expr_entry.get()
                result = eval(expr)
                result_label.config(text=f"Result: {result}")
                log_event("Simple Calculator", expr, result)
            except:
                result_label.config(text="Invalid expression.")

        tk.Button(win, text="Calculate", command=compute).pack(pady=5)
        return win

    register_window("Simple Calculator", create_window)

# ----------------- TOOLKIT LAUNCH -----------------

def launch_tool(selection):
    if selection == "Math Tools":
        open_math_tools_hub()
    elif selection == "Physics Tools":
        open_physics_tools_hub()
    elif selection == "Geology Tools":
        open_geology_tools_hub()
    elif selection == "Biology Tools":
        open_bio_tools_hub()
    elif selection == "Chemistry Tools":
        open_chemistry_tools_hub()
    elif selection == "Science Library":
        open_science_library()


    #------------------ Define ----------------------
def show_last_used():
    try:
        with open("calchub_log.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        if not lines:
            msg = "No entries found."
        else:
            msg = lines[-1]
    except FileNotFoundError:
        msg = "No log available."

    win = tk.Toplevel()
    win.title("Last Used Tool")
    tk.Label(win, text="Last Log Entry:", font=("Helvetica", 12, "bold")).pack(pady=5)
    tk.Message(win, text=msg, width=600).pack(pady=10)

def show_favorites():
    win = tk.Toplevel()
    win.title("Favorites")

    tk.Label(win, text="Favorites", font=("Helvetica", 12, "bold")).pack(pady=5)

    # Mineral favorites
    try:
        with open("mineral_favorites.json", "r") as f:
            mineral_favs = json.load(f)
    except FileNotFoundError:
        mineral_favs = []

    if mineral_favs:
        tk.Label(win, text="★ Mineral Favorites", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10)
        for name in mineral_favs:
            tk.Label(win, text=name).pack(anchor="w", padx=20)
    else:
        tk.Label(win, text="No starred minerals.").pack(anchor="w", padx=10)

    # Science Library favorites
    from os import listdir
    from os.path import join
    library_path = "library_entries"
    library_favs = []
    if os.path.exists(library_path):
        for file in listdir(library_path):
            if file.endswith(".json"):
                try:
                    with open(join(library_path, file), "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if data.get("favorite"):
                            library_favs.append(data["title"])
                except:
                    continue

    if library_favs:
        tk.Label(win, text="★ Science Library Favorites", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        for name in library_favs:
            tk.Label(win, text=name).pack(anchor="w", padx=20)
    else:
        tk.Label(win, text="No starred library entries.").pack(anchor="w", padx=10, pady=(10, 0))

chainable_tools = {
    "Simple Calculator": open_simple_calculator,
    "Function Plotter": open_function_plotter,
    "Quadratic Solver": open_quadratic_solver,
    "Triangle Solver": open_triangle_solver,
    "Unit Converter": open_unit_converter,
    "Terminal Velocity Calculator": open_terminal_velocity_calculator,
    "Projectile Motion Tool": open_projectile_motion_tool,
    "Ohm's Law Calculator": open_ohms_law_tool,
    "Lens & Mirror Equation": open_lens_calculator,
    "Mass Calculator": open_mass_calculator,
    "Shell Visualizer": open_shell_visualizer,
    "Property Grapher": open_property_grapher,
    "Isotope Tool": open_isotope_tool,
    "Phase Predictor": open_phase_predictor,
    "Comparator": open_comparator,
    "Unit Multiplier": open_unit_multiplier,
    "Element Viewer": open_element_viewer,
    "DNA Transcription Tool": open_transcription_tool,
    "Codon Lookup Tool": open_codon_lookup_tool,
    "Osmosis Tool": open_osmosis_tool,
    "Mineral Id Tool": open_mineral_id_tool,
    "Radioactive Dating Tool": open_radioactive_dating_tool,
    "Plate Boundary Tool": open_plate_boundary_tool,
    "Mineral Explorer": open_mineral_explorer,
    "Molecule Assembler": open_molecule_assembler,
    "Speed Calculator": open_speed_calculator,
    "Drag Force Calculator": open_drag_force_calculator,
    "Acceleration Calculator": open_acceleration_calculator,
    "Force Calculator": open_force_calculator,
    "Kinetic Energy Calculator": open_kinetic_energy_calculator,
    "Molecular Weight Calculator": open_molecular_weight_calculator,
    "pH Calculator": open_ph_calculator,
    "Population Growth Calculator": open_population_growth_calculator,
    "Plate Velocity Calculator": open_plate_velocity_calculator,
    #"Geology Model Tool": open_geo_model_tool <-- Commented out, because the FRICKING TOOL WONT WORK AND I WORKED ON IT FOR AN HOUR WITHOUT RESULTS AAAAAHHHH
    "Reverse Complement Tool": open_reverse_complement_tool,
    "DNA to Protein Tool": open_translate_dna_tool,
    "GC Content Tool": open_gc_content_tool,
    "Sequence File Parser": open_seq_file_parser_tool,
    "Pairwise Alignment Tool": open_pairwise_align_tool,

}

    # ----------------- MAIN WINDOW -----------------

if __name__ == "__main__":
    def initialize_gui():
        global root
        if root is None:
            root = tk.Tk()
            root.title("The Science Hub")
            # Use the dark background from theme.py
            root.configure(bg=theme.THEMES["dark"]["bg"])
            root.geometry("1000x700")

    # Then after you call initialize_gui():
    initialize_gui()

    style = ttk.Style()
    style.theme_use('clam')  # 'clam' supports better theming on ttk

    # Set your root background explicitly for the dark theme
    root.configure(bg=theme.THEMES["dark"]["bg"])

    ttk.Label(root, text="Choose a Toolkit:", style="Dark.TLabel").grid(row=0, column=0, padx=10, pady=10)

    tool_var = tk.StringVar(value="Select a Toolkit")
    tool_choices = ["Chemistry Tools", "Biology Tools", "Geology Tools", "Physics Tools", "Math Tools", "Science Library"]

    option_menu = tk.OptionMenu(root, tool_var, *tool_choices)
    option_menu.config(
        bg=theme.THEMES["dark"]["bg"],
        fg=theme.THEMES["dark"]["fg"],
        activebackground=theme.THEMES["dark"]["bg"],
        activeforeground=theme.THEMES["dark"]["fg"],
        highlightthickness=0,
        relief="flat",
        borderwidth=0,
        highlightbackground=theme.THEMES["dark"]["bg"],
    )
    option_menu["menu"].config(
        bg=theme.THEMES["dark"]["entry_bg"],
        fg=theme.THEMES["dark"]["entry_fg"],
        activebackground=theme.THEMES["dark"]["button_bg"],
        activeforeground=theme.THEMES["dark"]["button_fg"],
    )
    option_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    open_button = ttk.Button(root, text="Open Toolkit", command=lambda: launch_tool(tool_var.get()))
    open_button.grid(row=0, column=2, padx=10, pady=10)


    style = ttk.Style()
    style.configure("Dark.TButton",
                    background=theme.THEMES["dark"]["bg"],  # exact window bg
                    foreground=theme.THEMES["dark"]["fg"],
                    padding=6,
                    relief="flat",
                    font=("Helvetica", 10))
    style.map("Dark.TButton",
            background=[("active", theme.THEMES["dark"]["bg"]), ("disabled", "#222222")],
            foreground=[("disabled", "#999999")])


    open_button = ttk.Button(
        root,
        text="Open Toolkit",
        command=lambda: launch_tool(tool_var.get()),
        style="Dark.TButton"
    )
    open_button.grid(row=0, column=2, padx=10, pady=10)




    # Title label with a bigger font and dark label style
    ttk.Label(root, text="The Science Hub", font=("Helvetica", 26, "bold"), style="Dark.TLabel").grid(row=1, column=0, columnspan=3, pady=(30, 20))

    # Apply theme to root and frame explicitly
    theme.apply_theme(root)

# Utility Panel with sound feedback on button clicks
style.configure("Dark.TLabelframe",
    background="#222222",
    foreground="#eee",
    font=("Helvetica", 11, "bold"))

style.configure("Dark.TLabelframe.Label",
    background="#222222",
    foreground="#eee")

style.configure("Dark.TLabel",
    background="#222222",
    foreground="#eee",
    font=("Helvetica", 10))

# Apply style when creating the frame and labels
util_frame = ttk.LabelFrame(root, text="Utility Panel", padding=10, style="Dark.TLabelframe")
util_frame.grid(pady=30, padx=40, sticky="ew")

ttk.Label(util_frame, text="Quick access tools that aren't part of any major category.", style="Dark.TLabel").pack(anchor="w", pady=5)
ttk.Label(util_frame, text="Open the Quick Bar with Ctrl + K.", style="Dark.TLabel").pack(anchor="w", pady=5)

import subprocess
import sys
import os

def launch_ai_assistant_subprocess():
    # Launch it as a separate process so closing it doesn't affect the main app
    script_path = os.path.join(os.path.dirname(__file__), "launch_ai_assistant.py")
    python_exe = sys.executable
    subprocess.Popen([python_exe, script_path])


def on_button_click(cmd):
    def wrapper():
        theme.play_click_sound()
        cmd()
    return wrapper

style = ttk.Style()
style.configure("Dark.TButton",
    background="#444444",
    foreground="#eee",
    padding=6,
    relief="flat",
    font=("Helvetica", 10))
style.map("Dark.TButton",
    background=[("active", "#555555"), ("disabled", "#222222")],
    foreground=[("disabled", "#999999")])

tools = [
    ("Simple Calculator", open_simple_calculator),
    ("View Log", open_log),
    ("Last Used Tool", show_last_used),
    ("View Favorites", show_favorites),
    ("Export Log", export_log_to_md),
    ("Window Manager", show_window_manager),
    ("Chain Mode", lambda: open_chain_mode(chainable_tools)),
    ("Gallery", lambda: GalleryTool(root)),
    ("AI Assistant", launch_ai_assistant_subprocess)
]

for text, func in tools:
    ttk.Button(util_frame, text=text, style="Dark.TButton",
               command=on_button_click(func)).pack(pady=4, anchor="w")

counter_label = ttk.Label(util_frame, font=("Helvetica", 10), style="Dark.TLabel")
counter_label.pack(anchor="e", padx=5)

def update_counter_label():
    counter_label.config(text=f"Tools used this session: {utils.session_counter}")
    root.after(2000, update_counter_label)

        # The Holy Ultramoly Gigasoley: TOOL RUNNER

tool_registry = {
    "Simple Calculator": open_simple_calculator,
    "View Log": open_log,
    "Function Plotter": open_function_plotter,
    "Quadratic Solver": open_quadratic_solver,
    "Triangle Solver": open_triangle_solver,
    "Unit Converter": open_unit_converter,
    "Terminal Velocity Calculator": open_terminal_velocity_calculator,
    "Projectile Motion Tool": open_projectile_motion_tool,
    "Ohm's Law Calculator": open_ohms_law_tool,
    "Lens & Mirror Equation": open_lens_calculator,
    "Mass Calculator": open_mass_calculator,
    "Shell Visualizer": open_shell_visualizer,
    "Property Grapher": open_property_grapher,
    "Isotope Tool": open_isotope_tool,
    "Phase Predictor": open_phase_predictor,
    "Comparator": open_comparator,
    "Unit Multiplier": open_unit_multiplier,
    "Element Viewer": open_element_viewer,
    "DNA Transcription Tool": open_transcription_tool,
    "Codon Lookup Tool": open_codon_lookup_tool,
    "Osmosis Tool": open_osmosis_tool,
    "Mineral Id Tool": open_mineral_id_tool,
    "Radioactive Dating Tool": open_radioactive_dating_tool,
    "Plate Boundary Tool": open_plate_boundary_tool,
    "Mineral Explorer": open_mineral_explorer,
    "Molecule Assembler": open_molecule_assembler,
    "Speed Calculator": open_speed_calculator,
    "Drag Force Calculator": open_drag_force_calculator,
    "Acceleration Calculator": open_acceleration_calculator,
    "Force Calculator": open_force_calculator,
    "Kinetic Energy Calculator": open_kinetic_energy_calculator,
    "Molecular Weight Calculator": open_molecular_weight_calculator,
    "pH Calculator": open_ph_calculator,
    "Population Growth Calculator": open_population_growth_calculator,
    "Plate Velocity Calculator": open_plate_velocity_calculator,
    "Gallery": lambda: GalleryTool(root),
    "Library": lambda: ScienceLibrary(root),
    #"Geology Model Tool": open_geo_model_tool <-- Commented out, because the FRICKING TOOL WONT WORK AND I WORKED ON IT FOR AN HOUR WITHOUT RESULTS AAAAAHHHH
    "Reverse Complement Tool": open_reverse_complement_tool,
    "DNA to Protein Tool": open_translate_dna_tool,
    "GC Content Tool": open_gc_content_tool,
    "Sequence File Parser": open_seq_file_parser_tool,
    "Pairwise Alignment Tool": open_pairwise_align_tool,
} 

# AI Model Launchers (for global launcher integration)
from utils import smart_launch

tool_registry.update({
    "Tiny": lambda: smart_launch("tiny"),
    "Tinyllama": lambda: smart_launch("tinyllama"),
    "Gem2": lambda: smart_launch("gem2"),
    "Gem4": lambda: smart_launch("gem4"),
    "Gem12": lambda: smart_launch("gem12"),
    "Phi-mini": lambda: smart_launch("phi-mini"),
    "Phi4": lambda: smart_launch("phi4"),
    "Phi4r": lambda: smart_launch("phi4r"),
    "Mathstral": lambda: smart_launch("mathstral"),
    "Dolphin": lambda: smart_launch("dolphin"),
    "Qwen8": lambda: smart_launch("qwen8"),
    "Qwen14": lambda: smart_launch("qwen14"),
    "Deep7": lambda: smart_launch("deep7"),
    "Deep14": lambda: smart_launch("deep14"),
    "Code2": lambda: smart_launch("code2"),
    "Code7": lambda: smart_launch("code7"),
    "Mistral": lambda: smart_launch("mistral"),

    # Optional mode presets
    "Tiny Use": lambda: smart_launch("tiny use"),
    "Dolphin Learn": lambda: smart_launch("dolphin learn"),
    "Gem4 Learn": lambda: smart_launch("gem4 learn"),
    "Phi4r Use": lambda: smart_launch("phi4r use"),
    "Mistral Casual": lambda: smart_launch("mistral casual")
})

 
root.bind("<Control-k>", lambda e: open_global_launcher(root, tool_registry))
update_counter_label()
root.mainloop()
