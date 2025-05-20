import datetime
import os
import tkinter as tk
from tools.data_utils import _open_dialogs
from tools.data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data, ai_chatlogs_dir
)

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton
from tools.data_utils import load_element_data, parse_formula

class MassCalculatorDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Molecular Weight Calculator")
        self.setMinimumWidth(360)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Enter Formula:"))
        self.formula_entry = QLineEdit()
        layout.addWidget(self.formula_entry)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)

        calc_btn = QPushButton("Calculate")
        calc_btn.clicked.connect(self.calculate)
        layout.addWidget(calc_btn)

    def calculate(self):
        data = load_element_data()
        formula = self.formula_entry.text().strip()
        try:
            counts = parse_formula(formula)
            total = 0
            result_lines = []
            for el, count in counts.items():
                el_data = data.get(el)
                if el_data:
                    mass = el_data.get("AtomicMass") or el_data.get("atomic_mass")
                else:
                    self.result_box.append(f"{el}: unknown")
                    continue
                subtotal = count * mass
                result_lines.append(f"{el} × {count} = {subtotal:.3f} g/mol")
                total += subtotal
            result_lines.append(f"\nTotal = {total:.3f} g/mol")
            self.result_box.setText('\n'.join(result_lines))
        except Exception as e:
            self.result_box.setText(f"Error: {e}")

def open_mass_calculator():
    dlg = MassCalculatorDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))


from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
)
from tools.data_utils import load_element_data, log_event

def open_isotope_tool(preload=None):
    class IsotopeDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Isotopic Notation")
            self.data = load_element_data()
            self.setMinimumWidth(350)
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Element Symbol:"))
            self.symbol_entry = QLineEdit()
            layout.addWidget(self.symbol_entry)

            layout.addWidget(QLabel("Mass Number:"))
            self.mass_entry = QLineEdit()
            layout.addWidget(self.mass_entry)

            if preload and isinstance(preload, tuple) and len(preload) == 2:
                self.symbol_entry.setText(str(preload[0]))
                self.mass_entry.setText(str(preload[1]))
                log_event("Isotopic Notation (Chain)", f"{preload}", "Waiting for confirmation")

            self.result = QLabel("")
            layout.addWidget(self.result)

            btn = QPushButton("Calculate")
            btn.clicked.connect(self.calculate)
            layout.addWidget(btn)

        def calculate(self):
            sym = self.symbol_entry.text().strip()
            try:
                mass = int(self.mass_entry.text())
                if sym in self.data:
                    Z = self.data[sym].get("AtomicNumber") or self.data[sym].get("number")
                else:
                    raise ValueError
                neutrons = mass - Z
                output = f"Notation: <b>{mass}{sym}</b><br>Protons: <b>{Z}</b><br>Neutrons: <b>{neutrons}</b>"
                self.result.setText(output)
                log_event("Isotopic Notation", f"{sym}, mass={mass}", output)
            except Exception as e:
                error_msg = "Invalid input or element not found."
                self.result.setText(error_msg)
                log_event("Isotopic Notation", f"{sym}, mass={self.mass_entry.text()}", error_msg)

    dlg = IsotopeDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

import math
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from tools.data_utils import load_element_data, log_event
import matplotlib.pyplot as plt

