from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
)
from data_utils import log_event, _open_dialogs
import math
from data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data, ai_chatlogs_dir
)
conversion_data = {
    "Length": {
        "m": 1,
        "km": 1000,
        "cm": 0.01,
        "mm": 0.001,
        "μm": 1e-6,
        "nm": 1e-9,
        "mile": 1609.344,
        "yard": 0.9144,
        "foot": 0.3048,
        "inch": 0.0254,
        "nautical mile": 1852,
        "angstrom": 1e-10,
        "light year": 9.4607e15,
        "astronomical unit": 1.496e11,
        "parsec": 3.085677581e16,
    },
    "Mass": {
        "kg": 1,
        "g": 0.001,
        "mg": 1e-6,
        "μg": 1e-9,
        "tonne": 1000,
        "lb": 0.45359237,
        "oz": 0.0283495231,
        "stone": 6.35029318,
        "atomic mass unit": 1.66053906660e-27,
        "solar mass": 1.98847e30,
        "earth mass": 5.9722e24,
    },
    "Time": {
        "s": 1,
        "ms": 0.001,
        "μs": 1e-6,
        "ns": 1e-9,
        "min": 60,
        "h": 3600,
        "day": 86400,
        "week": 604800,
        "year": 31557600,  # 365.25 days (Julian year)
        "month": 2629800,  # average
        "century": 3155760000,
    },
    "Temperature": {
        "C": None, "K": None, "F": None,
    },
    "Area": {
        "m²": 1,
        "km²": 1e6,
        "cm²": 1e-4,
        "mm²": 1e-6,
        "hectare": 1e4,
        "acre": 4046.8564224,
        "ft²": 0.09290304,
        "in²": 0.00064516,
        "mi²": 2.59e6,
    },
    "Volume": {
        "m³": 1,
        "L": 0.001,
        "mL": 1e-6,
        "cm³": 1e-6,
        "mm³": 1e-9,
        "ft³": 0.0283168466,
        "in³": 1.6387064e-5,
        "gal (US)": 0.00378541178,
        "qt (US)": 0.000946352946,
        "pt (US)": 0.000473176473,
        "cup (US)": 0.0002365882365,
        "tbsp (US)": 1.47867648e-5,
        "tsp (US)": 4.92892159e-6,
    },
    "Speed": {
        "m/s": 1,
        "km/h": 0.277777778,
        "mph": 0.44704,
        "knot": 0.514444444,
        "ft/s": 0.3048,
        "c (speed of light)": 299792458,
    },
    "Pressure": {
        "Pa": 1,
        "kPa": 1000,
        "MPa": 1e6,
        "bar": 100000,
        "atm": 101325,
        "mmHg": 133.322368,
        "torr": 133.322368,
        "psi": 6894.75729,
        "mbar": 100,
    },
    "Energy": {
        "J": 1,
        "kJ": 1000,
        "cal": 4.184,
        "kcal": 4184,
        "Wh": 3600,
        "kWh": 3.6e6,
        "eV": 1.602176634e-19,
        "BTU": 1055.05585,
        "ft-lb": 1.35581795,
    },
    "Power": {
        "W": 1,
        "kW": 1000,
        "MW": 1e6,
        "hp": 745.699872,
        "ft-lb/s": 1.35581795,
        "BTU/h": 0.29307107,
    },
    "Electric Charge": {
        "C": 1,
        "mC": 0.001,
        "μC": 1e-6,
        "nC": 1e-9,
        "Ah": 3600,
        "mAh": 3.6,
        "e (elementary charge)": 1.602176634e-19,
    },
    "Electric Potential": {
        "V": 1,
        "mV": 0.001,
        "kV": 1000,
    },
    "Electric Current": {
        "A": 1,
        "mA": 0.001,
        "μA": 1e-6,
        "kA": 1000,
    },
    "Frequency": {
        "Hz": 1,
        "kHz": 1000,
        "MHz": 1e6,
        "GHz": 1e9,
        "THz": 1e12,
        "rpm": 1/60,
    },
    "Data Size": {
        "bit": 1,
        "byte": 8,
        "kB": 8e3,
        "MB": 8e6,
        "GB": 8e9,
        "TB": 8e12,
        "PB": 8e15,
    },
    "Luminance": {
        "cd/m²": 1,
        "nit": 1,
        "stilb": 10000,
        "foot-lambert": 3.4262591,
    },
    "Force": {
        "N": 1,
        "dyn": 1e-5,
        "lbf": 4.44822162,
        "kgf": 9.80665,
        "ozf": 0.2780139,
    },
    "Angle": {
        "rad": 1,
        "deg": 0.017453292519943295,
        "grad": 0.015707963267948967,
        "arcmin": 0.0002908882086657216,
        "arcsec": 0.00000484813681109536,
        "revolution": 6.283185307179586,
    },
    "Fuel Consumption": {
        "L/100km": 1,
        "mpg (US)": 235.214583,
        "mpg (Imp)": 282.480936,
        "km/L": 100,
    },
    "Magnetic Field": {
        "T": 1,
        "G": 1e-4,
        "mT": 0.001,
        "μT": 1e-6,
    },
    "Illuminance": {
        "lux": 1,
        "ph": 1e4,
        "foot-candle": 10.76391,
    },
    "Radioactivity": {
        "Bq": 1,
        "Ci": 3.7e10,
        "dpm": 1/60,
    },
}

def open_unit_converter():
    class UnitConverterDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Unit Converter")
            layout = QVBoxLayout(self)

            row = QHBoxLayout()
            row.addWidget(QLabel("Category:"))
            self.category = QComboBox()
            self.category.addItems(conversion_data.keys())
            row.addWidget(self.category)
            layout.addLayout(row)

            row2 = QHBoxLayout()
            row2.addWidget(QLabel("From:"))
            self.from_unit = QComboBox()
            row2.addWidget(self.from_unit)
            layout.addLayout(row2)
            row3 = QHBoxLayout()
            row3.addWidget(QLabel("To:"))
            self.to_unit = QComboBox()
            row3.addWidget(self.to_unit)
            layout.addLayout(row3)

            self.value_edit = QLineEdit()
            row4 = QHBoxLayout()
            row4.addWidget(QLabel("Value:"))
            row4.addWidget(self.value_edit)
            layout.addLayout(row4)

            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Convert")
            btn.clicked.connect(self.convert)
            layout.addWidget(btn)

            self.category.currentTextChanged.connect(self.update_units)
            self.update_units()

        def update_units(self):
            cat = self.category.currentText()
            units = list(conversion_data[cat].keys())
            self.from_unit.clear()
            self.from_unit.addItems(units)
            self.to_unit.clear()
            self.to_unit.addItems(units)
            if len(units) > 1:
                self.from_unit.setCurrentIndex(0)
                self.to_unit.setCurrentIndex(1)

        def convert(self):
            try:
                val = float(self.value_edit.text())
                cat = self.category.currentText()
                from_unit = self.from_unit.currentText()
                to_unit = self.to_unit.currentText()
                if cat == "Temperature":
                    if from_unit == "F":
                        val_c = (val - 32) * 5 / 9
                    elif from_unit == "K":
                        val_c = val - 273.15
                    elif from_unit == "C":
                        val_c = val
                    else:
                        msg = f"Invalid 'from' unit: {from_unit}"
                        self.result.setText(msg)
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
                        self.result.setText(msg)
                        log_event("Unit Converter", f"Temperature to={to_unit}", msg)
                        return
                else:
                    if cat not in conversion_data:
                        msg = f"Invalid category: {cat}"
                        self.result.setText(msg)
                        log_event("Unit Converter", f"Category={cat}", msg)
                        return
                    if from_unit not in conversion_data[cat] or to_unit not in conversion_data[cat]:
                        msg = f"Invalid units: {from_unit} to {to_unit}"
                        self.result.setText(msg)
                        log_event("Unit Converter", f"{from_unit} to {to_unit}", msg)
                        return
                    base = val * conversion_data[cat][from_unit]
                    converted = base / conversion_data[cat][to_unit]
                msg = f"{val:.2f} {from_unit} = {converted:.4f} {to_unit}"
                self.result.setText(msg)
                log_event("Unit Converter", f"{val} {from_unit} to {to_unit}", msg)
            except Exception:
                msg = "Invalid input value."
                self.result.setText(msg)
                log_event("Unit Converter", self.value_edit.text(), msg)

    dlg = UnitConverterDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))


