from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
)
from tools.data_utils import log_event, _open_dialogs
import math
from tools.data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data, ai_chatlogs_dir
)
conversion_data = {
    "Length": {"m": 1, "cm": 100, "mm": 1000, "km": 0.001},
    "Mass": {"kg": 1, "g": 1000, "mg": 1e6},
    "Time": {"s": 1, "min": 1/60, "h": 1/3600},
    "Temperature": {"C": 1, "F": 0, "K": 0}
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


def open_terminal_velocity_calculator():
    class TerminalDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Terminal Velocity Calculator")
            layout = QVBoxLayout(self)
            self.mass = QLineEdit("1.0")
            self.area = QLineEdit("0.5")
            self.height = QLineEdit("100")
            self.cd = QLineEdit("1.0")
            for label, edit in [
                ("Mass (kg):", self.mass),
                ("Cross-sectional Area (m²):", self.area),
                ("Height (m):", self.height),
                ("Drag Coefficient:", self.cd)
            ]:
                row = QHBoxLayout()
                row.addWidget(QLabel(label))
                row.addWidget(edit)
                layout.addLayout(row)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Calculate")
            btn.clicked.connect(self.calculate)
            layout.addWidget(btn)
            self.setMinimumWidth(320)
        def calculate(self):
            try:
                mass = float(self.mass.text())
                area = float(self.area.text())
                height = float(self.height.text())
                Cd = float(self.cd.text())
                g = 9.81
                rho = 1.225
                v_terminal = math.sqrt((2 * mass * g) / (rho * area * Cd))
                t = math.sqrt((2 * height) / g)
                msg = f"Terminal Velocity ≈ {v_terminal:.2f} m/s\nFall Time ≈ {t:.2f} s (without drag)"
                self.result.setText(msg)
                log_event("Terminal Velocity", f"mass={mass}, area={area}, height={height}, Cd={Cd}", msg.replace('\n', ' | '))
            except ValueError:
                msg = "Please enter valid numbers."
                self.result.setText(msg)
                log_event("Terminal Velocity", "invalid", msg)
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
            self.v = QLineEdit("20")
            self.angle = QLineEdit("45")
            for label, edit in [
                ("Initial Velocity (m/s):", self.v),
                ("Angle (degrees):", self.angle)
            ]:
                row = QHBoxLayout()
                row.addWidget(QLabel(label))
                row.addWidget(edit)
                layout.addLayout(row)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Calculate")
            btn.clicked.connect(self.calculate)
            layout.addWidget(btn)
            self.setMinimumWidth(300)
        def calculate(self):
            try:
                v = float(self.v.text())
                angle = math.radians(float(self.angle.text()))
                g = 9.81
                range_ = (v ** 2) * math.sin(2 * angle) / g
                height = (v ** 2) * (math.sin(angle) ** 2) / (2 * g)
                time = 2 * v * math.sin(angle) / g
                msg = f"Range: {range_:.2f} m\nMax Height: {height:.2f} m\nFlight Time: {time:.2f} s"
                self.result.setText(msg)
                log_event("Projectile Motion", f"v={v}, angle={math.degrees(angle)}°", msg.replace('\n', ' | '))
            except Exception:
                msg = "Invalid input."
                self.result.setText(msg)
                log_event("Projectile Motion", f"v={self.v.text()}, angle={self.angle.text()}", msg)
    dlg = ProjectileDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))


def open_ohms_law_tool():
    class OhmDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Ohm's Law Calculator")
            layout = QVBoxLayout(self)
            self.voltage = QLineEdit()
            self.current = QLineEdit()
            self.resistance = QLineEdit()
            layout.addWidget(QLabel("Enter two known values (leave one blank):"))
            for label, edit in [
                ("Voltage (V):", self.voltage),
                ("Current (A):", self.current),
                ("Resistance (Ω):", self.resistance)
            ]:
                row = QHBoxLayout()
                row.addWidget(QLabel(label))
                row.addWidget(edit)
                layout.addLayout(row)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Solve")
            btn.clicked.connect(self.solve)
            layout.addWidget(btn)
            self.setMinimumWidth(320)
        def solve(self):
            try:
                V = self.voltage.text()
                I = self.current.text()
                R = self.resistance.text()
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
                self.result.setText(msg)
                log_event("Ohm's Law", f"V={self.voltage.text()}, I={self.current.text()}, R={self.resistance.text()}", msg)
            except Exception:
                msg = "Invalid input."
                self.result.setText(msg)
                log_event("Ohm's Law", f"V={self.voltage.text()}, I={self.current.text()}, R={self.resistance.text()}", msg)
    dlg = OhmDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))


def open_lens_calculator():
    class LensDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Lens & Mirror Equation")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Enter two of the three values (leave one blank):"))
            self.f = QLineEdit()
            self.do = QLineEdit()
            self.di = QLineEdit()
            for label, edit in [
                ("Focal length (f):", self.f),
                ("Object distance (do):", self.do),
                ("Image distance (di):", self.di)
            ]:
                row = QHBoxLayout()
                row.addWidget(QLabel(label))
                row.addWidget(edit)
                layout.addLayout(row)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Calculate")
            btn.clicked.connect(self.calculate)
            layout.addWidget(btn)
            self.setMinimumWidth(320)
        def calculate(self):
            try:
                f = self.f.text()
                do = self.do.text()
                di = self.di.text()
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
                self.result.setText(msg)
                log_event("Lens Calculator", f"f={f}, do={do}, di={di}", msg)
            except Exception:
                msg = "Invalid input."
                self.result.setText(msg)
                log_event("Lens Calculator", f"f={self.f.text()}, do={self.do.text()}, di={self.di.text()}", msg)
    dlg = LensDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))


