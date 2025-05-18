import tkinter as tk
from tkinter import ttk
import os, json, math
import matplotlib.pyplot as plt
import re
import datetime
from utils import register_window
from mol_assembler import open_molecule_assembler
from data_utils import load_element_data, parse_formula


def log_event(tool_name, entry, result):
    with open("calchub_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {tool_name} | Input: {entry} | Output: {result}\n")


# 1. Molecular Weight Calculator
def open_mass_calculator(preload=None):
    def create_window():
        data = load_element_data()
        win = tk.Toplevel()
        win.title("Molecular Weight Calculator")

        tk.Label(win, text="Enter Formula:").pack(pady=5)
        entry = tk.Entry(win, width=30)
        entry.pack(pady=5)

        if preload:
            entry.insert(0, preload)
            log_event("Mass Calculator (Chain)", preload, "Waiting for confirmation")

        result_box = tk.Text(win, width=50, height=10)
        result_box.pack(pady=5)

        def calculate():
            formula = entry.get().strip()
            try:
                counts = parse_formula(formula)
                total = 0
                result_box.delete('1.0', tk.END)
                log_lines = []

                for el, count in counts.items():
                    if el in data and "AtomicMass" in data[el]:
                        mass = data[el]["AtomicMass"]
                    elif el in data and "atomic_mass" in data[el]:
                        mass = data[el]["atomic_mass"]
                    else:
                        msg = f"{el}: unknown"
                        result_box.insert(tk.END, msg + "\n")
                        log_lines.append(msg)
                        continue
                    subtotal = count * mass
                    line = f"{el} × {count} = {subtotal:.3f} g/mol"
                    result_box.insert(tk.END, line + "\n")
                    log_lines.append(line)
                    total += subtotal

                total_line = f"\nTotal = {total:.3f} g/mol"
                result_box.insert(tk.END, total_line)
                log_lines.append(total_line.strip())
                log_event("Mass Calculator", formula, total_line.strip())

            except Exception as e:
                error_msg = f"Error: {e}"
                result_box.delete('1.0', tk.END)
                result_box.insert(tk.END, error_msg)
                log_event("Mass Calculator", formula, error_msg)

        tk.Button(win, text="Calculate", command=calculate).pack(pady=5)
        return win

    register_window("Mass Calculator", create_window)


# 2. Isotopic Notation Tool
def open_isotope_tool(preload=None):
    def create_window():
        data = load_element_data()
        win = tk.Toplevel()
        win.title("Isotopic Notation")

        tk.Label(win, text="Element Symbol:").pack()
        symbol_entry = tk.Entry(win)
        symbol_entry.pack()

        tk.Label(win, text="Mass Number:").pack()
        mass_entry = tk.Entry(win)
        mass_entry.pack()

        if preload and isinstance(preload, tuple) and len(preload) == 2:
            symbol_entry.insert(0, preload[0])
            mass_entry.insert(0, preload[1])
            log_event("Isotopic Notation (Chain)", f"{preload}", "Waiting for confirmation")

        result = tk.Label(win, text="")
        result.pack(pady=10)

        def calculate():
            sym = symbol_entry.get().strip()
            try:
                mass = int(mass_entry.get())
                Z = data[sym]["AtomicNumber"] if sym in data else data[sym]["number"]
                neutrons = mass - Z
                output = f"Notation: {mass}{sym}\nProtons: {Z}\nNeutrons: {neutrons}"
                result.config(text=output)
                log_event("Isotopic Notation", f"{sym}, mass={mass}", output)
            except Exception as e:
                error_msg = "Invalid input or element not found."
                result.config(text=error_msg)
                log_event("Isotopic Notation", f"{sym}, mass={mass_entry.get()}", error_msg)

        tk.Button(win, text="Calculate", command=calculate).pack()
        return win

    register_window("Isotope Tool", create_window)


# 3. Electron Shell Visualizer
def open_shell_visualizer(preload=None):
    def create_window():
        data = load_element_data()
        win = tk.Toplevel()
        win.title("Shell Visualizer")

        tk.Label(win, text="Element Symbol:").pack()
        entry = tk.Entry(win)
        entry.pack()

        if preload:
            entry.insert(0, preload)
            log_event("Shell Visualizer (Chain)", preload, "Waiting for draw")

        canvas = tk.Canvas(win, width=300, height=300, bg="white")
        canvas.pack()

        def draw():
            canvas.delete("all")
            sym = entry.get().strip()
            if sym not in data or "shells" not in data[sym]:
                return
            shells = data[sym]["shells"]
            cx, cy = 150, 150
            for i, count in enumerate(shells):
                r = 30 + i * 30
                canvas.create_oval(cx - r, cy - r, cx + r, cy + r)
                for j in range(count):
                    angle = 2 * math.pi * j / count
                    ex = cx + r * math.cos(angle)
                    ey = cy + r * math.sin(angle)
                    canvas.create_oval(ex - 3, ey - 3, ex + 3, ey + 3, fill="black")
            canvas.create_text(cx, cy, text=sym, font=("Arial", 12, "bold"))
            log_event("Shell Visualizer", sym, f"Shells: {shells}")

        tk.Button(win, text="Draw", command=draw).pack()
        return win

    register_window("Shell Visualizer", create_window)