import math
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QCheckBox)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

def open_terminal_velocity_calculator():
    class TerminalDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Terminal Velocity Calculator")
            self.setMinimumWidth(500)
            layout = QVBoxLayout(self)

            # Mass input + units
            row_mass = QHBoxLayout()
            row_mass.addWidget(QLabel("Mass:"))
            self.mass_edit = QLineEdit("1.0")
            self.mass_unit = QComboBox()
            self.mass_unit.addItems(["kg", "lb"])
            row_mass.addWidget(self.mass_edit)
            row_mass.addWidget(self.mass_unit)
            layout.addLayout(row_mass)

            # Area input + units
            row_area = QHBoxLayout()
            row_area.addWidget(QLabel("Cross-sectional Area:"))
            self.area_edit = QLineEdit("0.5")
            self.area_unit = QComboBox()
            self.area_unit.addItems(["m²", "cm²", "in²"])
            row_area.addWidget(self.area_edit)
            row_area.addWidget(self.area_unit)
            layout.addLayout(row_area)

            # Height input + units
            row_height = QHBoxLayout()
            row_height.addWidget(QLabel("Height:"))
            self.height_edit = QLineEdit("100")
            self.height_unit = QComboBox()
            self.height_unit.addItems(["m", "ft"])
            row_height.addWidget(self.height_edit)
            row_height.addWidget(self.height_unit)
            layout.addLayout(row_height)

            # Air density / Altitude input
            row_air = QHBoxLayout()
            row_air.addWidget(QLabel("Air Density (kg/m³) or Altitude (m):"))
            self.air_mode = QComboBox()
            self.air_mode.addItems(["Air Density", "Altitude", "Custom"])
            self.air_value = QLineEdit("1.225")
            row_air.addWidget(self.air_mode)
            row_air.addWidget(self.air_value)
            layout.addLayout(row_air)

            # Drag coefficient presets
            row_cd = QHBoxLayout()
            row_cd.addWidget(QLabel("Drag Coefficient:"))
            self.cd_preset = QComboBox()
            self.cd_preset.addItems([
                "Sphere (0.47)",
                "Flat Plate (1.28)",
                "Cylinder (1.2)",
                "Streamlined Body (0.04)",
                "Custom"
            ])
            self.cd_edit = QLineEdit("1.0")
            row_cd.addWidget(self.cd_preset)
            row_cd.addWidget(self.cd_edit)
            layout.addLayout(row_cd)

            # Calculate button
            self.result_label = QLabel("")
            layout.addWidget(self.result_label)
            btn_calc = QPushButton("Calculate")
            btn_calc.clicked.connect(self.calculate)
            layout.addWidget(btn_calc)

            # Plot area using matplotlib
            self.figure = Figure(figsize=(5, 3))
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)

            # Connections
            self.air_mode.currentTextChanged.connect(self.update_air_mode)
            self.cd_preset.currentTextChanged.connect(self.update_cd_preset)
            self.update_air_mode()
            self.update_cd_preset()

        def update_air_mode(self):
            mode = self.air_mode.currentText()
            if mode == "Air Density":
                self.air_value.setText("1.225")
                self.air_value.setEnabled(False)
            elif mode == "Altitude":
                self.air_value.setText("0")
                self.air_value.setEnabled(True)
            else:  # Custom
                self.air_value.setEnabled(True)

        def update_cd_preset(self):
            preset = self.cd_preset.currentText()
            mapping = {
                "Sphere (0.47)": "0.47",
                "Flat Plate (1.28)": "1.28",
                "Cylinder (1.2)": "1.2",
                "Streamlined Body (0.04)": "0.04"
            }
            if preset in mapping:
                self.cd_edit.setText(mapping[preset])
                self.cd_edit.setEnabled(False)
            else:
                self.cd_edit.setEnabled(True)

        def calculate(self):
            import numpy as np
            import datetime

            try:
                # Convert inputs to SI units
                mass = float(self.mass_edit.text())
                if self.mass_unit.currentText() == "lb":
                    mass *= 0.45359237  # lb to kg

                area = float(self.area_edit.text())
                if self.area_unit.currentText() == "cm²":
                    area *= 1e-4
                elif self.area_unit.currentText() == "in²":
                    area *= 0.00064516

                height = float(self.height_edit.text())
                if self.height_unit.currentText() == "ft":
                    height *= 0.3048

                # Air density calculation
                air_mode = self.air_mode.currentText()
                air_val = float(self.air_value.text())
                if air_mode == "Altitude":
                    # Simple barometric formula approximation
                    h = air_val
                    if h < 11000:
                        T0 = 288.15
                        L = 0.0065
                        p0 = 101325
                        R = 8.31447
                        M = 0.0289644
                        g = 9.80665
                        T = T0 - L * h
                        p = p0 * (T / T0) ** (g * M / (R * L))
                        rho = p * M / (8.31447 * T)
                    else:
                        rho = 0.364  # Approx constant above 11km
                elif air_mode == "Air Density":
                    rho = 1.225
                else:
                    rho = air_val

                Cd = float(self.cd_edit.text())

                g = 9.81

                # Terminal velocity formula
                v_terminal = math.sqrt((2 * mass * g) / (rho * area * Cd))

                # Numerical integration for fall time and velocity over time
                dt = 0.01
                v = 0
                y = height
                t = 0
                times = []
                velocities = []
                while y > 0:
                    F_gravity = mass * g
                    F_drag = 0.5 * rho * v * v * Cd * area
                    a = (F_gravity - F_drag) / mass if v >= 0 else (F_gravity + F_drag) / mass
                    v += a * dt
                    y -= v * dt
                    if y < 0:
                        y = 0
                    t += dt
                    times.append(t)
                    velocities.append(v)

                msg = (f"Terminal Velocity ≈ {v_terminal:.2f} m/s\n"
                       f"Fall Time with drag ≈ {t:.2f} s\n"
                       f"Fall Time without drag ≈ {math.sqrt(2 * height / g):.2f} s")
                self.result_label.setText(msg)

                # Plot velocity vs time
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.plot(times, velocities)
                ax.set_xlabel("Time (s)")
                ax.set_ylabel("Velocity (m/s)")
                ax.set_title("Velocity vs Time")
                ax.grid(True)
                self.canvas.draw()

                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                img_name = f"terminal_velocity_{timestamp}.png"
                img_path = os.path.join(results_dir, img_name)
                self.figure.savefig(img_path, dpi=150)

                msg = (f"Terminal Velocity ≈ {v_terminal:.2f} m/s\n"
                        f"Fall Time with drag ≈ {t:.2f} s\n"
                        f"Fall Time without drag ≈ {math.sqrt(2 * height / g):.2f} s\n"
                        f"Plot saved to {img_path}")

                self.result_label.setText(msg)

                log_event("Terminal Velocity", f"mass={mass}, area={area}, height={height}, Cd={Cd}, rho={rho}, plot={img_path}", msg.replace('\n', ' | '))

            except Exception as e:
                self.result_label.setText("Please enter valid numbers.")
                log_event("Terminal Velocity", "invalid", str(e))

    dlg = TerminalDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