def open_speed_calculator():
    class SpeedDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Speed Calculator")
            layout = QVBoxLayout(self)
            self.dist = QLineEdit()
            self.time = QLineEdit()
            row1 = QHBoxLayout()
            row1.addWidget(QLabel("Distance (m):"))
            row1.addWidget(self.dist)
            row2 = QHBoxLayout()
            row2.addWidget(QLabel("Time (s):"))
            row2.addWidget(self.time)
            layout.addLayout(row1)
            layout.addLayout(row2)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Calculate Speed")
            btn.clicked.connect(self.compute)
            layout.addWidget(btn)
            self.setMinimumWidth(300)
        def compute(self):
            try:
                dist = float(self.dist.text())
                time = float(self.time.text())
                if time == 0:
                    raise ValueError("Time cannot be zero")
                speed = dist / time
                self.result.setText(f"Speed = {speed:.3f} m/s")
                log_event("Speed Calculator", f"Distance={dist}, Time={time}", speed)
            except Exception as e:
                self.result.setText(f"Error: {e}")
    dlg = SpeedDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))


def open_drag_force_calculator():
    class DragDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Drag Force Calculator")
            layout = QVBoxLayout(self)
            self.density = QLineEdit()
            self.velocity = QLineEdit()
            self.cd = QLineEdit()
            self.area = QLineEdit()
            for label, edit in [
                ("Air Density ρ (kg/m³):", self.density),
                ("Velocity v (m/s):", self.velocity),
                ("Drag Coefficient Cd:", self.cd),
                ("Cross-sectional Area A (m²):", self.area)
            ]:
                row = QHBoxLayout()
                row.addWidget(QLabel(label))
                row.addWidget(edit)
                layout.addLayout(row)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Calculate Drag Force")
            btn.clicked.connect(self.compute)
            layout.addWidget(btn)
            self.setMinimumWidth(320)
        def compute(self):
            try:
                rho = float(self.density.text())
                v = float(self.velocity.text())
                cd = float(self.cd.text())
                A = float(self.area.text())
                Fd = 0.5 * rho * v**2 * cd * A
                self.result.setText(f"Drag Force = {Fd:.3f} N")
                log_event("Drag Force Calculator", f"ρ={rho}, v={v}, Cd={cd}, A={A}", Fd)
            except Exception as e:
                self.result.setText(f"Error: {e}")
    dlg = DragDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))


def open_acceleration_calculator():
    class AccelDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Acceleration Calculator")
            layout = QVBoxLayout(self)
            self.dv = QLineEdit()
            self.time = QLineEdit()
            row1 = QHBoxLayout()
            row1.addWidget(QLabel("Change in Velocity Δv (m/s):"))
            row1.addWidget(self.dv)
            row2 = QHBoxLayout()
            row2.addWidget(QLabel("Time (s):"))
            row2.addWidget(self.time)
            layout.addLayout(row1)
            layout.addLayout(row2)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Calculate")
            btn.clicked.connect(self.compute)
            layout.addWidget(btn)
            self.setMinimumWidth(320)
        def compute(self):
            try:
                dv = float(self.dv.text())
                t = float(self.time.text())
                if t == 0:
                    raise ValueError("Time cannot be zero")
                a = dv / t
                self.result.setText(f"Acceleration = {a:.3f} m/s²")
                log_event("Acceleration Calculator", f"Δv={dv}, t={t}", a)
            except Exception as e:
                self.result.setText(f"Error: {e}")
    dlg = AccelDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))


def open_force_calculator():
    class ForceDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Force Calculator")
            layout = QVBoxLayout(self)
            self.mass = QLineEdit()
            self.accel = QLineEdit()
            row1 = QHBoxLayout()
            row1.addWidget(QLabel("Mass (kg):"))
            row1.addWidget(self.mass)
            row2 = QHBoxLayout()
            row2.addWidget(QLabel("Acceleration (m/s²):"))
            row2.addWidget(self.accel)
            layout.addLayout(row1)
            layout.addLayout(row2)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Calculate")
            btn.clicked.connect(self.compute)
            layout.addWidget(btn)
            self.setMinimumWidth(300)
        def compute(self):
            try:
                m = float(self.mass.text())
                a = float(self.accel.text())
                F = m * a
                self.result.setText(f"Force = {F:.3f} N")
                log_event("Force Calculator", f"m={m}, a={a}", F)
            except Exception as e:
                self.result.setText(f"Error: {e}")
    dlg = ForceDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))


def open_kinetic_energy_calculator():
    class KEnergyDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Kinetic Energy Calculator")
            layout = QVBoxLayout(self)
            self.mass = QLineEdit()
            self.velocity = QLineEdit()
            row1 = QHBoxLayout()
            row1.addWidget(QLabel("Mass (kg):"))
            row1.addWidget(self.mass)
            row2 = QHBoxLayout()
            row2.addWidget(QLabel("Velocity (m/s):"))
            row2.addWidget(self.velocity)
            layout.addLayout(row1)
            layout.addLayout(row2)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Calculate")
            btn.clicked.connect(self.compute)
            layout.addWidget(btn)
            self.setMinimumWidth(300)
        def compute(self):
            try:
                m = float(self.mass.text())
                v = float(self.velocity.text())
                KE = 0.5 * m * v**2
                self.result.setText(f"Kinetic Energy = {KE:.3f} J")
                log_event("Kinetic Energy Calculator", f"m={m}, v={v}", KE)
            except Exception as e:
                self.result.setText(f"Error: {e}")
    dlg = KEnergyDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
