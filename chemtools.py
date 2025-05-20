import datetime
import os
import tkinter as tk
from data_utils import _open_dialogs
from data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data, ai_chatlogs_dir
)

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton
from data_utils import load_element_data, parse_formula

import re
import os
import json
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QHBoxLayout
from data_utils import _open_dialogs, log_event

class MolecularWeightCalculatorDialog(QDialog):
    def __init__(self, element_data):
        super().__init__()
        self.setWindowTitle("Molecular Weight Calculator")
        self.setMinimumWidth(400)
        self.element_data = element_data

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter molecular formula (e.g. H2O, C6H12O6, CuSO4·5H2O):"))
        self.formula_entry = QLineEdit()
        self.formula_entry.setPlaceholderText("Example: C6H12O6 or CuSO4·5H2O")
        layout.addWidget(self.formula_entry)

        btn_layout = QHBoxLayout()
        calc_btn = QPushButton("Calculate")
        clear_btn = QPushButton("Clear")
        btn_layout.addWidget(calc_btn)
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)

        calc_btn.clicked.connect(self.calculate)
        clear_btn.clicked.connect(self.clear)

    def clear(self):
        self.formula_entry.clear()
        self.result_box.clear()

    def calculate(self):
        formula = self.formula_entry.text().strip()
        if not formula:
            self.result_box.setText("Please enter a molecular formula.")
            return

        try:
            parts = formula.split('·')  # split on hydrate dot
            total_counts = {}
            for part in parts:
                m = re.match(r'^(\d+)(.*)$', part)
                if m:
                    multiplier = int(m.group(1))
                    subformula = m.group(2)
                    counts = self.parse_formula(subformula)
                    for el, cnt in counts.items():
                        total_counts[el] = total_counts.get(el, 0) + cnt * multiplier
                else:
                    counts = self.parse_formula(part)
                    for el, cnt in counts.items():
                        total_counts[el] = total_counts.get(el, 0) + cnt
        except Exception as e:
            self.result_box.setText(f"Error parsing formula: {e}")
            return

        total_mass = 0
        lines = []
        unknown_elements = []

        for el, count in sorted(total_counts.items()):
            data = self.element_data.get(el)
            if not data:
                unknown_elements.append(el)
                continue
            atomic_mass = data.get("AtomicMass") or data.get("atomic_mass")
            subtotal = atomic_mass * count
            total_mass += subtotal
            name = data.get("Element", "Unknown")
            lines.append(f"{el} ({name}) × {count} = {subtotal:.4f} g/mol")

        if unknown_elements:
            lines.append("\nUnknown elements: " + ", ".join(unknown_elements))

        lines.append(f"\nTotal Molecular Weight: {total_mass:.4f} g/mol")
        self.result_box.setText("\n".join(lines))
        log_event("Molecular Weight Calculator", f"Formula={formula}", f"{total_mass:.4f} g/mol")

    def parse_formula(self, formula):
        # Tokenize (elements, digits, parentheses)
        tokens = re.findall(r'([A-Z][a-z]?|\d+|\(|\))', formula)
        stack = [{}]
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == '(':
                stack.append({})
                i += 1
            elif token == ')':
                group = stack.pop()
                i += 1
                multiplier = 1
                if i < len(tokens) and tokens[i].isdigit():
                    multiplier = int(tokens[i])
                    i += 1
                for el, cnt in group.items():
                    stack[-1][el] = stack[-1].get(el, 0) + cnt * multiplier
            elif re.match(r'[A-Z][a-z]?', token):
                el = token
                cnt = 1
                i += 1
                if i < len(tokens) and tokens[i].isdigit():
                    cnt = int(tokens[i])
                    i += 1
                stack[-1][el] = stack[-1].get(el, 0) + cnt
            else:
                raise ValueError(f"Unexpected token: {token}")
        if len(stack) != 1:
            raise ValueError("Mismatched parentheses in formula")
        return stack.pop()

def open_mass_calculator():
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, 'databases', 'PeriodicTableJSON.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        element_data_raw = json.load(f)
    element_data = {el['symbol']: el for el in element_data_raw['elements']} if 'elements' in element_data_raw else element_data_raw

    dlg = MolecularWeightCalculatorDialog(element_data)
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
import os
import json
import re
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog
)
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression, Qt
from data_utils import log_event, _open_dialogs