def open_projectile_motion_tool():
    class ProjectileDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Projectile Motion")
            layout = QVBoxLayout(self)

            # Initial velocity input + unit selector
            row_v = QHBoxLayout()
            row_v.addWidget(QLabel("Initial Velocity:"))
            self.v_edit = QLineEdit("20")
            self.v_unit = QComboBox()
            self.v_unit.addItems(["m/s", "km/h", "mph"])
            row_v.addWidget(self.v_edit)
            row_v.addWidget(self.v_unit)
            layout.addLayout(row_v)

            # Angle input + unit selector
            row_angle = QHBoxLayout()
            row_angle.addWidget(QLabel("Launch Angle:"))
            self.angle_edit = QLineEdit("45")
            self.angle_unit = QComboBox()
            self.angle_unit.addItems(["degrees", "radians"])
            row_angle.addWidget(self.angle_edit)
            row_angle.addWidget(self.angle_unit)
            layout.addLayout(row_angle)

            # Initial height input + unit selector
            row_h = QHBoxLayout()
            row_h.addWidget(QLabel("Initial Height:"))
            self.h_edit = QLineEdit("0")
            self.h_unit = QComboBox()
            self.h_unit.addItems(["m", "ft"])
            row_h.addWidget(self.h_edit)
            row_h.addWidget(self.h_unit)
            layout.addLayout(row_h)

            # Result display
            self.result_label = QLabel("")
            layout.addWidget(self.result_label)

            # Matplotlib plot area
            self.figure = Figure(figsize=(6, 4))
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)

            # Buttons
            btn_calc = QPushButton("Calculate")
            btn_calc.clicked.connect(self.calculate)
            layout.addWidget(btn_calc)

            btn_anim = QPushButton("Start Animation")
            btn_anim.clicked.connect(self.start_animation)
            layout.addWidget(btn_anim)

            # Timer for animation
            from PyQt6.QtCore import QTimer
            self.timer = QTimer()
            self.timer.timeout.connect(self.animate_step)
            self.anim_index = 0

            self.x_vals = []
            self.y_vals = []

        def calculate(self):
            try:
                v = float(self.v_edit.text())
                angle = float(self.angle_edit.text())
                h = float(self.h_edit.text())
                g = 9.81

                # Convert units to SI
                if self.v_unit.currentText() == "km/h":
                    v /= 3.6
                elif self.v_unit.currentText() == "mph":
                    v *= 0.44704

                if self.angle_unit.currentText() == "degrees":
                    angle = math.radians(angle)

                if self.h_unit.currentText() == "ft":
                    h *= 0.3048

                # Time to max height
                t_max_height = v * math.sin(angle) / g

                # Max height
                max_height = h + (v ** 2) * (math.sin(angle) ** 2) / (2 * g)

                # Flight time by solving quadratic for y=0
                a = -0.5 * g
                b = v * math.sin(angle)
                c = h
                discriminant = b ** 2 - 4 * a * c
                if discriminant < 0:
                    self.result_label.setText("No valid flight time (check inputs).")
                    return
                t_flight = (-b - math.sqrt(discriminant)) / (2 * a)
                if t_flight < 0:
                    t_flight = (-b + math.sqrt(discriminant)) / (2 * a)

                # Range
                range_ = v * math.cos(angle) * t_flight

                # Impact velocity components
                vx_impact = v * math.cos(angle)
                vy_impact = -g * t_flight + v * math.sin(angle)
                impact_speed = math.sqrt(vx_impact ** 2 + vy_impact ** 2)

                # Prepare trajectory for plotting
                import numpy as np
                self.x_vals = np.linspace(0, range_, num=500)
                self.y_vals = h + self.x_vals * math.tan(angle) - (g * self.x_vals ** 2) / (2 * (v * math.cos(angle)) ** 2)
                self.y_vals = np.maximum(self.y_vals, 0)  # Clamp to ground

                msg = (f"Range: {range_:.2f} m\n"
                       f"Max Height: {max_height:.2f} m\n"
                       f"Flight Time: {t_flight:.2f} s\n"
                       f"Time to Max Height: {t_max_height:.2f} s\n"
                       f"Impact Velocity: {impact_speed:.2f} m/s\n"
                       f"Velocity X at Impact: {vx_impact:.2f} m/s\n"
                       f"Velocity Y at Impact: {vy_impact:.2f} m/s")

                self.result_label.setText(msg)

                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.plot(self.x_vals, self.y_vals)
                ax.set_xlabel("Horizontal Distance (m)")
                ax.set_ylabel("Vertical Height (m)")
                ax.set_title("Projectile Trajectory")
                ax.grid(True)
                self.canvas.draw()

                self.anim_index = 0

                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                img_name = f"projectile_trajectory_{timestamp}.png"
                img_path = os.path.join(results_dir, img_name)
                self.figure.savefig(img_path, dpi=150)

                # Optionally update the result label to include the saved file path:
                self.result_label.setText(self.result_label.text() + f"\nPlot saved to {img_path}")

                # Log the export event
                log_event("Projectile Motion", f"v={v}, angle={math.degrees(angle):.2f}°, h={h}, plot={img_path}", "Plot saved")

            except Exception as e:
                self.result_label.setText("Invalid input.")
                log_event("Projectile Motion", f"error: {str(e)}", "")

        def start_animation(self):
            if len(self.x_vals) == 0 or len(self.y_vals) == 0:
                self.result_label.setText("Calculate first.")
                return
            self.anim_index = 0
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            self.ax.set_xlim(0, max(self.x_vals) * 1.1)
            self.ax.set_ylim(0, max(self.y_vals) * 1.1)
            self.point, = self.ax.plot([], [], 'ro')
            self.ax.plot(self.x_vals, self.y_vals, 'b-')
            self.canvas.draw()
            self.timer.start(30)  # 30 ms update interval

        def animate_step(self):
            if self.anim_index >= len(self.x_vals):
                self.timer.stop()
                return
            self.point.set_data([self.x_vals[self.anim_index]], [self.y_vals[self.anim_index]])
            self.anim_index += 1
            self.canvas.draw_idle()

    dlg = ProjectileDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
)
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression
from data_utils import log_event, _open_dialogs


