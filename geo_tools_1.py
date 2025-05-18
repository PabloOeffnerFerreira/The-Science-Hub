from utils import register_window  # [AUTO-REFRACTORED]
import pandas as pd
import tkinter as tk
from tkinter import ttk
import json
from utils import log_event

# Load mineral database
minerals_df = pd.read_csv("Minerals_Database.csv")
minerals_df.drop(columns=[col for col in minerals_df.columns if ".ru" in col], inplace=True)

# 1. Mineral Identifier Tool
def open_mineral_id_tool(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Mineral Identifier (Fuzzy Matching)")

        tk.Label(win, text="Hardness (Mohs):").pack()
        hard_entry = tk.Entry(win)
        hard_entry.pack()

        tk.Label(win, text="Specific Gravity:").pack()
        sg_entry = tk.Entry(win)
        sg_entry.pack()

        tk.Label(win, text="Crystal Structure (number code):").pack()
        cs_entry = tk.Entry(win)
        cs_entry.pack()

        if preload and isinstance(preload, tuple) and len(preload) == 3:
            hard_entry.insert(0, str(preload[0]))
            sg_entry.insert(0, str(preload[1]))
            cs_entry.insert(0, str(preload[2]))
            log_event("Mineral Identifier (Chain)", str(preload), "Waiting for match")

        result = tk.Text(win, width=70, height=10, wrap="word")
        result.pack(pady=10)

        def identify():
            try:
                h = float(hard_entry.get())
                sg = float(sg_entry.get())
                cs = float(cs_entry.get())
                matches = minerals_df[
                    (minerals_df['Mohs Hardness'].between(h - 0.5, h + 0.5)) &
                    (minerals_df['Specific Gravity'].between(sg - 0.5, sg + 0.5)) &
                    (minerals_df['Crystal Structure'] == cs)
                ]
                result.delete('1.0', tk.END)
                if not matches.empty:
                    for _, row in matches.iterrows():
                        line = f"Name: {row['Name']} | Hardness: {row['Mohs Hardness']} | SG: {row['Specific Gravity']} | Structure: {row['Crystal Structure']}\n"
                        result.insert(tk.END, line)
                    log_event("Mineral Identifier", f"H={h}, SG={sg}, CS={cs}", f"Matches found: {len(matches)}")
                else:
                    msg = "No matching minerals found."
                    result.insert(tk.END, msg)
                    log_event("Mineral Identifier", f"H={h}, SG={sg}, CS={cs}", msg)
            except Exception:
                msg = "Invalid input."
                result.delete('1.0', tk.END)
                result.insert(tk.END, msg)
                log_event("Mineral Identifier", f"H={hard_entry.get()}, SG={sg_entry.get()}, CS={cs_entry.get()}", msg)

        tk.Button(win, text="Identify", command=identify).pack(pady=5)
        return win

    register_window("Mineral Id Tool", create_window)


# 2. Radioactive Dating Tool
def open_radioactive_dating_tool(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Radioactive Dating")

        tk.Label(win, text="Half-Life (years):").pack()
        half_life_entry = tk.Entry(win)
        half_life_entry.pack()

        tk.Label(win, text="Percentage remaining (%):").pack()
        percent_entry = tk.Entry(win)
        percent_entry.pack()

        if preload and isinstance(preload, tuple) and len(preload) == 2:
            half_life_entry.insert(0, str(preload[0]))
            percent_entry.insert(0, str(preload[1]))
            log_event("Radioactive Dating (Chain)", str(preload), "Waiting for calculation")

        result = tk.Label(win, text="")
        result.pack(pady=10)

        def calculate_age():
            try:
                hl = float(half_life_entry.get())
                rem = float(percent_entry.get())
                if not (0 < rem <= 100):
                    msg = "Percentage must be between 0 and 100."
                    result.config(text=msg)
                    log_event("Radioactive Dating", f"HL={hl}, rem={rem}", msg)
                    return
                import math
                age = -hl * math.log2(rem / 100)
                msg = f"Estimated age: {age:.2f} years"
                result.config(text=msg)
                log_event("Radioactive Dating", f"HL={hl}, rem={rem}", msg)
            except Exception:
                msg = "Invalid input."
                result.config(text=msg)
                log_event("Radioactive Dating", f"HL={half_life_entry.get()}, rem={percent_entry.get()}", msg)

        tk.Button(win, text="Estimate Age", command=calculate_age).pack(pady=5)
        return win

    register_window("Radioactive Dating Tool", create_window)


# 3. Plate Boundary Tool
def open_plate_boundary_tool(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Plate Boundary Types")

        tk.Label(win, text="Choose a boundary type:").pack(pady=5)
        choices = ["Convergent", "Divergent", "Transform"]
        var = tk.StringVar()
        box = ttk.Combobox(win, textvariable=var, values=choices, state="readonly")
        box.pack(pady=5)
        box.set("Select Type")

        if preload and preload in choices:
            var.set(preload)
            log_event("Plate Boundaries (Chain)", preload, "Waiting for explanation")

        result = tk.Label(win, text="", wraplength=400, justify="left")
        result.pack(pady=10)

        def explain():
            selected = var.get()
            if selected == "Convergent":
                msg = "Plates move toward each other. Mountains, trenches, and volcanoes form."
            elif selected == "Divergent":
                msg = "Plates move apart. Mid-ocean ridges and new crust form."
            elif selected == "Transform":
                msg = "Plates slide past each other. Earthquakes are common."
            else:
                msg = "No boundary type selected."
            result.config(text=msg)
            log_event("Plate Boundaries", selected, msg)

        tk.Button(win, text="Explain", command=explain).pack(pady=5)
        return win

    register_window("Plate Boundary Tool", create_window)


# 4. Mineral Explorer
def open_mineral_explorer(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Mineral Explorer")

        favorites_path = "mineral_favorites.json"
        try:
            with open(favorites_path, "r") as f:
                favorites = set(json.load(f))
        except:
            favorites = set()

        search_var = tk.StringVar()
        structure_var = tk.StringVar()
        show_favs_var = tk.BooleanVar()

        if preload and isinstance(preload, str):
            search_var.set(preload)
            log_event("Mineral Explorer (Chain)", preload, "Waiting for search")

        def update_display():
            query = search_var.get().strip().lower()
            selected_structure = structure_var.get()
            show_favs = show_favs_var.get()

            filtered = minerals_df.copy()
            if show_favs:
                filtered = filtered[filtered["Name"].isin(favorites)]

            if query:
                filtered = filtered[
                    filtered["Name"].fillna("").str.lower().str.contains(query)
                ]

            if selected_structure and selected_structure != "All":
                try:
                    val = int(selected_structure)
                    filtered = filtered[filtered["Crystal Structure"] == val]
                except:
                    pass

            results.delete("1.0", tk.END)

            def safe(val):
                return val if pd.notna(val) and val != 0.0 else "—"

            for _, row in filtered.iterrows():
                name = row["Name"]
                hard = safe(row['Mohs Hardness'])
                sg = safe(row['Specific Gravity'])
                struct = safe(row['Crystal Structure'])
                line = f"★ " if name in favorites else "   "
                line += f"{name} | Hardness: {hard} | SG: {sg} | Structure: {struct}\n"
                results.insert(tk.END, line)

        def toggle_favorite():
            selected = search_var.get().strip()
            if selected in favorites:
                favorites.remove(selected)
            else:
                favorites.add(selected)
            with open(favorites_path, "w") as f:
                json.dump(list(favorites), f, indent=2)
            log_event("Favorite Toggled", selected, "★" if selected in favorites else "Unstarred")
            update_display()

        top = tk.Frame(win)
        top.pack(pady=5)
        tk.Label(top, text="Search:").pack(side="left")
        tk.Entry(top, textvariable=search_var, width=30).pack(side="left", padx=5)
        tk.Label(top, text="Structure:").pack(side="left")
        structures = ["All"] + sorted(minerals_df["Crystal Structure"].dropna().astype(int).unique().astype(str))
        ttk.Combobox(top, textvariable=structure_var, values=structures, state="readonly", width=6).pack(side="left")
        structure_var.set("All")
        tk.Checkbutton(top, text="Show Favorites Only", variable=show_favs_var, command=update_display).pack(side="left", padx=10)
        tk.Button(top, text="Refresh", command=update_display).pack(side="left", padx=5)

        results = tk.Text(win, height=25, width=95, wrap="word")
        results.pack(padx=10, pady=10)

        bottom = tk.Frame(win)
        bottom.pack(pady=5)
        tk.Button(bottom, text="Toggle Favorite (by name)", command=toggle_favorite).pack()

        search_var.trace_add("write", lambda *args: update_display())
        structure_var.trace_add("write", lambda *args: update_display())

        update_display()
        return win

    register_window("Mineral Explorer", create_window)

def open_plate_velocity_calculator(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Plate Velocity Calculator")

        tk.Label(win, text="Enter Distance Moved (cm):").pack()
        dist_entry = tk.Entry(win, width=20)
        dist_entry.pack(pady=5)

        tk.Label(win, text="Enter Time (million years):").pack()
        time_entry = tk.Entry(win, width=20)
        time_entry.pack(pady=5)

        result_label = tk.Label(win, text="")
        result_label.pack(pady=10)

        def compute():
            try:
                dist_cm = float(dist_entry.get())
                time_myr = float(time_entry.get())
                if time_myr == 0:
                    raise ValueError("Time cannot be zero")
                velocity_cm_per_year = dist_cm / (time_myr * 1_000_000)
                velocity_mm_per_year = velocity_cm_per_year * 10  # convert cm/yr to mm/yr
                result_label.config(text=f"Plate Velocity ≈ {velocity_mm_per_year:.4f} mm/yr")
                log_event("Plate Velocity Calculator", f"Distance={dist_cm} cm, Time={time_myr} Myr", velocity_mm_per_year)
            except Exception as e:
                result_label.config(text=f"Error: {e}")

        tk.Button(win, text="Calculate Velocity", command=compute).pack(pady=5)
        return win

    register_window("Plate Velocity Calculator", create_window)

def open_geology_tools_hub():
        def create_window():
            geo = tk.Toplevel()
            geo.title("Geology Tools")
        
            tk.Label(geo, text="Choose a Geology Tool:").pack(pady=10)
            options = [
                "Mineral Identifier",
                "Radioactive Dating",
                "Plate Boundary Types",
                "Mineral Explorer",
                "Plate Velocity Calculator"
            ]
            var = tk.StringVar()
            dropdown = ttk.Combobox(geo, textvariable=var, values=options, state="readonly")
            dropdown.pack(pady=5)
            dropdown.set("Select Tool")
        
            def open_selected():
                sel = var.get()
                if sel == "Mineral Identifier":
                    open_mineral_id_tool()
                elif sel == "Radioactive Dating":
                    open_radioactive_dating_tool()
                elif sel == "Plate Boundary Types":
                    open_plate_boundary_tool()
                elif sel == "Mineral Explorer":
                    open_mineral_explorer()
                elif sel == "Plate Velocity Calculator":
                    open_plate_velocity_calculator()
        
        
            tk.Button(geo, text="Open", command=open_selected).pack(pady=10)
            return geo
        register_window(open_geology_tools_hub.__name__.replace("open_", "").replace("_", " ").title(), create_window)