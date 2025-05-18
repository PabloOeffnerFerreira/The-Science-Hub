from utils import register_window  # [AUTO-REFRACTORED]
import tkinter as tk
from tkinter import ttk
import math
from utils import log_event

conversion_data = {
    "Length": {"m": 1, "cm": 100, "mm": 1000, "km": 0.001},
    "Mass": {"kg": 1, "g": 1000, "mg": 1e6},
    "Time": {"s": 1, "min": 1/60, "h": 1/3600},
    "Temperature": {"C": 1, "F": 0, "K": 0}
}

# 1. Physics Tools Hub (menu only, no preload)
def open_physics_tools_hub(preload=None):
    def create_window():
        phys = tk.Toplevel()
        phys.title("Physics Tools")

        tk.Label(phys, text="Choose a Physics Tool:").pack(pady=10)
        tools = [
            "Unit Converter",
            "Terminal Velocity Calculator",
            "Projectile Motion",
            "Ohm's Law Calculator",
            "Lens & Mirror Equation",
            "Speed Calculator",
            "Drag Force Calculator",
            "Acceleration Calculator",
            "Force Calculator",
            "Kinetic Energy Calculator"
        ]
        var = tk.StringVar()
        dropdown = ttk.Combobox(phys, textvariable=var, values=tools, state="readonly")
        dropdown.pack(pady=5)
        dropdown.set("Select Tool")

        def launch():
            sel = var.get()
            if sel == "Unit Converter":
                open_unit_converter()
            elif sel == "Terminal Velocity Calculator":
                open_terminal_velocity_calculator()
            elif sel == "Projectile Motion":
                open_projectile_motion_tool()
            elif sel == "Ohm's Law Calculator":
                open_ohms_law_tool()
            elif sel == "Lens & Mirror Equation":
                open_lens_calculator()
            elif sel == "Speed Calculator":
                open_speed_calculator()
            elif sel == "Drag Force Calculator":
                open_drag_force_calculator()
            elif sel == "Acceleration Calculator":
                open_acceleration_calculator()
            elif sel == "Force Calculator":
                open_force_calculator()
            elif sel == "Kinetic Energy Calculator":
                open_kinetic_energy_calculator()

        tk.Button(phys, text="Open", command=launch).pack(pady=10)
        return phys

    return create_window()

    register_window("Physics Tools Hub", create_window)