def open_ohms_law_tool():
    class OhmDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Ohm's Law Calculator")
            self.setMinimumWidth(350)

            main_layout = QVBoxLayout(self)
            main_layout.addWidget(QLabel("Enter two known values (leave one blank):"))

            # Units lists
            self.voltage_units = ['V', 'mV', 'kV']
            self.current_units = ['A', 'mA', 'kA']
            self.resistance_units = ['Ω', 'mΩ', 'kΩ', 'MΩ']

            # Input validators: allow digits and dot only
            regex = QRegularExpression(r"[0-9]*\.?[0-9]*")
            validator = QRegularExpressionValidator(regex)

            # Voltage input + unit
            self.voltage_edit = QLineEdit()
            self.voltage_edit.setValidator(validator)
            self.voltage_edit.setText("120")  # prefill simple number
            self.voltage_unit = QComboBox()
            self.voltage_unit.addItems(self.voltage_units)
            self.voltage_unit.setCurrentText("V")

            # Current input + unit
            self.current_edit = QLineEdit()
            self.current_edit.setValidator(validator)
            self.current_edit.setText("20")
            self.current_unit = QComboBox()
            self.current_unit.addItems(self.current_units)
            self.current_unit.setCurrentText("mA")

            # Resistance input + unit
            self.resistance_edit = QLineEdit()
            self.resistance_edit.setValidator(validator)
            self.resistance_edit.setText("")
            self.resistance_unit = QComboBox()
            self.resistance_unit.addItems(self.resistance_units)
            self.resistance_unit.setCurrentText("Ω")

            # Layout for each input
            def create_row(label_text, edit, unit_combo):
                row = QHBoxLayout()
                row.addWidget(QLabel(label_text))
                row.addWidget(edit)
                row.addWidget(unit_combo)
                return row

            main_layout.addLayout(create_row("Voltage:", self.voltage_edit, self.voltage_unit))
            main_layout.addLayout(create_row("Current:", self.current_edit, self.current_unit))
            main_layout.addLayout(create_row("Resistance:", self.resistance_edit, self.resistance_unit))

            # Result display
            self.result_label = QLabel("")
            main_layout.addWidget(self.result_label)

            # Buttons
            btn_layout = QHBoxLayout()
            self.solve_btn = QPushButton("Solve")
            self.clear_btn = QPushButton("Clear")
            btn_layout.addWidget(self.solve_btn)
            btn_layout.addWidget(self.clear_btn)
            main_layout.addLayout(btn_layout)

            # Connect signals
            self.solve_btn.clicked.connect(self.solve)
            self.clear_btn.clicked.connect(self.clear_all)

            # Track last units for conversion
            self.last_voltage_unit = self.voltage_unit.currentText()
            self.last_current_unit = self.current_unit.currentText()
            self.last_resistance_unit = self.resistance_unit.currentText()

            # Flag to prevent recursion on unit change
            self.updating = False

            # Connect unit changes
            self.voltage_unit.currentTextChanged.connect(self.on_voltage_unit_changed)
            self.current_unit.currentTextChanged.connect(self.on_current_unit_changed)
            self.resistance_unit.currentTextChanged.connect(self.on_resistance_unit_changed)

        # Unit conversion helpers
        def convert_to_base(self, val, unit):
            if unit == 'mV':
                return val / 1000
            if unit == 'kV':
                return val * 1000
            if unit == 'mA':
                return val / 1000
            if unit == 'kA':
                return val * 1000
            if unit == 'mΩ':
                return val / 1000
            if unit == 'kΩ':
                return val * 1000
            if unit == 'MΩ':
                return val * 1e6
            return val

        def convert_from_base(self, val, unit):
            if unit == 'mV':
                return val * 1000
            if unit == 'kV':
                return val / 1000
            if unit == 'mA':
                return val * 1000
            if unit == 'kA':
                return val / 1000
            if unit == 'mΩ':
                return val * 1000
            if unit == 'kΩ':
                return val / 1000
            if unit == 'MΩ':
                return val / 1e6
            return val

        def format_clean(self, val):
            if val.is_integer():
                return str(int(val))
            else:
                return f"{val:.6g}"

        # Handle unit changes properly converting the value
        def _update_value_on_unit_change(self, edit, old_unit, new_unit):
            try:
                val = float(edit.text())
            except ValueError:
                return
            base_val = self.convert_to_base(val, old_unit)
            new_val = self.convert_from_base(base_val, new_unit)
            edit.setText(self.format_clean(new_val))

        def on_voltage_unit_changed(self, new_unit):
            if self.updating:
                return
            self.updating = True
            self._update_value_on_unit_change(self.voltage_edit, self.last_voltage_unit, new_unit)
            self.last_voltage_unit = new_unit
            self.updating = False

        def on_current_unit_changed(self, new_unit):
            if self.updating:
                return
            self.updating = True
            self._update_value_on_unit_change(self.current_edit, self.last_current_unit, new_unit)
            self.last_current_unit = new_unit
            self.updating = False

        def on_resistance_unit_changed(self, new_unit):
            if self.updating:
                return
            self.updating = True
            self._update_value_on_unit_change(self.resistance_edit, self.last_resistance_unit, new_unit)
            self.last_resistance_unit = new_unit
            self.updating = False

        def solve(self):
            # Grab inputs safely
            try:
                V_str = self.voltage_edit.text()
                I_str = self.current_edit.text()
                R_str = self.resistance_edit.text()

                V = None if V_str == "" else float(V_str)
                I = None if I_str == "" else float(I_str)
                R = None if R_str == "" else float(R_str)

                # Check how many are provided
                provided = sum(x is not None for x in [V, I, R])
                if provided != 2:
                    self.result_label.setText("Please fill exactly two fields.")
                    return

                # Convert all inputs to base units
                if V is not None:
                    V_base = self.convert_to_base(V, self.voltage_unit.currentText())
                if I is not None:
                    I_base = self.convert_to_base(I, self.current_unit.currentText())
                if R is not None:
                    R_base = self.convert_to_base(R, self.resistance_unit.currentText())

                # Calculate missing value in base units
                if V is None:
                    V_base = I_base * R_base
                    V_out = self.convert_from_base(V_base, self.voltage_unit.currentText())
                    msg = f"Voltage = {self.format_clean(V_out)} {self.voltage_unit.currentText()}"
                elif I is None:
                    I_base = V_base / R_base
                    I_out = self.convert_from_base(I_base, self.current_unit.currentText())
                    msg = f"Current = {self.format_clean(I_out)} {self.current_unit.currentText()}"
                elif R is None:
                    R_base = V_base / I_base
                    R_out = self.convert_from_base(R_base, self.resistance_unit.currentText())
                    msg = f"Resistance = {self.format_clean(R_out)} {self.resistance_unit.currentText()}"
                else:
                    msg = "Leave one field empty."

                self.result_label.setText(msg)
                log_event("Ohm's Law",
                          f"V={V_str} {self.voltage_unit.currentText()}, "
                          f"I={I_str} {self.current_unit.currentText()}, "
                          f"R={R_str} {self.resistance_unit.currentText()}", msg)

            except Exception:
                self.result_label.setText("Invalid input.")
                log_event("Ohm's Law", "error", "Invalid input.")

        def clear_all(self):
            self.voltage_edit.setText("120")
            self.current_edit.setText("20")
            self.resistance_edit.clear()
            self.result_label.clear()

    dlg = OhmDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))


import math
import datetime
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QMessageBox
)
from PyQt6.QtGui import QDoubleValidator
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from data_utils import log_event, _open_dialogs, results_dir