# 4. Phase at Room Temperature Predictor
def open_phase_predictor(preload=None):
    def create_window():
        data = load_element_data()
        win = tk.Toplevel()
        win.title("Phase at 25°C")

        tk.Label(win, text="Element Symbol:").pack()
        entry = tk.Entry(win)
        entry.pack()

        if preload:
            entry.insert(0, preload)
            log_event("Phase Predictor (Chain)", preload, "Waiting for check")

        result = tk.Label(win, text="")
        result.pack(pady=10)

        def predict():
            sym = entry.get().strip()
            try:
                el = data[sym]
                melt = el.get("MeltingPoint") or el.get("melt")
                boil = el.get("BoilingPoint") or el.get("boil")
                if melt is None or boil is None:
                    msg = "No data available."
                    result.config(text=msg)
                    log_event("Phase Predictor", sym, msg)
                    return
                if 25 < melt:
                    phase = "solid"
                elif melt <= 25 < boil:
                    phase = "liquid"
                else:
                    phase = "gas"
                msg = f"Predicted phase: {phase}"
                result.config(text=msg)
                log_event("Phase Predictor", sym, msg)
            except Exception:
                msg = "Invalid input or element not found."
                result.config(text=msg)
                log_event("Phase Predictor", sym, msg)

        tk.Button(win, text="Check Phase", command=predict).pack()
        return win

    register_window("Phase Predictor", create_window)


# 5. Element Comparator Tool
def open_comparator(preload=None):
    def create_window():
        data = load_element_data()
        win = tk.Toplevel()
        win.title("Compare Elements")

        tk.Label(win, text="Element A:").grid(row=0, column=0)
        a_var = tk.StringVar()
        a_drop = ttk.Combobox(win, textvariable=a_var, values=sorted(data.keys()), state='readonly')
        a_drop.grid(row=0, column=1)

        tk.Label(win, text="Element B:").grid(row=1, column=0)
        b_var = tk.StringVar()
        b_drop = ttk.Combobox(win, textvariable=b_var, values=sorted(data.keys()), state='readonly')
        b_drop.grid(row=1, column=1)

        if preload and isinstance(preload, tuple) and len(preload) == 2:
            a_var.set(preload[0])
            b_var.set(preload[1])
            log_event("Comparator (Chain)", f"{preload}", "Waiting for compare")

        output = tk.Text(win, width=50, height=12)
        output.grid(row=2, column=0, columnspan=2, pady=10)

        def compare():
            a, b = a_var.get(), b_var.get()
            if a not in data or b not in data:
                msg = "Invalid element selection."
                output.delete('1.0', tk.END)
                output.insert(tk.END, msg)
                log_event("Element Comparator", f"{a} vs {b}", msg)
                return
            keys = ["AtomicNumber", "AtomicMass", "Electronegativity", "BoilingPoint", "MeltingPoint", "Type"]
            output.delete('1.0', tk.END)
            log_lines = []
            for key in keys:
                a_val = data[a].get(key)
                b_val = data[b].get(key)
                line = f"{key}: {a} = {a_val}, {b} = {b_val}"
                output.insert(tk.END, line + "\n")
                log_lines.append(line)
            summary = f"Compared {a} and {b}"
            log_event("Element Comparator", f"{a} vs {b}", summary + " | " + " | ".join(log_lines))

        tk.Button(win, text="Compare", command=compare).grid(row=3, column=0, columnspan=2)
        return win

    register_window("Comparator", create_window)