def open_isotope_tool(preload=None):
    class IsotopeDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Isotopic Notation")
            self.setMinimumWidth(480)
            layout = QVBoxLayout(self)

            # Load element data
            base_dir = os.path.dirname(__file__)
            data_path = os.path.join(base_dir, 'databases', 'PeriodicTableJSON.json')
            with open(data_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            self.element_data = {el['symbol']: el for el in raw_data.get('elements', [])}

            # Element symbol input
            self.symbol_entry = QLineEdit()
            self.symbol_entry.setPlaceholderText("Element symbol (e.g., H, He, Fe)")
            self.symbol_entry.setMaxLength(2)
            symbol_regex = QRegularExpression("^[A-Za-z]{0,2}$")
            self.symbol_entry.setValidator(QRegularExpressionValidator(symbol_regex))
            layout.addWidget(QLabel("Element Symbol:"))
            layout.addWidget(self.symbol_entry)

            # Mass number input
            self.mass_entry = QLineEdit()
            self.mass_entry.setPlaceholderText("Mass number (integer)")
            mass_regex = QRegularExpression("^[0-9]*$")
            self.mass_entry.setValidator(QRegularExpressionValidator(mass_regex))
            layout.addWidget(QLabel("Mass Number (unitless):"))
            layout.addWidget(self.mass_entry)

            # Buttons
            btn_layout = QHBoxLayout()
            self.calc_btn = QPushButton("Calculate")
            self.copy_btn = QPushButton("Copy Result")
            self.export_btn = QPushButton("Export Chart")
            btn_layout.addWidget(self.calc_btn)
            btn_layout.addWidget(self.copy_btn)
            btn_layout.addWidget(self.export_btn)
            layout.addLayout(btn_layout)

            # Result display
            self.result_display = QTextEdit()
            self.result_display.setReadOnly(True)
            self.result_display.setMinimumHeight(150)
            layout.addWidget(self.result_display)

            # Matplotlib figure and canvas
            self.figure = plt.figure(figsize=(4, 3))
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)

            # Connect signals
            self.calc_btn.clicked.connect(self.calculate)
            self.copy_btn.clicked.connect(self.copy_result)
            self.export_btn.clicked.connect(self.export_chart)

            if preload and isinstance(preload, tuple) and len(preload) == 2:
                self.symbol_entry.setText(str(preload[0]))
                self.mass_entry.setText(str(preload[1]))
                log_event("Isotopic Notation (Preload)", f"{preload}", "Waiting for calculation")

            # To track last saved image path for adding to result
            self.last_img_path = None

        def calculate(self):
            symbol = self.symbol_entry.text().capitalize()
            mass_str = self.mass_entry.text()
            if not symbol or not mass_str:
                self.show_error("Please enter both element symbol and mass number.")
                return

            if symbol not in self.element_data:
                self.show_error(f"Element symbol '{symbol}' not found.")
                return

            try:
                mass_num = int(mass_str)
            except ValueError:
                self.show_error("Mass number must be a valid integer.")
                return

            element = self.element_data[symbol]
            Z = element.get("number") or element.get("AtomicNumber")
            if Z is None:
                self.show_error(f"Atomic number not found for element '{symbol}'.")
                return

            neutrons = mass_num - Z
            if neutrons < 0:
                self.show_error("Mass number cannot be less than atomic number (protons).")
                return

            # Find isotope info if available
            isotope_info = None
            isotopes = element.get("isotopes", [])
            for iso in isotopes:
                if iso.get("mass_number") == mass_num or iso.get("massNumber") == mass_num:
                    isotope_info = iso
                    break

            atomic_mass = isotope_info.get("atomic_mass") if isotope_info else element.get("atomic_mass") or element.get("AtomicMass")

            abundance = isotope_info.get("abundance") if isotope_info else None
            abundance_str = f"{abundance:.3%}" if abundance is not None else "Unknown"

            result_html = (
                f"<b>Isotopic Notation:</b> {mass_num}<sub>{symbol}</sub><br>"
                f"<b>Element:</b> {element.get('name', 'Unknown')} ({symbol})<br>"
                f"<b>Atomic Number (Protons):</b> {Z}<br>"
                f"<b>Neutrons:</b> {neutrons}<br>"
                f"<b>Atomic Mass:</b> {atomic_mass:.5f} u<br>"
                f"<b>Natural Abundance:</b> {abundance_str}<br>"
            )

            # Draw pie chart and save image
            self.draw_pie_chart(Z, neutrons)
            img_path = self.save_chart_image()
            self.last_img_path = img_path
            result_html += f'<br><i>Chart saved to:</i><br><small>{img_path}</small>'

            self.result_display.setHtml(result_html)
            log_event("Isotopic Notation", f"{symbol}, mass={mass_num}", result_html)

        def draw_pie_chart(self, protons, neutrons):
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            labels = ['Protons', 'Neutrons']
            sizes = [protons, neutrons]
            colors = ['#1f77b4', '#ff7f0e']
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            ax.axis('equal')
            ax.set_title('Nucleon Composition')
            self.canvas.draw()

        def save_chart_image(self):
            results_dir = os.path.join(os.path.dirname(__file__), 'results')
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            img_path = os.path.join(results_dir, f"isotope_chart_{timestamp}.png")
            self.figure.savefig(img_path, dpi=150)
            return img_path

        def copy_result(self):
            clipboard = self.clipboard()
            clipboard.setText(self.result_display.toPlainText())

        def export_chart(self):
            fname, _ = QFileDialog.getSaveFileName(self, "Save Chart Image", "", "PNG Files (*.png);;All Files (*)")
            if fname:
                try:
                    self.figure.savefig(fname, dpi=150)
                except Exception as e:
                    self.show_error(f"Failed to save image: {e}")

        def show_error(self, message):
            self.result_display.setHtml(f'<span style="color: red;">{message}</span>')
            log_event("Isotopic Notation", "Error", message)

    dlg = IsotopeDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))