def open_lens_calculator():
    class LensDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Lens & Mirror Equation")
            self.setMinimumWidth(500)
            layout = QVBoxLayout(self)

            layout.addWidget(QLabel("Enter two of the three values (leave one blank):"))

            units = ["m", "cm", "mm", "in", "ft"]

            # Inputs + units
            self.f_edit = QLineEdit("0.1")  # default focal length 0.1 m
            self.f_unit = QComboBox()
            self.f_unit.addItems(units)
            self.f_unit.setCurrentIndex(0)  # default to meters

            self.do_edit = QLineEdit("0.5")  # default object distance 0.5 m
            self.do_unit = QComboBox()
            self.do_unit.addItems(units)
            self.do_unit.setCurrentIndex(0)

            self.di_edit = QLineEdit("")
            self.di_unit = QComboBox()
            self.di_unit.addItems(units)
            self.di_unit.setCurrentIndex(0)

            # Validators
            validator = QDoubleValidator(bottom=-1e12, top=1e12, decimals=6)
            for edit in (self.f_edit, self.do_edit, self.di_edit):
                edit.setValidator(validator)

            # Tooltips
            self.f_edit.setToolTip("Focal length of the lens or mirror. Positive for converging lens/mirror, negative for diverging.")
            self.do_edit.setToolTip("Object distance from the lens or mirror.")
            self.di_edit.setToolTip("Image distance from the lens or mirror.")

            # Lens or mirror toggle

            self.is_mirror = QCheckBox("Mirror (uncheck for Lens)")
            layout.addWidget(self.is_mirror)
            self.is_mirror.setChecked(False)  # default: lens
            self.is_mirror.setToolTip("Toggle to calculate for mirror (different sign conventions).")

            # Layout inputs
            for label, edit, unit in [
                ("Focal length (f):", self.f_edit, self.f_unit),
                ("Object distance (do):", self.do_edit, self.do_unit),
                ("Image distance (di):", self.di_edit, self.di_unit),
            ]:
                row = QHBoxLayout()
                row.addWidget(QLabel(label))
                row.addWidget(edit)
                row.addWidget(unit)
                layout.addLayout(row)

            # Result label
            self.result = QLabel("")
            layout.addWidget(self.result)

            # Matplotlib figure and canvas
            self.figure = Figure(figsize=(6, 4))
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)

            # Buttons row
            row_buttons = QHBoxLayout()
            self.btn_calc = QPushButton("Calculate")
            self.btn_calc.clicked.connect(self.calculate)
            self.btn_clear = QPushButton("Clear")
            self.btn_clear.clicked.connect(self.clear_all)
            row_buttons.addWidget(self.btn_calc)
            row_buttons.addWidget(self.btn_clear)
            layout.addLayout(row_buttons)

        def convert_to_meters(self, val_str, unit_str):
            if val_str == "":
                return None
            val = float(val_str)
            if unit_str == "cm":
                val *= 0.01
            elif unit_str == "mm":
                val *= 0.001
            elif unit_str == "in":
                val *= 0.0254
            elif unit_str == "ft":
                val *= 0.3048
            return val

        def convert_from_meters(self, val, unit_str):
            if unit_str == "cm":
                return val / 0.01
            elif unit_str == "mm":
                return val / 0.001
            elif unit_str == "in":
                return val / 0.0254
            elif unit_str == "ft":
                return val / 0.3048
            return val

        def calculate(self):
            try:
                f_val = self.convert_to_meters(self.f_edit.text(), self.f_unit.currentText())
                do_val = self.convert_to_meters(self.do_edit.text(), self.do_unit.currentText())
                di_val = self.convert_to_meters(self.di_edit.text(), self.di_unit.currentText())

                provided = sum(v is not None for v in [f_val, do_val, di_val])
                if provided != 2:
                    self.result.setText("Error: Please fill exactly two fields.")
                    return

                # Adjust sign convention for mirrors
                if self.is_mirror.isChecked():
                    # For mirrors, focal length is negative for converging concave mirrors
                    if f_val is not None:
                        f_val = -abs(f_val) if f_val > 0 else f_val

                # Calculate missing value
                if f_val is None:
                    f_val = 1 / (1 / do_val + 1 / di_val)
                    missing_label = "Focal length"
                    missing_unit = self.f_unit.currentText()
                    result_val = self.convert_from_meters(f_val, missing_unit)
                elif do_val is None:
                    do_val = 1 / (1 / f_val - 1 / di_val)
                    missing_label = "Object distance"
                    missing_unit = self.do_unit.currentText()
                    result_val = self.convert_from_meters(do_val, missing_unit)
                elif di_val is None:
                    di_val = 1 / (1 / f_val - 1 / do_val)
                    missing_label = "Image distance"
                    missing_unit = self.di_unit.currentText()
                    result_val = self.convert_from_meters(di_val, missing_unit)
                else:
                    self.result.setText("Error: Leave one field empty.")
                    return

                # Magnification
                magnification = -di_val / do_val if do_val != 0 else float('inf')

                # Lens type
                lens_type = "Converging" if f_val > 0 else "Diverging"
                if self.is_mirror.isChecked():
                    lens_type += " Mirror"
                else:
                    lens_type += " Lens"

                # Build message
                msg = (f"{missing_label} = {result_val:.3f} {missing_unit}\n"
                       f"Magnification = {magnification:.3f}\n"
                       f"Type: {lens_type}")

                self.result.setText(msg)

                # Plot ray diagram
                self.plot_ray_diagram(f_val, do_val, di_val)

                log_event("Lens Calculator", 
                          f"f={self.f_edit.text()} {self.f_unit.currentText()}, "
                          f"do={self.do_edit.text()} {self.do_unit.currentText()}, "
                          f"di={self.di_edit.text()} {self.di_unit.currentText()}, "
                          f"type={'Mirror' if self.is_mirror.isChecked() else 'Lens'}", 
                          msg)

            except Exception as e:
                self.result.setText("Invalid input.")
                log_event("Lens Calculator", "error", str(e))

        def plot_ray_diagram(self, f, do, di):
            # Basic ray diagram for thin lens or mirror on optical axis
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.set_title("Ray Diagram")
            ax.set_xlabel("Distance (m)")
            ax.set_ylabel("Height (m)")
            ax.grid(True)
            ax.axvline(0, color='black', linewidth=1)  # lens/mirror plane

            # Setup scale
            max_dist = max(abs(do), abs(di), abs(f)) * 1.5
            ax.set_xlim(-max_dist*0.5, max_dist)
            ax.set_ylim(-max_dist*0.5, max_dist*0.5)

            # Draw principal axis
            ax.axhline(0, color='gray', linestyle='--')

            # Object position and height (assume height 1m)
            obj_height = 1.0
            ax.plot([-do, -do], [0, obj_height], 'g', linewidth=3, label='Object')

            # Image position and height
            img_height = -di/do * obj_height if do != 0 else 0
            ax.plot([di, di], [0, img_height], 'r', linewidth=3, label='Image')

            # Focal points
            ax.plot([f, f], [-0.1, 0.1], 'bo', label='Focal Point')
            ax.plot([-f, -f], [-0.1, 0.1], 'bo')

            # Draw rays (3 principal rays for lens/mirror)

            # Ray 1: parallel to axis then through focal point
            ax.plot([-do, 0], [obj_height, obj_height], 'b')
            if not self.is_mirror.isChecked():
                ax.plot([0, di], [obj_height, 0], 'b')
            else:
                # For mirrors ray reflects through focal point
                ax.plot([0, di], [obj_height, 0], 'b')

            # Ray 2: through center of lens/mirror (undeviated)
            ax.plot([-do, di], [obj_height, img_height], 'm')

            # Ray 3: through focal point then parallel to axis
            if not self.is_mirror.isChecked():
                ax.plot([-do, -f], [obj_height, 0], 'c')
                ax.plot([-f, di], [0, img_height], 'c')
            else:
                ax.plot([-do, 0], [obj_height, 0], 'c')
                ax.plot([0, di], [0, img_height], 'c')

            ax.legend(loc='upper right')

            self.canvas.draw()

            # Save plot image
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            img_name = f"lens_ray_diagram_{timestamp}.png"
            img_path = os.path.join(results_dir, img_name)
            self.figure.savefig(img_path, dpi=150)

            # Append image path to result label
            current_text = self.result.text()
            self.result.setText(current_text + f"\nRay diagram saved to {img_path}")

            # Log export event
            log_event("Lens Calculator", "ray diagram export", img_path)

        def clear_all(self):
            self.f_edit.clear()
            self.do_edit.clear()
            self.di_edit.clear()
            self.result.clear()
            self.figure.clear()
            self.canvas.draw()
            self.is_mirror.setChecked(False)

    dlg = LensDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))