# 6. Mole-Mass-Volume Tool
def open_unit_multiplier(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Mole-Mass Calculator")

        tk.Label(win, text="Moles:").pack()
        mol_entry = tk.Entry(win)
        mol_entry.pack()

        tk.Label(win, text="Molar Mass (g/mol):").pack()
        mass_entry = tk.Entry(win)
        mass_entry.pack()

        if preload and isinstance(preload, tuple) and len(preload) == 2:
            mol_entry.insert(0, str(preload[0]))
            mass_entry.insert(0, str(preload[1]))
            log_event("Mole-Mass Calculator (Chain)", f"{preload}", "Waiting for calculation")

        result = tk.Label(win, text="")
        result.pack(pady=10)

        def calc():
            try:
                mol = float(mol_entry.get())
                mm = float(mass_entry.get())
                mass = mol * mm
                volume = mol * 22.4
                output = f"Mass: {mass:.2f} g\nVolume (STP): {volume:.2f} L"
                result.config(text=output)
                log_event("Mole-Mass Calculator", f"mol={mol}, mm={mm}", output.replace('\n', ' | '))
            except Exception:
                error_msg = "Invalid input."
                result.config(text=error_msg)
                log_event("Mole-Mass Calculator", f"mol={mol_entry.get()}, mm={mass_entry.get()}", error_msg)

        tk.Button(win, text="Calculate", command=calc).pack()
        return win

    register_window("Unit Multiplier", create_window)

# 7. Element Viewer
def open_element_viewer(preload=None):
    def create_window():
        data = load_element_data()
        if not data:
            return

        win = tk.Toplevel()
        win.title("Element Viewer")

        tk.Label(win, text="Select an Element:").grid(row=0, column=0, padx=5, pady=5)
        element_var = tk.StringVar()
        dropdown = ttk.Combobox(win, textvariable=element_var, values=sorted(data.keys()), state='readonly')
        dropdown.grid(row=0, column=1, padx=5, pady=5)

        info_text = tk.Text(win, width=120, height=45, wrap='word')
        info_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        def show_info(*args):
            symbol = element_var.get()
            el = data.get(symbol)
            if el:
                info_text.delete('1.0', tk.END)
                lines = []
                for key, value in el.items():
                    line = f"{key}: {value}"
                    info_text.insert(tk.END, line + "\n")
                    lines.append(line)
                log_event("Element Viewer", symbol, f"Viewed properties ({len(lines)} lines)")

        dropdown.bind('<<ComboboxSelected>>', show_info)

        if preload and preload in data:
            element_var.set(preload)
            show_info()

        return win

    register_window("Element Viewer", create_window)


# 8. Element Property Grapher
def open_property_grapher(preload=None):
    def create_window():
        import matplotlib.pyplot as plt
        import os
        import datetime
        data = load_element_data()
        win = tk.Toplevel()
        win.title("Element Property Grapher")

        tk.Label(win, text="Select Property to Graph:").pack(pady=5)
        prop_var = tk.StringVar()
        dropdown = ttk.Combobox(win, textvariable=prop_var, state="readonly")
        dropdown["values"] = [
            "AtomicMass", "Electronegativity", "BoilingPoint", "MeltingPoint",
            "Density", "FirstIonization", "AtomicRadius", "NumberofValence"
        ]
        dropdown.pack(pady=5)
        dropdown.set("Electronegativity")

        if preload:
            prop_var.set(preload)
            log_event("Property Grapher (Chain)", preload, "Waiting for plot")

        def plot():
            prop = prop_var.get()
            symbols, xs, ys = [], [], []
            for el in data.values():
                x = el.get("AtomicNumber") or el.get("number")
                y = el.get(prop)
                if x is not None and y is not None:
                    xs.append(x)
                    ys.append(y)
                    symbols.append(el["symbol"])

            if not xs or not ys:
                log_event("Property Grapher", prop, "No data points available")
                return

            points = sorted(zip(xs, ys, symbols), key=lambda p: p[0])
            xs_sorted, ys_sorted, symbols_sorted = zip(*points)

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(xs_sorted, ys_sorted, linestyle='-', marker='o')
            for i, symbol in enumerate(symbols_sorted):
                ax.text(xs_sorted[i], ys_sorted[i], symbol, fontsize=8, ha='center')
            ax.set_xlabel("Atomic Number")
            ax.set_ylabel(prop)
            ax.set_title(f"{prop} vs Atomic Number")
            ax.grid(True)
            fig.tight_layout()

            if not os.path.exists("results"):
                os.makedirs("results")
            filename = f"results/{prop}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
            fig.savefig(filename)

            plt.show()

            summary = f"Plotted {len(xs_sorted)} elements ({symbols_sorted[0]} to {symbols_sorted[-1]})"
            log_event("Property Grapher", prop, f"{summary} [IMG:{filename}]")

        tk.Button(win, text="Plot", command=plot).pack(pady=10)
        return win

    register_window("Property Grapher", create_window)

# Open Tools
def open_chemistry_tools_hub():
    def create_window():
        win = tk.Toplevel()
        win.title("Chemistry Tools")
    
        tk.Label(win, text="Choose a Chemistry Tool:").pack(pady=10)
        tools = [
            "Element Viewer",
            "Mass Calculator",
            "Property Grapher",
            "Element Reactor",
            "Isotopic Notation",
            "Shell Visualizer",
            "Phase at 25°C",
            "Element Comparator",
            "Mole-Mass-Volume Calculator",
            "Molecule Assembler"
        ]
    
        var = tk.StringVar()
        box = ttk.Combobox(win, textvariable=var, values=tools, state="readonly")
        box.pack(pady=5)
        box.set("Select Tool")
    
        def launch():
            sel = var.get()
            if sel == "Element Viewer":
                open_element_viewer()
            elif sel == "Mass Calculator":
                open_mass_calculator()
            elif sel == "Property Grapher":
                open_property_grapher()
            elif sel == "Isotopic Notation":
                open_isotope_tool()
            elif sel == "Shell Visualizer":
                open_shell_visualizer()
            elif sel == "Phase at 25°C":
                open_phase_predictor()
            elif sel == "Element Comparator":
                open_comparator()
            elif sel == "Mole-Mass-Volume Calculator":
                open_unit_multiplier()
            elif sel == "Molecule Assembler":
                open_molecule_assembler()
    
        tk.Button(win, text="Open", command=launch).pack(pady=10)
        return win
    register_window(open_chemistry_tools_hub.__name__.replace("open_", "").replace("_", " ").title(), create_window)