import math
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from data_utils import load_element_data, log_event
import matplotlib.pyplot as plt
import os
import datetime
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt
from data_utils import load_element_data, log_event, _open_dialogs

results_dir = os.path.join(os.path.dirname(__file__), 'results')

def open_shell_visualizer(preload=None):
    class ShellDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Shell Visualizer")
            self.data = load_element_data()
            self.setMinimumWidth(450)
            self.resize(600, 650)

            layout = QVBoxLayout(self)

            layout.addWidget(QLabel("Element Symbol:"))
            self.entry = QLineEdit()
            self.entry.setPlaceholderText("Example: H, He, Fe")
            layout.addWidget(self.entry)

            btn_layout = QHBoxLayout()
            self.draw_btn = QPushButton("Draw & Save")
            btn_layout.addWidget(self.draw_btn)
            layout.addLayout(btn_layout)

            self.status_label = QLabel("")
            layout.addWidget(self.status_label)

            self.figure = plt.figure(figsize=(5, 5), dpi=100)
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.canvas.updateGeometry()
            # Debug border: uncomment to see canvas boundaries
            # self.canvas.setStyleSheet("border: 2px solid red;")
            layout.addWidget(self.canvas)

            self.toolbar = NavigationToolbar(self.canvas, self)
            layout.addWidget(self.toolbar)

            self.draw_btn.clicked.connect(self.draw)

            if preload:
                self.entry.setText(preload)
                log_event("Shell Visualizer (Chain)", preload, "Waiting for draw")

        def draw(self):
            sym = self.entry.text().strip().capitalize()
            if sym not in self.data or "shells" not in self.data[sym]:
                QMessageBox.warning(self, "Not found", f"No shell data for element '{sym}'")
                return

            shells = self.data[sym]["shells"]
            max_shells = len(shells)
            max_electrons = max(shells) if shells else 1

            base_radius = 0.6

            def radius_func(i):
                return base_radius + np.sqrt(i + 1) * 0.7

            radii = np.array([radius_func(i) for i in range(max_shells)])
            max_radius = radii[-1] if len(radii) > 0 else base_radius

            max_allowed_radius = 8
            scale = 1.0
            if max_radius > max_allowed_radius:
                scale = max_allowed_radius / max_radius
                radii = radii * scale
                max_radius = max_allowed_radius

            fig_size = 5 + max_radius * 0.8
            self.figure.set_size_inches(fig_size, fig_size)
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            cx, cy = 0, 0
            colors = ["#b0c4de", "#add8e6", "#90ee90", "#ffa07a", "#ffd700", "#e9967a", "#dda0dd"]

            for i, count in enumerate(shells):
                r = radii[i]
                circ = plt.Circle((cx, cy), r, fill=False, color=colors[i % len(colors)], linewidth=2)
                ax.add_patch(circ)

                for j in range(count):
                    angle = 2 * math.pi * j / count
                    ex = cx + r * math.cos(angle)
                    ey = cy + r * math.sin(angle)
                    electron = plt.Circle((ex, ey), 0.06 * scale, color="black")
                    ax.add_patch(electron)

            ax.text(cx, cy, sym, fontsize=16 * scale, fontweight="bold", ha='center', va='center')

            padding = max_radius * 0.6 + 1.0  # Increased padding
            ax.set_xlim(-max_radius - padding, max_radius + padding)
            ax.set_ylim(-max_radius - padding, max_radius + padding)

            ax.set_aspect('equal', adjustable='box')  # Aspect set last
            ax.axis('off')

            self.canvas.draw()
            self.canvas.resize(self.canvas.sizeHint())  # Force canvas resize

            if not os.path.exists(results_dir):
                os.makedirs(results_dir)

            fname = f"shells_{sym}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
            full_path = os.path.join(results_dir, fname)
            self.figure.savefig(full_path)

            self.status_label.setText(f"Shell visualization saved as: {full_path}")
            log_event("Shell Visualizer", sym, f"Shells: {shells} [IMG:{full_path}]")

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