def open_speed_calculator():
    class SpeedDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Speed Calculator")
            self.setMinimumWidth(350)
            layout = QVBoxLayout(self)

            # Units options
            self.dist_units = ["m", "km", "mile", "ft"]
            self.time_units = ["s", "min", "hr"]
            self.speed_units = ["m/s", "km/h", "mph"]

            # Distance input + units
            dist_row = QHBoxLayout()
            dist_row.addWidget(QLabel("Distance:"))
            self.dist_edit = QLineEdit("100")
            dist_row.addWidget(self.dist_edit)
            self.dist_unit = QComboBox()
            self.dist_unit.addItems(self.dist_units)
            dist_row.addWidget(self.dist_unit)
            layout.addLayout(dist_row)

            # Time input + units
            time_row = QHBoxLayout()
            time_row.addWidget(QLabel("Time:"))
            self.time_edit = QLineEdit("10")
            time_row.addWidget(self.time_edit)
            self.time_unit = QComboBox()
            self.time_unit.addItems(self.time_units)
            time_row.addWidget(self.time_unit)
            layout.addLayout(time_row)

            # Output unit selector (optional)
            output_row = QHBoxLayout()
            output_row.addWidget(QLabel("Output speed unit:"))
            self.speed_unit = QComboBox()
            self.speed_unit.addItems(self.speed_units)
            output_row.addWidget(self.speed_unit)
            layout.addLayout(output_row)

            # Result label
            self.result_label = QLabel("")
            layout.addWidget(self.result_label)

            # Calculate button
            btn = QPushButton("Calculate Speed")
            btn.clicked.connect(self.compute)
            layout.addWidget(btn)

        def convert_distance_to_meters(self, val, unit):
            if unit == "m":
                return val
            elif unit == "km":
                return val * 1000
            elif unit == "mile":
                return val * 1609.344
            elif unit == "ft":
                return val * 0.3048

        def convert_time_to_seconds(self, val, unit):
            if unit == "s":
                return val
            elif unit == "min":
                return val * 60
            elif unit == "hr":
                return val * 3600

        def convert_speed_from_m_s(self, speed_m_s, unit):
            if unit == "m/s":
                return speed_m_s
            elif unit == "km/h":
                return speed_m_s * 3.6
            elif unit == "mph":
                return speed_m_s * 2.23694

        def compute(self):
            try:
                dist = float(self.dist_edit.text())
                time = float(self.time_edit.text())

                if time == 0:
                    raise ValueError("Time cannot be zero")

                dist_m = self.convert_distance_to_meters(dist, self.dist_unit.currentText())
                time_s = self.convert_time_to_seconds(time, self.time_unit.currentText())
                speed_m_s = dist_m / time_s

                speed_out = self.convert_speed_from_m_s(speed_m_s, self.speed_unit.currentText())
                self.result_label.setText(f"Speed = {speed_out:.3f} {self.speed_unit.currentText()}")

                log_event(
                    "Speed Calculator",
                    f"Distance={dist} {self.dist_unit.currentText()}, Time={time} {self.time_unit.currentText()}",
                    f"Speed={speed_out:.3f} {self.speed_unit.currentText()}"
                )

            except Exception as e:
                self.result_label.setText(f"Error: {e}")

    dlg = SpeedDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
def open_drag_force_calculator():
    class DragDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Drag Force Calculator")
            self.setMinimumWidth(350)
            layout = QVBoxLayout(self)

            # Units options
            self.density_units = ["kg/m³", "g/cm³"]
            self.velocity_units = ["m/s", "km/h", "mph"]
            self.area_units = ["m²", "cm²", "ft²"]

            # Input fields with validators and prefill
            decimal_regex = QRegularExpression(r"[0-9]*\.?[0-9]*")
            validator = QRegularExpressionValidator(decimal_regex)

            self.density_edit = QLineEdit("1.225")  # air density at sea level in kg/m³
            self.density_edit.setValidator(validator)
            self.density_unit = QComboBox()
            self.density_unit.addItems(self.density_units)

            self.velocity_edit = QLineEdit("10")
            self.velocity_edit.setValidator(validator)
            self.velocity_unit = QComboBox()
            self.velocity_unit.addItems(self.velocity_units)

            self.cd_edit = QLineEdit("1.0")
            self.cd_edit.setValidator(validator)

            self.area_edit = QLineEdit("0.5")
            self.area_edit.setValidator(validator)
            self.area_unit = QComboBox()
            self.area_unit.addItems(self.area_units)

            # Layout helper
            def make_row(label_text, edit_widget, unit_combo=None):
                row = QHBoxLayout()
                row.addWidget(QLabel(label_text))
                row.addWidget(edit_widget)
                if unit_combo:
                    row.addWidget(unit_combo)
                return row

            layout.addLayout(make_row("Air Density ρ:", self.density_edit, self.density_unit))
            layout.addLayout(make_row("Velocity v:", self.velocity_edit, self.velocity_unit))
            layout.addLayout(make_row("Drag Coefficient Cd:", self.cd_edit))
            layout.addLayout(make_row("Cross-sectional Area A:", self.area_edit, self.area_unit))

            self.result_label = QLabel("")
            layout.addWidget(self.result_label)

            btn_layout = QHBoxLayout()
            self.calc_btn = QPushButton("Calculate Drag Force")
            self.clear_btn = QPushButton("Clear")
            btn_layout.addWidget(self.calc_btn)
            btn_layout.addWidget(self.clear_btn)
            layout.addLayout(btn_layout)

            # Connections
            self.calc_btn.clicked.connect(self.compute)
            self.clear_btn.clicked.connect(self.clear_all)

        def convert_to_SI_density(self, val, unit):
            if unit == "g/cm³":
                return val * 1000  # 1 g/cm³ = 1000 kg/m³
            return val

        def convert_to_SI_velocity(self, val, unit):
            if unit == "km/h":
                return val / 3.6
            elif unit == "mph":
                return val * 0.44704
            return val

        def convert_to_SI_area(self, val, unit):
            if unit == "cm²":
                return val / 10000
            elif unit == "ft²":
                return val * 0.092903
            return val

        def compute(self):
            try:
                rho = float(self.density_edit.text())
                v = float(self.velocity_edit.text())
                cd = float(self.cd_edit.text())
                A = float(self.area_edit.text())

                rho_si = self.convert_to_SI_density(rho, self.density_unit.currentText())
                v_si = self.convert_to_SI_velocity(v, self.velocity_unit.currentText())
                A_si = self.convert_to_SI_area(A, self.area_unit.currentText())

                Fd = 0.5 * rho_si * v_si**2 * cd * A_si
                self.result_label.setText(f"Drag Force = {Fd:.3f} N")
                log_event("Drag Force Calculator",
                          f"ρ={rho} {self.density_unit.currentText()}, "
                          f"v={v} {self.velocity_unit.currentText()}, "
                          f"Cd={cd}, "
                          f"A={A} {self.area_unit.currentText()}",
                          f"{Fd:.3f} N")
            except Exception as e:
                self.result_label.setText(f"Error: {e}")

        def clear_all(self):
            self.density_edit.setText("1.225")
            self.velocity_edit.setText("10")
            self.cd_edit.setText("1.0")
            self.area_edit.setText("0.5")
            self.result_label.clear()

    dlg = DragDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