# 2. Unit Converter Tool
def open_unit_converter(preload=None):
    def create_window():
        tool = tk.Toplevel()
        tool.title("Unit Converter")

        tk.Label(tool, text="Select Category:").grid(row=0, column=0, padx=5, pady=5)
        category_var = tk.StringVar(value="Length")
        category_menu = ttk.Combobox(tool, textvariable=category_var, values=list(conversion_data.keys()), state='readonly')
        category_menu.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(tool, text="From Unit:").grid(row=1, column=0, padx=5, pady=5)
        from_var = tk.StringVar()
        from_menu = ttk.Combobox(tool, textvariable=from_var, state='readonly')
        from_menu.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(tool, text="To Unit:").grid(row=2, column=0, padx=5, pady=5)
        to_var = tk.StringVar()
        to_menu = ttk.Combobox(tool, textvariable=to_var, state='readonly')
        to_menu.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(tool, text="Enter Value:").grid(row=3, column=0, padx=5, pady=5)
        entry_value = tk.Entry(tool)
        entry_value.grid(row=3, column=1, padx=5, pady=5)

        result_label = tk.Label(tool, text='', font=("Arial", 10))
        result_label.grid(row=5, column=0, columnspan=2, pady=5)

        def update_units(*args):
            cat = category_var.get()
            if cat not in conversion_data:
                return  # Invalid category, skip
            units = list(conversion_data[cat].keys())
            from_menu['values'] = units
            to_menu['values'] = units
            from_var.set(units[0])
            to_var.set(units[1])

        category_var.trace_add('write', update_units)
        update_units()

        if preload and isinstance(preload, tuple) and len(preload) == 4:
            category_var.set(preload[0])
            from_var.set(preload[1])
            to_var.set(preload[2])
            entry_value.insert(0, str(preload[3]))
            log_event("Unit Converter (Chain)", str(preload), "Waiting for conversion")

        def convert():
            try:
                val = float(entry_value.get())
                cat = category_var.get()
                from_unit = from_var.get()
                to_unit = to_var.get()

                if cat == "Temperature":
                    if from_unit == "F":
                        val_c = (val - 32) * 5 / 9
                    elif from_unit == "K":
                        val_c = val - 273.15
                    elif from_unit == "C":
                        val_c = val
                    else:
                        msg = f"Invalid 'from' unit: {from_unit}"
                        result_label.config(text=msg)
                        log_event("Unit Converter", f"Temperature from={from_unit}", msg)
                        return

                    if to_unit == "F":
                        converted = (val_c * 9 / 5) + 32
                    elif to_unit == "K":
                        converted = val_c + 273.15
                    elif to_unit == "C":
                        converted = val_c
                    else:
                        msg = f"Invalid 'to' unit: {to_unit}"
                        result_label.config(text=msg)
                        log_event("Unit Converter", f"Temperature to={to_unit}", msg)
                        return

                else:
                    # SAFEGUARD checks
                    if cat not in conversion_data:
                        msg = f"Invalid category: {cat}"
                        result_label.config(text=msg)
                        log_event("Unit Converter", f"Category={cat}", msg)
                        return
                    if from_unit not in conversion_data[cat] or to_unit not in conversion_data[cat]:
                        msg = f"Invalid units: {from_unit} to {to_unit}"
                        result_label.config(text=msg)
                        log_event("Unit Converter", f"{from_unit} to {to_unit}", msg)
                        return

                    # Proceed with safe base conversion
                    base = val * conversion_data[cat][from_unit]
                    converted = base / conversion_data[cat][to_unit]


                msg = f"{val:.2f} {from_unit} = {converted:.4f} {to_unit}"
                result_label.config(text=msg)
                log_event("Unit Converter", f"{val} {from_unit} to {to_unit}", msg)
            except ValueError:
                msg = "Invalid input value."
                result_label.config(text=msg)
                log_event("Unit Converter", entry_value.get(), msg)

        tk.Button(tool, text='Convert', command=convert).grid(row=4, column=0, columnspan=2, pady=5)

        return tool

    register_window("Unit Converter", create_window)
# 3. Terminal Velocity Calculator
def open_terminal_velocity_calculator(preload=None):
    def create_window():
        tool = tk.Toplevel()
        tool.title("Fall Time & Terminal Velocity")

        fields = [
            ("Enter mass in kg:", "1.0"),
            ("Enter Cross-Sectional Area in m²:", "0.5"),
            ("Enter height in m:", "100"),
            ("Enter drag coefficient:", "1.0"),
        ]
        entries = []

        for i, (label, default) in enumerate(fields):
            tk.Label(tool, text=label).grid(row=i, column=0, padx=5, pady=3, sticky='e')
            entry = tk.Entry(tool)
            entry.insert(0, default)
            entry.grid(row=i, column=1, padx=5, pady=3)
            entries.append(entry)

        result_label = tk.Label(tool, text='', font=("Arial", 10))
        result_label.grid(row=len(fields)+1, column=0, columnspan=2, pady=5)

        if preload and isinstance(preload, tuple) and len(preload) == 4:
            for e, val in zip(entries, preload):
                e.delete(0, tk.END)
                e.insert(0, str(val))
            log_event("Terminal Velocity (Chain)", str(preload), "Waiting for calculation")

        def calculate():
            try:
                mass = float(entries[0].get())
                area = float(entries[1].get())
                height = float(entries[2].get())
                Cd = float(entries[3].get())
                g = 9.81
                rho = 1.225
                v_terminal = math.sqrt((2 * mass * g) / (rho * area * Cd))
                t = math.sqrt((2 * height) / g)
                msg = f"Terminal Velocity ≈ {v_terminal:.2f} m/s\nFall Time ≈ {t:.2f} s (without drag)"
                result_label.config(text=msg)
                log_event("Terminal Velocity", f"mass={mass}, area={area}, height={height}, Cd={Cd}", msg.replace('\n', ' | '))
            except ValueError:
                msg = "Please enter valid numbers."
                result_label.config(text=msg)
                log_event("Terminal Velocity", "invalid", msg)

        tk.Button(tool, text='Calculate', command=calculate).grid(row=len(fields), column=0, columnspan=2, pady=5)
        return tool

    register_window("Terminal Velocity Calculator", create_window)