def open_shell_visualizer(preload=None):
    class ShellDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Shell Visualizer")
            self.data = load_element_data()
            self.setMinimumWidth(320)
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Element Symbol:"))
            self.entry = QLineEdit()
            layout.addWidget(self.entry)

            btn = QPushButton("Draw & Save")
            btn.clicked.connect(self.draw)
            layout.addWidget(btn)

            if preload:
                self.entry.setText(preload)
                log_event("Shell Visualizer (Chain)", preload, "Waiting for draw")

        def draw(self):
            sym = self.entry.text().strip()
            if sym not in self.data or "shells" not in self.data[sym]:
                QMessageBox.warning(self, "Not found", f"No shell data for element '{sym}'")
                return
            shells = self.data[sym]["shells"]
            fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
            cx, cy = 0, 0
            colors = ["#b0c4de", "#add8e6", "#90ee90", "#ffa07a", "#ffd700", "#e9967a", "#dda0dd"]
            for i, count in enumerate(shells):
                r = 0.6 + i * 0.7
                circ = plt.Circle((cx, cy), r, fill=False, color=colors[i % len(colors)], linewidth=2)
                ax.add_patch(circ)
                for j in range(count):
                    angle = 2 * math.pi * j / count
                    ex = cx + r * math.cos(angle)
                    ey = cy + r * math.sin(angle)
                    electron = plt.Circle((ex, ey), 0.06, color="black")
                    ax.add_patch(electron)
            ax.text(cx, cy, sym, fontsize=16, fontweight="bold", ha='center', va='center')
            ax.set_xlim(-2.5, 2.5)
            ax.set_ylim(-2.5, 2.5)
            ax.axis('off')
            plt.tight_layout()

            # Save to results folder
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)

            fname = f"shells_{sym}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
            full_path = os.path.join(results_dir, fname)
            plt.savefig(full_path)
            plt.show()
            log_event("Shell Visualizer", sym, f"Shells: {shells} [IMG:{full_path}]")
            QMessageBox.information(self, "Saved", f"Shell visualization saved as:\n{full_path}")

    dlg = ShellDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)

def open_phase_predictor(preload=None):
    class PhaseDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Phase Predictor")
            self.data = load_element_data()
            self.setMinimumWidth(360)
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Element Symbol:"))
            self.sym_entry = QLineEdit()
            layout.addWidget(self.sym_entry)

            layout.addWidget(QLabel("Temperature (°C):"))
            self.temp_entry = QLineEdit()
            self.temp_entry.setText("25")
            layout.addWidget(self.temp_entry)

            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Check Phase")
            btn.clicked.connect(self.predict)
            layout.addWidget(btn)

            if preload:
                self.sym_entry.setText(preload)
                log_event("Phase Predictor (Chain)", preload, "Waiting for check")

        def predict(self):
            sym = self.sym_entry.text().strip()
            try:
                temp_c = float(self.temp_entry.text())
            except Exception:
                self.result.setText("Enter a valid temperature.")
                return
            try:
                el = self.data[sym]
                melt = el.get("MeltingPoint") or el.get("melt")
                boil = el.get("BoilingPoint") or el.get("boil")
                if melt is None or boil is None:
                    msg = "No data available."
                    self.result.setText(msg)
                    log_event("Phase Predictor", sym, msg)
                    return
                temp_k = temp_c + 273.15
                msg = f"Melting point: {melt} K<br>Boiling point: {boil} K<br>"
                if temp_k < melt:
                    phase = "solid"
                elif melt <= temp_k < boil:
                    phase = "liquid"
                else:
                    phase = "gas"
                msg += f"<b>Predicted phase at {temp_c:.1f}°C: {phase}</b>"
                self.result.setText(msg)
                log_event("Phase Predictor", f"{sym}, {temp_c}°C", msg)
            except Exception:
                msg = "Invalid input or element not found."
                self.result.setText(msg)
                log_event("Phase Predictor", sym, msg)

    dlg = PhaseDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QCheckBox, QMessageBox, QAbstractItemView
)
from PyQt6.QtGui import QBrush, QColor, QFont