def open_acceleration_calculator():
    class AccelDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Acceleration Calculator")
            self.setMinimumWidth(350)
            layout = QVBoxLayout(self)

            # Units options
            self.velocity_units = ["m/s", "km/h", "mph"]
            self.time_units = ["s", "min", "hr"]

            # Input fields with validator
            decimal_regex = QRegularExpression(r"[0-9]*\.?[0-9]*")
            validator = QRegularExpressionValidator(decimal_regex)

            self.dv_edit = QLineEdit("10")
            self.dv_edit.setValidator(validator)
            self.dv_unit = QComboBox()
            self.dv_unit.addItems(self.velocity_units)
            self.dv_unit.setCurrentText("m/s")

            self.time_edit = QLineEdit("5")
            self.time_edit.setValidator(validator)
            self.time_unit = QComboBox()
            self.time_unit.addItems(self.time_units)
            self.time_unit.setCurrentText("s")

            # Layout helpers
            def make_row(label_text, edit_widget, unit_combo):
                row = QHBoxLayout()
                row.addWidget(QLabel(label_text))
                row.addWidget(edit_widget)
                row.addWidget(unit_combo)
                return row

            layout.addLayout(make_row("Change in Velocity Δv:", self.dv_edit, self.dv_unit))
            layout.addLayout(make_row("Time:", self.time_edit, self.time_unit))

            self.result_label = QLabel("")
            layout.addWidget(self.result_label)

            btn_layout = QHBoxLayout()
            self.calc_btn = QPushButton("Calculate")
            self.clear_btn = QPushButton("Clear")
            btn_layout.addWidget(self.calc_btn)
            btn_layout.addWidget(self.clear_btn)
            layout.addLayout(btn_layout)

            # Connect signals
            self.calc_btn.clicked.connect(self.compute)
            self.clear_btn.clicked.connect(self.clear_all)

        def convert_to_m_s(self, val, unit):
            if unit == "km/h":
                return val / 3.6
            elif unit == "mph":
                return val * 0.44704
            return val

        def convert_to_seconds(self, val, unit):
            if unit == "min":
                return val * 60
            elif unit == "hr":
                return val * 3600
            return val

        def convert_from_m_s2(self, val, unit):
            # Converts acceleration in m/s² to unit / s² if needed (usually m/s² output is standard)
            # You can expand this if you want other acceleration units
            return val

        def compute(self):
            try:
                dv = float(self.dv_edit.text())
                t = float(self.time_edit.text())
                if t == 0:
                    raise ValueError("Time cannot be zero")

                dv_m_s = self.convert_to_m_s(dv, self.dv_unit.currentText())
                t_s = self.convert_to_seconds(t, self.time_unit.currentText())

                a = dv_m_s / t_s
                a_out = self.convert_from_m_s2(a, "m/s²")  # Keep m/s² output for now

                self.result_label.setText(f"Acceleration = {a_out:.3f} m/s²")
                log_event("Acceleration Calculator", f"Δv={dv} {self.dv_unit.currentText()}, t={t} {self.time_unit.currentText()}", a_out)
            except Exception as e:
                self.result_label.setText(f"Error: {e}")

        def clear_all(self):
            self.dv_edit.setText("10")
            self.dv_unit.setCurrentText("m/s")
            self.time_edit.setText("5")
            self.time_unit.setCurrentText("s")
            self.result_label.clear()

    dlg = AccelDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
)
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression
from data_utils import log_event, _open_dialogs
import numpy as np

def open_force_calculator():
    class ForceDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Force Calculator")
            self.setMinimumWidth(400)
            layout = QVBoxLayout(self)

            self.mass_units = ["kg", "g", "lb"]
            self.accel_units = ["m/s²", "ft/s²"]

            decimal_regex = QRegularExpression(r"[0-9]*\.?[0-9]*")
            validator = QRegularExpressionValidator(decimal_regex)

            # Mass input and unit
            self.mass_edit = QLineEdit("1")
            self.mass_edit.setValidator(validator)
            self.mass_unit = QComboBox()
            self.mass_unit.addItems(self.mass_units)
            self.mass_unit.setCurrentText("kg")

            # Acceleration input and unit
            self.accel_edit = QLineEdit("9.81")
            self.accel_edit.setValidator(validator)
            self.accel_unit = QComboBox()
            self.accel_unit.addItems(self.accel_units)
            self.accel_unit.setCurrentText("m/s²")

            def create_row(label, edit, unit):
                row = QHBoxLayout()
                row.addWidget(QLabel(label))
                row.addWidget(edit)
                row.addWidget(unit)
                return row

            layout.addLayout(create_row("Mass:", self.mass_edit, self.mass_unit))
            layout.addLayout(create_row("Acceleration:", self.accel_edit, self.accel_unit))

            self.result_label = QLabel("")
            layout.addWidget(self.result_label)

            btn_layout = QHBoxLayout()
            self.calc_btn = QPushButton("Calculate")
            self.clear_btn = QPushButton("Clear")
            btn_layout.addWidget(self.calc_btn)
            btn_layout.addWidget(self.clear_btn)
            layout.addLayout(btn_layout)

            # Matplotlib plot
            self.figure = plt.figure(figsize=(5,3))
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)

            self.last_mass_unit = self.mass_unit.currentText()
            self.last_accel_unit = self.accel_unit.currentText()
            self.updating = False

            # Connect signals
            self.mass_unit.currentIndexChanged.connect(
                lambda idx: self.on_mass_unit_changed(self.mass_unit.currentText())
            )
            self.accel_unit.currentIndexChanged.connect(
                lambda idx: self.on_accel_unit_changed(self.accel_unit.currentText())
            )
            self.calc_btn.clicked.connect(self.compute)
            self.clear_btn.clicked.connect(self.clear_all)

        def convert_to_kg(self, val, unit):
            if unit == "g":
                return val / 1000
            elif unit == "lb":
                return val * 0.453592
            return val

        def convert_from_kg(self, val, unit):
            if unit == "g":
                return val * 1000
            elif unit == "lb":
                return val / 0.453592
            return val

        def convert_to_m_s2(self, val, unit):
            if unit == "ft/s²":
                return val * 0.3048
            return val

        def convert_from_m_s2(self, val, unit):
            if unit == "ft/s²":
                return val / 0.3048
            return val

        def format_clean(self, val):
            if val.is_integer():
                return str(int(val))
            else:
                return f"{val:.6g}"

        def _update_value_on_unit_change(self, line_edit, old_unit, new_unit, to_base_func, from_base_func):
            try:
                val = float(line_edit.text())
            except ValueError:
                return
            base_val = to_base_func(val, old_unit)
            new_val = from_base_func(base_val, new_unit)
            line_edit.setText(self.format_clean(new_val))

        def on_mass_unit_changed(self, new_unit):
            if self.updating:
                return
            self.updating = True
            self._update_value_on_unit_change(self.mass_edit, self.last_mass_unit, new_unit, self.convert_to_kg, self.convert_from_kg)
            self.last_mass_unit = new_unit
            self.updating = False

        def on_accel_unit_changed(self, new_unit):
            if self.updating:
                return
            self.updating = True
            self._update_value_on_unit_change(self.accel_edit, self.last_accel_unit, new_unit, self.convert_to_m_s2, self.convert_from_m_s2)
            self.last_accel_unit = new_unit
            self.updating = False

        def compute(self):
            try:
                m = float(self.mass_edit.text())
                a = float(self.accel_edit.text())

                m_kg = self.convert_to_kg(m, self.mass_unit.currentText())
                a_m_s2 = self.convert_to_m_s2(a, self.accel_unit.currentText())

                F = m_kg * a_m_s2
                self.result_label.setText(f"Force = {F:.3f} N")
                log_event("Force Calculator", f"m={m} {self.mass_unit.currentText()}, a={a} {self.accel_unit.currentText()}", F)

                # Plot Force vs Acceleration for fixed mass range +/- 50%
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                accel_range = np.linspace(a_m_s2 * 0.5, a_m_s2 * 1.5, 100)
                force_vals = m_kg * accel_range
                ax.plot(accel_range, force_vals, label=f"Mass = {m_kg:.3f} kg")
                ax.scatter([a_m_s2], [F], color='red', label="Current Value")
                ax.set_xlabel("Acceleration (m/s²)")
                ax.set_ylabel("Force (N)")
                ax.set_title("Force vs Acceleration")
                ax.legend()
                ax.grid(True)
                self.canvas.draw()

            except Exception as e:
                self.result_label.setText(f"Error: {e}")

        def clear_all(self):
            self.mass_edit.setText("1")
            self.mass_unit.setCurrentText("kg")
            self.accel_edit.setText("9.81")
            self.accel_unit.setCurrentText("m/s²")
            self.result_label.clear()
            self.figure.clear()
            self.canvas.draw()

    dlg = ForceDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
)
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression
from data_utils import log_event, _open_dialogs
import numpy as np