# 4. Projectile Motion
def open_projectile_motion_tool(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Projectile Motion")

        fields = [
            ("Initial velocity (m/s):", "20"),
            ("Angle (degrees):", "45")
        ]
        entries = []
        for label, default in fields:
            tk.Label(win, text=label).pack()
            e = tk.Entry(win)
            e.insert(0, default)
            e.pack()
            entries.append(e)

        if preload and isinstance(preload, tuple) and len(preload) == 2:
            entries[0].delete(0, tk.END)
            entries[1].delete(0, tk.END)
            entries[0].insert(0, str(preload[0]))
            entries[1].insert(0, str(preload[1]))
            log_event("Projectile Motion (Chain)", str(preload), "Waiting for calculation")

        result = tk.Label(win, text="")
        result.pack(pady=5)

        def calculate():
            try:
                v = float(entries[0].get())
                angle = math.radians(float(entries[1].get()))
                g = 9.81
                range_ = (v ** 2) * math.sin(2 * angle) / g
                height = (v ** 2) * (math.sin(angle) ** 2) / (2 * g)
                time = 2 * v * math.sin(angle) / g
                msg = f"Range: {range_:.2f} m\nMax Height: {height:.2f} m\nFlight Time: {time:.2f} s"
                result.config(text=msg)
                log_event("Projectile Motion", f"v={v}, angle={math.degrees(angle)}°", msg.replace('\n', ' | '))
            except Exception:
                msg = "Invalid input."
                result.config(text=msg)
                log_event("Projectile Motion", f"v={entries[0].get()}, angle={entries[1].get()}", msg)

        tk.Button(win, text="Calculate", command=calculate).pack(pady=5)
        return win

    register_window("Projectile Motion Tool", create_window)


# 5. Ohm's Law Calculator
def open_ohms_law_tool(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Ohm's Law Calculator")

        tk.Label(win, text="Enter two known values (leave one blank):").pack()
        tk.Label(win, text="Voltage (V):").pack()
        voltage_entry = tk.Entry(win)
        voltage_entry.pack()
        tk.Label(win, text="Current (A):").pack()
        current_entry = tk.Entry(win)
        current_entry.pack()
        tk.Label(win, text="Resistance (Ω):").pack()
        resistance_entry = tk.Entry(win)
        resistance_entry.pack()

        if preload and isinstance(preload, tuple) and len(preload) == 3:
            voltage_entry.insert(0, str(preload[0]) if preload[0] is not None else '')
            current_entry.insert(0, str(preload[1]) if preload[1] is not None else '')
            resistance_entry.insert(0, str(preload[2]) if preload[2] is not None else '')
            log_event("Ohm's Law (Chain)", str(preload), "Waiting for solve")

        result = tk.Label(win, text="")
        result.pack(pady=5)

        def solve():
            try:
                V = voltage_entry.get()
                I = current_entry.get()
                R = resistance_entry.get()
                if V == '':
                    V = float(I) * float(R)
                    msg = f"Voltage = {V:.2f} V"
                elif I == '':
                    I = float(V) / float(R)
                    msg = f"Current = {I:.2f} A"
                elif R == '':
                    R = float(V) / float(I)
                    msg = f"Resistance = {R:.2f} Ω"
                else:
                    msg = "Leave one field empty."
                result.config(text=msg)
                log_event("Ohm's Law", f"V={voltage_entry.get()}, I={current_entry.get()}, R={resistance_entry.get()}", msg)
            except Exception:
                msg = "Invalid input."
                result.config(text=msg)
                log_event("Ohm's Law", f"V={voltage_entry.get()}, I={current_entry.get()}, R={resistance_entry.get()}", msg)

        tk.Button(win, text="Solve", command=solve).pack(pady=5)
        return win

    register_window("Ohms Law Tool", create_window)


# 6. Lens Calculator
def open_lens_calculator(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Lens & Mirror Equation")

        tk.Label(win, text="Enter two of the three values (leave one blank):").pack()
        tk.Label(win, text="Focal length (f):").pack()
        f_entry = tk.Entry(win)
        f_entry.pack()
        tk.Label(win, text="Object distance (do):").pack()
        do_entry = tk.Entry(win)
        do_entry.pack()
        tk.Label(win, text="Image distance (di):").pack()
        di_entry = tk.Entry(win)
        di_entry.pack()

        if preload and isinstance(preload, tuple) and len(preload) == 3:
            f_entry.insert(0, str(preload[0]) if preload[0] is not None else '')
            do_entry.insert(0, str(preload[1]) if preload[1] is not None else '')
            di_entry.insert(0, str(preload[2]) if preload[2] is not None else '')
            log_event("Lens Calculator (Chain)", str(preload), "Waiting for solve")

        result = tk.Label(win, text="")
        result.pack(pady=5)

        def calculate():
            try:
                f = f_entry.get()
                do = do_entry.get()
                di = di_entry.get()
                if f == '':
                    f_val = 1 / (1/float(do) + 1/float(di))
                    msg = f"Focal length = {f_val:.2f}"
                elif do == '':
                    do_val = 1 / (1/float(f) - 1/float(di))
                    msg = f"Object distance = {do_val:.2f}"
                elif di == '':
                    di_val = 1 / (1/float(f) - 1/float(do))
                    msg = f"Image distance = {di_val:.2f}"
                else:
                    msg = "Leave one field empty."
                result.config(text=msg)
                log_event("Lens Calculator", f"f={f}, do={do}, di={di}", msg)
            except Exception:
                msg = "Invalid input."
                result.config(text=msg)
                log_event("Lens Calculator", f"f={f_entry.get()}, do={do_entry.get()}, di={di_entry.get()}", msg)

        tk.Button(win, text="Calculate", command=calculate).pack(pady=5)
        return win

    register_window("Lens & Mirror Equation", create_window)

import tkinter as tk
from utils import register_window, log_event

# 7. Speed Calc

def open_speed_calculator(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Speed Calculator")

        tk.Label(win, text="Enter Distance (m):").pack()
        dist_entry = tk.Entry(win, width=20)
        dist_entry.pack(pady=5)

        tk.Label(win, text="Enter Time (s):").pack()
        time_entry = tk.Entry(win, width=20)
        time_entry.pack(pady=5)

        result_label = tk.Label(win, text="")
        result_label.pack(pady=10)

        def compute():
            try:
                dist = float(dist_entry.get())
                time = float(time_entry.get())
                if time == 0:
                    raise ValueError("Time cannot be zero")
                speed = dist / time
                result_label.config(text=f"Speed = {speed:.3f} m/s")
                log_event("Speed Calculator", f"Distance={dist}, Time={time}", speed)
            except Exception as e:
                result_label.config(text=f"Error: {e}")

        tk.Button(win, text="Calculate Speed", command=compute).pack(pady=5)

        if preload:
            # Optional: parse preload input if needed
            pass

        return win

    register_window("Speed Calculator", create_window)

# 8. Drag calc

def open_drag_force_calculator(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Drag Force Calculator")

        tk.Label(win, text="Enter Air Density ρ (kg/m³):").pack()
        density_entry = tk.Entry(win, width=20)
        density_entry.pack(pady=5)

        tk.Label(win, text="Enter Velocity v (m/s):").pack()
        velocity_entry = tk.Entry(win, width=20)
        velocity_entry.pack(pady=5)

        tk.Label(win, text="Enter Drag Coefficient Cd:").pack()
        cd_entry = tk.Entry(win, width=20)
        cd_entry.pack(pady=5)

        tk.Label(win, text="Enter Cross-sectional Area A (m²):").pack()
        area_entry = tk.Entry(win, width=20)
        area_entry.pack(pady=5)

        result_label = tk.Label(win, text="")
        result_label.pack(pady=10)

        def compute():
            try:
                rho = float(density_entry.get())
                v = float(velocity_entry.get())
                cd = float(cd_entry.get())
                A = float(area_entry.get())
                Fd = 0.5 * rho * v**2 * cd * A
                result_label.config(text=f"Drag Force = {Fd:.3f} N")
                log_event("Drag Force Calculator", f"ρ={rho}, v={v}, Cd={cd}, A={A}", Fd)
            except Exception as e:
                result_label.config(text=f"Error: {e}")

        tk.Button(win, text="Calculate Drag Force", command=compute).pack(pady=5)

        return win

    register_window("Drag Force Calculator", create_window)

# 9. Accelaration Calc
def open_acceleration_calculator(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Acceleration Calculator")

        tk.Label(win, text="Enter Change in Velocity Δv (m/s):").pack()
        dv_entry = tk.Entry(win, width=20)
        dv_entry.pack(pady=5)

        tk.Label(win, text="Enter Time (s):").pack()
        time_entry = tk.Entry(win, width=20)
        time_entry.pack(pady=5)

        result_label = tk.Label(win, text="")
        result_label.pack(pady=10)

        def compute():
            try:
                dv = float(dv_entry.get())
                t = float(time_entry.get())
                if t == 0:
                    raise ValueError("Time cannot be zero")
                a = dv / t
                result_label.config(text=f"Acceleration = {a:.3f} m/s²")
                log_event("Acceleration Calculator", f"Δv={dv}, t={t}", a)
            except Exception as e:
                result_label.config(text=f"Error: {e}")

        tk.Button(win, text="Calculate", command=compute).pack(pady=5)

        return win

    register_window("Acceleration Calculator", create_window)

#9. Force Calc

def open_force_calculator(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Force Calculator")

        tk.Label(win, text="Enter Mass (kg):").pack()
        mass_entry = tk.Entry(win, width=20)
        mass_entry.pack(pady=5)

        tk.Label(win, text="Enter Acceleration (m/s²):").pack()
        accel_entry = tk.Entry(win, width=20)
        accel_entry.pack(pady=5)

        result_label = tk.Label(win, text="")
        result_label.pack(pady=10)

        def compute():
            try:
                m = float(mass_entry.get())
                a = float(accel_entry.get())
                F = m * a
                result_label.config(text=f"Force = {F:.3f} N")
                log_event("Force Calculator", f"m={m}, a={a}", F)
            except Exception as e:
                result_label.config(text=f"Error: {e}")

        tk.Button(win, text="Calculate", command=compute).pack(pady=5)

        return win

    register_window("Force Calculator", create_window)

# 10. Kinetic Energy Calc

def open_kinetic_energy_calculator(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Kinetic Energy Calculator")

        tk.Label(win, text="Enter Mass (kg):").pack()
        mass_entry = tk.Entry(win, width=20)
        mass_entry.pack(pady=5)

        tk.Label(win, text="Enter Velocity (m/s):").pack()
        velocity_entry = tk.Entry(win, width=20)
        velocity_entry.pack(pady=5)

        result_label = tk.Label(win, text="")
        result_label.pack(pady=10)

        def compute():
            try:
                m = float(mass_entry.get())
                v = float(velocity_entry.get())
                KE = 0.5 * m * v**2
                result_label.config(text=f"Kinetic Energy = {KE:.3f} J")
                log_event("Kinetic Energy Calculator", f"m={m}, v={v}", KE)
            except Exception as e:
                result_label.config(text=f"Error: {e}")

        tk.Button(win, text="Calculate", command=compute).pack(pady=5)

        return win

    register_window("Kinetic Energy Calculator", create_window)