def open_comparator(preload=None):
    class ComparatorDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Element Comparator")
            self.data = load_element_data()
            self.setMinimumWidth(470)
            vbox = QVBoxLayout(self)

            elements = sorted(self.data.keys())
            row = QHBoxLayout()
            row.addWidget(QLabel("Element A:"))
            self.a_box = QComboBox()
            self.a_box.addItems(elements)
            row.addWidget(self.a_box)
            row.addWidget(QLabel("Element B:"))
            self.b_box = QComboBox()
            self.b_box.addItems(elements)
            row.addWidget(self.b_box)
            vbox.addLayout(row)

            # Pick properties
            props = [
                ("Atomic Number", "AtomicNumber"),
                ("Atomic Mass", "AtomicMass"),
                ("Electronegativity", "Electronegativity"),
                ("Boiling Point", "BoilingPoint"),
                ("Melting Point", "MeltingPoint"),
                ("Type", "Type")
            ]
            self.props = []
            row2 = QHBoxLayout()
            for label, key in props:
                chk = QCheckBox(label)
                chk.setChecked(True)
                chk.key = key
                self.props.append(chk)
                row2.addWidget(chk)
            vbox.addLayout(row2)

            self.compare_btn = QPushButton("Compare")
            vbox.addWidget(self.compare_btn)

            self.table = QTableWidget()
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["Property", "A", "B"])
            self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            vbox.addWidget(self.table)

            self.compare_btn.clicked.connect(self.compare)

            if preload and isinstance(preload, tuple) and len(preload) == 2:
                self.a_box.setCurrentText(preload[0])
                self.b_box.setCurrentText(preload[1])
                log_event("Comparator (Chain)", f"{preload}", "Waiting for compare")

        def compare(self):
            a = self.a_box.currentText()
            b = self.b_box.currentText()
            if a not in self.data or b not in self.data:
                QMessageBox.warning(self, "Invalid", "Invalid element selection.")
                log_event("Element Comparator", f"{a} vs {b}", "Invalid element selection.")
                return
            keys = [chk.key for chk in self.props if chk.isChecked()]
            self.table.setRowCount(len(keys))
            log_lines = []
            for i, key in enumerate(keys):
                prop_label = [chk.text() for chk in self.props if chk.key == key][0]
                a_val = self.data[a].get(key)
                b_val = self.data[b].get(key)
                # Pretty formatting
                def fmt(x): return "—" if x is None else f"{x}"
                item_prop = QTableWidgetItem(prop_label)
                item_a = QTableWidgetItem(fmt(a_val))
                item_b = QTableWidgetItem(fmt(b_val))
                # Highlight largest value (if numeric)
                try:
                    va = float(a_val)
                    vb = float(b_val)
                    if va > vb:
                        item_a.setFont(QFont("", weight=QFont.Weight.Bold))
                        item_a.setForeground(QBrush(QColor("blue")))
                    elif vb > va:
                        item_b.setFont(QFont("", weight=QFont.Weight.Bold))
                        item_b.setForeground(QBrush(QColor("blue")))
                except:
                    # For non-numeric: bold if not equal
                    if a_val != b_val and None not in (a_val, b_val):
                        item_a.setFont(QFont("", italic=True))
                        item_b.setFont(QFont("", italic=True))
                self.table.setItem(i, 0, item_prop)
                self.table.setItem(i, 1, item_a)
                self.table.setItem(i, 2, item_b)
                log_lines.append(f"{prop_label}: {a}={a_val}, {b}={b_val}")
            summary = f"Compared {a} and {b}"
            log_event("Element Comparator", f"{a} vs {b}", summary + " | " + " | ".join(log_lines))

    dlg = ComparatorDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
)