def open_kinetic_energy_calculator():
    class KEnergyDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Kinetic Energy Calculator")
            self.setMinimumWidth(400)
            layout = QVBoxLayout(self)

            self.mass_units = ["kg", "g", "lb"]
            self.velocity_units = ["m/s", "km/h", "mph"]

            decimal_regex = QRegularExpression(r"[0-9]*\.?[0-9]*")
            validator = QRegularExpressionValidator(decimal_regex)

            self.mass_edit = QLineEdit("1")
            self.mass_edit.setValidator(validator)
            self.mass_unit = QComboBox()
            self.mass_unit.addItems(self.mass_units)
            self.mass_unit.setCurrentText("kg")

            self.velocity_edit = QLineEdit("10")
            self.velocity_edit.setValidator(validator)
            self.velocity_unit = QComboBox()
            self.velocity_unit.addItems(self.velocity_units)
            self.velocity_unit.setCurrentText("m/s")

            def create_row(label, edit, unit):
                row = QHBoxLayout()
                row.addWidget(QLabel(label))
                row.addWidget(edit)
                row.addWidget(unit)
                return row

            layout.addLayout(create_row("Mass:", self.mass_edit, self.mass_unit))
            layout.addLayout(create_row("Velocity:", self.velocity_edit, self.velocity_unit))

            self.result_label = QLabel("")
            layout.addWidget(self.result_label)

            btn_layout = QHBoxLayout()
            self.calc_btn = QPushButton("Calculate")
            self.clear_btn = QPushButton("Clear")
            btn_layout.addWidget(self.calc_btn)
            btn_layout.addWidget(self.clear_btn)
            layout.addLayout(btn_layout)

            self.figure = plt.figure(figsize=(5, 3))
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)

            self.last_mass_unit = self.mass_unit.currentText()
            self.last_velocity_unit = self.velocity_unit.currentText()
            self.updating = False

            self.mass_unit.currentIndexChanged.connect(
                lambda idx: self.on_mass_unit_changed(self.mass_unit.currentText())
            )
            self.velocity_unit.currentIndexChanged.connect(
                lambda idx: self.on_velocity_unit_changed(self.velocity_unit.currentText())
            )
            self.calc_btn.clicked.connect(self.compute)
            self.clear_btn.clicked.connect(self.clear_all)

        def convert_to_kg(self, val, unit):
            if unit == "g":
                return val / 1000
            elif unit == "lb":
                return val * 0.453592
            return val

        def convert_from_kg(self, val, unit):
            if unit == "g":
                return val * 1000
            elif unit == "lb":
                return val / 0.453592
            return val

        def convert_to_m_s(self, val, unit):
            if unit == "km/h":
                return val / 3.6
            elif unit == "mph":
                return val * 0.44704
            return val

        def convert_from_m_s(self, val, unit):
            if unit == "km/h":
                return val * 3.6
            elif unit == "mph":
                return val / 0.44704
            return val

        def format_clean(self, val):
            if val.is_integer():
                return str(int(val))
            else:
                return f"{val:.6g}"

        def _update_value_on_unit_change(self, line_edit, old_unit, new_unit, to_base_func, from_base_func):
            try:
                val = float(line_edit.text())
            except ValueError:
                return
            base_val = to_base_func(val, old_unit)
            new_val = from_base_func(base_val, new_unit)
            line_edit.setText(self.format_clean(new_val))

        def on_mass_unit_changed(self, new_unit):
            if self.updating:
                return
            self.updating = True
            self._update_value_on_unit_change(self.mass_edit, self.last_mass_unit, new_unit, self.convert_to_kg, self.convert_from_kg)
            self.last_mass_unit = new_unit
            self.updating = False

        def on_velocity_unit_changed(self, new_unit):
            if self.updating:
                return
            self.updating = True
            self._update_value_on_unit_change(self.velocity_edit, self.last_velocity_unit, new_unit, self.convert_to_m_s, self.convert_from_m_s)
            self.last_velocity_unit = new_unit
            self.updating = False

        def compute(self):
            try:
                m = float(self.mass_edit.text())
                v = float(self.velocity_edit.text())

                m_kg = self.convert_to_kg(m, self.mass_unit.currentText())
                v_m_s = self.convert_to_m_s(v, self.velocity_unit.currentText())

                KE = 0.5 * m_kg * v_m_s**2
                self.result_label.setText(f"Kinetic Energy = {KE:.3f} J")
                log_event("Kinetic Energy Calculator", f"m={m} {self.mass_unit.currentText()}, v={v} {self.velocity_unit.currentText()}", KE)

                # Plot KE vs Velocity for fixed mass +/-50%
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                velocities = np.linspace(v_m_s * 0.5, v_m_s * 1.5, 100)
                KE_values = 0.5 * m_kg * velocities**2
                ax.plot(velocities, KE_values, label=f"Mass = {m_kg:.3f} kg")
                ax.scatter([v_m_s], [KE], color='red', label="Current Value")
                ax.set_xlabel("Velocity (m/s)")
                ax.set_ylabel("Kinetic Energy (J)")
                ax.set_title("Kinetic Energy vs Velocity")
                ax.legend()
                ax.grid(True)
                self.canvas.draw()

            except Exception as e:
                self.result_label.setText(f"Error: {e}")

        def clear_all(self):
            self.mass_edit.setText("1")
            self.mass_unit.setCurrentText("kg")
            self.velocity_edit.setText("10")
            self.velocity_unit.setCurrentText("m/s")
            self.result_label.clear()
            self.figure.clear()
            self.canvas.draw()

    dlg = KEnergyDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