def open_unit_multiplier(preload=None):
    class UnitMultDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Mole-Mass-Volume Calculator")
            self.setMinimumWidth(350)
            layout = QVBoxLayout(self)

            self.field_choice = QComboBox()
            self.field_choice.addItems([
                "Calculate Mass (g) from Moles and Molar Mass",
                "Calculate Volume (L at STP) from Moles",
                "Calculate Moles from Mass and Molar Mass",
                "Calculate Moles from Volume at STP"
            ])
            layout.addWidget(QLabel("Mode:"))
            layout.addWidget(self.field_choice)

            self.mol_entry = QLineEdit()
            self.mass_entry = QLineEdit()
            self.mm_entry = QLineEdit()
            self.vol_entry = QLineEdit()

            layout.addWidget(QLabel("Moles:"))
            layout.addWidget(self.mol_entry)
            layout.addWidget(QLabel("Mass (g):"))
            layout.addWidget(self.mass_entry)
            layout.addWidget(QLabel("Molar Mass (g/mol):"))
            layout.addWidget(self.mm_entry)
            layout.addWidget(QLabel("Volume (L at STP):"))
            layout.addWidget(self.vol_entry)

            if preload and isinstance(preload, tuple):
                # Try to preload in order: moles, mm, mass, vol
                if len(preload) > 0:
                    self.mol_entry.setText(str(preload[0]))
                if len(preload) > 1:
                    self.mm_entry.setText(str(preload[1]))
                log_event("Mole-Mass Calculator (Chain)", f"{preload}", "Waiting for calculation")

            self.result = QLabel("")
            layout.addWidget(self.result)

            btn = QPushButton("Calculate")
            btn.clicked.connect(self.calculate)
            layout.addWidget(btn)

            self.field_choice.currentIndexChanged.connect(self.update_fields)
            self.update_fields()

        def update_fields(self):
            mode = self.field_choice.currentIndex()
            self.mol_entry.setReadOnly(False)
            self.mm_entry.setReadOnly(False)
            self.mass_entry.setReadOnly(False)
            self.vol_entry.setReadOnly(False)
            if mode == 0:  # Calculate Mass
                self.mass_entry.setReadOnly(True)
            elif mode == 1:  # Calculate Volume
                self.vol_entry.setReadOnly(True)
            elif mode == 2:  # Calculate Moles (from mass)
                self.mol_entry.setReadOnly(True)
            elif mode == 3:  # Calculate Moles (from volume)
                self.mol_entry.setReadOnly(True)

        def calculate(self):
            mode = self.field_choice.currentIndex()
            try:
                if mode == 0:  # Calculate Mass
                    mol = float(self.mol_entry.text())
                    mm = float(self.mm_entry.text())
                    mass = mol * mm
                    volume = mol * 22.4
                    output = f"Mass: {mass:.4f} g\nVolume (STP): {volume:.4f} L"
                    self.result.setText(output)
                    log_event("Mole-Mass Calculator", f"mol={mol}, mm={mm}", output.replace('\n', ' | '))
                elif mode == 1:  # Calculate Volume at STP
                    mol = float(self.mol_entry.text())
                    volume = mol * 22.4
                    output = f"Volume (STP): {volume:.4f} L"
                    self.result.setText(output)
                    log_event("Mole-Volume Calculator", f"mol={mol}", output)
                elif mode == 2:  # Calculate Moles (from mass and mm)
                    mass = float(self.mass_entry.text())
                    mm = float(self.mm_entry.text())
                    mol = mass / mm
                    output = f"Moles: {mol:.4f} mol"
                    self.result.setText(output)
                    log_event("Mass-Mole Calculator", f"mass={mass}, mm={mm}", output)
                elif mode == 3:  # Calculate Moles (from volume)
                    vol = float(self.vol_entry.text())
                    mol = vol / 22.4
                    output = f"Moles: {mol:.4f} mol"
                    self.result.setText(output)
                    log_event("Volume-Mole Calculator", f"vol={vol}", output)
            except Exception:
                self.result.setText("Invalid input.")
                log_event("Mole-Mass Calculator", f"mode={mode}", "Invalid input.")

    dlg = UnitMultDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QCheckBox
)
import matplotlib.pyplot as plt
import json

def open_property_grapher(preload=None):
    class GrapherDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Element Property Grapher")
            self.setMinimumWidth(440)
            layout = QVBoxLayout(self)

            self.data = load_element_data()
            # Gather all possible property keys
            any_el = next(iter(self.data.values()))
            self.all_props = sorted(k for k in any_el.keys() if k.lower() != "symbol" and not isinstance(any_el[k], list))
            # Favorite element symbols
            try:
                with open(element_favs_path, "r") as f:
                    self.favs = set(json.load(f))
            except:
                self.favs = set()

            layout.addWidget(QLabel("Property to Graph:"))
            prop_box = QHBoxLayout()
            self.prop_dd = QComboBox()
            self.prop_dd.addItems(self.all_props)
            self.prop_dd.setEditable(True)
            if preload:
                self.prop_dd.setCurrentText(str(preload))
                log_event("Property Grapher (Chain)", preload, "Waiting for plot")
            else:
                self.prop_dd.setCurrentText("Electronegativity")
            prop_box.addWidget(self.prop_dd)

            self.logscale_cb = QCheckBox("Logarithmic Y scale")
            prop_box.addWidget(self.logscale_cb)
            layout.addLayout(prop_box)

            btn = QPushButton("Plot")
            btn.clicked.connect(self.plot)
            layout.addWidget(btn)

            self.setLayout(layout)

        def plot(self):
            prop = self.prop_dd.currentText()
            symbols, xs, ys, names = [], [], [], []
            for el in self.data.values():
                x = el.get("AtomicNumber") or el.get("number")
                y = el.get(prop)
                if x is not None and y is not None:
                    xs.append(x)
                    ys.append(y)
                    symbols.append(el["symbol"])
                    names.append(el.get("name", ""))

            if not xs or not ys:
                log_event("Property Grapher", prop, "No data points available")
                return

            points = sorted(zip(xs, ys, symbols, names), key=lambda p: p[0])
            xs_sorted, ys_sorted, symbols_sorted, names_sorted = zip(*points)

            fig, ax = plt.subplots(figsize=(10, 5))
            # Favorite points: gold, rest: blue
            colors = ['#FFD700' if s in self.favs else '#1f77b4' for s in symbols_sorted]
            sc = ax.scatter(xs_sorted, ys_sorted, color=colors, s=60, zorder=3, picker=True)

            # Add symbol as text
            for i, symbol in enumerate(symbols_sorted):
                ax.text(xs_sorted[i], ys_sorted[i], symbol, fontsize=8, ha='center', zorder=5)

            ax.set_xlabel("Atomic Number")
            ax.set_ylabel(prop)
            ax.set_title(f"{prop} vs Atomic Number")
            ax.grid(True)
            if self.logscale_cb.isChecked():
                ax.set_yscale("log")
            fig.tight_layout()

            # Save to results folder
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
            filename = f"{prop}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
            fig.savefig(filename)

            # Interactive hover
            annot = ax.annotate(
                "",
                xy=(0,0), xytext=(15,15), textcoords="offset points",
                bbox=dict(boxstyle="round", fc="w"),
                arrowprops=dict(arrowstyle="->"),
            )
            annot.set_visible(False)

            def update_annot(ind):
                idx = ind["ind"][0]
                annot.xy = (xs_sorted[idx], ys_sorted[idx])
                text = (f"{names_sorted[idx]} ({symbols_sorted[idx]})\n"
                        f"Z = {xs_sorted[idx]}\n{prop} = {ys_sorted[idx]}")
                annot.set_text(text)
                annot.get_bbox_patch().set_facecolor('#FFFFE0')
                annot.get_bbox_patch().set_alpha(0.9)

            def hover(event):
                vis = annot.get_visible()
                if event.inaxes == ax:
                    cont, ind = sc.contains(event)
                    if cont:
                        update_annot(ind)
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                    elif vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

            fig.canvas.mpl_connect("motion_notify_event", hover)

            plt.show()
            full_path = os.path.join(results_dir, filename)
            fig.savefig(full_path)

            summary = f"Plotted {len(xs_sorted)} elements ({symbols_sorted[0]} to {symbols_sorted[-1]})"
            log_event("Property Grapher", prop, f"{summary} [IMG:{full_path}]")


    dlg = GrapherDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
