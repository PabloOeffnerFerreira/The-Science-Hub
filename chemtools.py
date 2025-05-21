import datetime
from collections import defaultdict
import os
from data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data, ai_chatlogs_dir, log_event
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import json
import re
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QSizePolicy, QListWidget, QListWidgetItem
)
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression, Qt
from data_utils import load_element_data, parse_formula, _open_dialogs
from sympy import Matrix, lcm
import math
import numpy as np
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
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
import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
)
from data_utils import load_element_data, log_event, _open_dialogs

def parse_temperature(text):
    text = text.strip().lower()
    m = re.match(r'^([-+]?\d*\.?\d+)\s*([cfk]?)$', text)
    if not m:
        raise ValueError("Invalid temperature format")
    value, unit = m.groups()
    value = float(value)
    unit = unit if unit else 'c'
    return value, unit

def to_kelvin(value, unit):
    if unit == 'c':
        return value + 273.15
    elif unit == 'f':
        return (value - 32) * 5/9 + 273.15
    elif unit == 'k':
        return value
    else:
        raise ValueError("Unknown temperature unit")

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

            layout.addWidget(QLabel("Temperature (°C, °F, or K, e.g. 25, 77F, 300K):"))
            self.temp_entry = QLineEdit()
            self.temp_entry.setText("25")
            layout.addWidget(self.temp_entry)

            layout.addWidget(QLabel("Pressure (atm, optional):"))
            self.pressure_entry = QLineEdit()
            self.pressure_entry.setPlaceholderText("Default: 1 atm")
            layout.addWidget(self.pressure_entry)

            self.result = QLabel("")
            self.result.setWordWrap(True)
            layout.addWidget(self.result)

            btn = QPushButton("Check Phase")
            btn.clicked.connect(self.predict)
            layout.addWidget(btn)

            if preload:
                self.sym_entry.setText(preload)
                log_event("Phase Predictor (Chain)", preload, "Waiting for check")

        def predict(self):
            sym = self.sym_entry.text().strip().capitalize()
            temp_text = self.temp_entry.text()
            pressure_text = self.pressure_entry.text().strip()
            try:
                temp_val, temp_unit = parse_temperature(temp_text)
                temp_k = to_kelvin(temp_val, temp_unit)
            except Exception as e:
                self.result.setText(f"<span style='color:red'>Enter a valid temperature. ({e})</span>")
                return

            try:
                pressure = float(pressure_text) if pressure_text else 1.0
            except Exception:
                self.result.setText("<span style='color:red'>Invalid pressure input. Defaulting to 1 atm.</span>")
                pressure = 1.0

            if sym not in self.data:
                self.result.setText(f"<span style='color:red'>Element symbol '{sym}' not found.</span>")
                return

            el = self.data[sym]
            melt = el.get("MeltingPoint") or el.get("melt")
            boil = el.get("BoilingPoint") or el.get("boil")

            if melt is None or boil is None:
                msg = "No melting or boiling point data available."
                self.result.setText(msg)
                log_event("Phase Predictor", sym, msg)
                return

            # Here pressure is not yet used for phase determination

            phase_colors = {'solid': 'blue', 'liquid': 'orange', 'gas': 'red'}

            msg = f"Melting point: {melt:.2f} K<br>Boiling point: {boil:.2f} K<br>"
            if temp_k < melt:
                phase = "solid"
            elif melt <= temp_k < boil:
                phase = "liquid"
            else:
                phase = "gas"

            msg += f"<b>Predicted phase at {temp_val:.1f}°{temp_unit.upper()} and {pressure} atm: " \
                   f"<span style='color:{phase_colors[phase]};'>{phase.capitalize()}</span></b>"

            self.result.setText(msg)
            log_event("Phase Predictor", f"{sym}, {temp_val} {temp_unit.upper()}, {pressure} atm", msg)

    dlg = PhaseDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
import os
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QCheckBox, QLineEdit, QMessageBox,
    QAbstractItemView, QTabWidget, QWidget, QHeaderView
)
from PyQt6.QtGui import QBrush, QColor, QFont
from PyQt6.QtCore import Qt
from data_utils import load_element_data, log_event, _open_dialogs

PROPERTY_METADATA = {
    "AtomicNumber": {
        "label": "Atomic Number",
        "unit": "",
        "category": "Atomic",
        "desc": "Number of protons in the nucleus",
        "numeric": True
    },
    "AtomicMass": {
        "label": "Atomic Mass",
        "unit": "u",
        "category": "Atomic",
        "desc": "Average atomic mass (unified atomic mass units)",
        "numeric": True
    },
    "Electronegativity": {
        "label": "Electronegativity",
        "unit": "",
        "category": "Chemical",
        "desc": "Pauling scale electronegativity",
        "numeric": True
    },
    "BoilingPoint": {
        "label": "Boiling Point",
        "unit": "K",
        "category": "Physical",
        "desc": "Boiling point temperature in Kelvin",
        "numeric": True
    },
    "MeltingPoint": {
        "label": "Melting Point",
        "unit": "K",
        "category": "Physical",
        "desc": "Melting point temperature in Kelvin",
        "numeric": True
    },
    "Density": {
        "label": "Density",
        "unit": "g/cm³",
        "category": "Physical",
        "desc": "Density near room temperature",
        "numeric": True
    },
    "Type": {
        "label": "Type",
        "unit": "",
        "category": "Chemical",
        "desc": "Element category/type (metal, nonmetal, etc.)",
        "numeric": False
    },
    "OxidationStates": {
        "label": "Oxidation States",
        "unit": "",
        "category": "Chemical",
        "desc": "Common oxidation states",
        "numeric": False
    },
}

CATEGORIES = sorted(set(prop["category"] for prop in PROPERTY_METADATA.values()))

class ElementComparatorDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Element Comparator")
        self.data = load_element_data()
        self.setMinimumWidth(700)
        self.resize(900, 600)

        main_layout = QVBoxLayout(self)

        element_layout = QHBoxLayout()
        element_layout.addWidget(QLabel("Select Elements:"))

        self.element_boxes = []
        for i in range(3):
            box = QComboBox()
            box.setEditable(True)
            box.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
            box.addItems(sorted(self.data.keys()))
            box.setCurrentIndex(i)
            box.setFixedWidth(150)
            self.element_boxes.append(box)
            element_layout.addWidget(box)

        main_layout.addLayout(element_layout)

        self.tabs = QTabWidget()
        self.prop_checkboxes = {}
        for category in CATEGORIES:
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            select_layout = QHBoxLayout()
            select_all_btn = QPushButton("Select All")
            select_none_btn = QPushButton("Select None")
            select_layout.addWidget(select_all_btn)
            select_layout.addWidget(select_none_btn)
            tab_layout.addLayout(select_layout)

            checkboxes = []
            for key, meta in PROPERTY_METADATA.items():
                if meta["category"] == category:
                    chk = QCheckBox(meta["label"])
                    chk.key = key
                    chk.setChecked(True)
                    chk.setToolTip(meta["desc"])
                    checkboxes.append(chk)
                    tab_layout.addWidget(chk)
            self.prop_checkboxes[category] = checkboxes

            select_all_btn.clicked.connect(lambda _, c=category: self.set_all_props(c, True))
            select_none_btn.clicked.connect(lambda _, c=category: self.set_all_props(c, False))

            self.tabs.addTab(tab, category)

        main_layout.addWidget(self.tabs)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter properties:"))
        self.filter_input = QLineEdit()
        filter_layout.addWidget(self.filter_input)
        main_layout.addLayout(filter_layout)

        self.filter_input.textChanged.connect(self.filter_properties)

        self.compare_btn = QPushButton("Compare")
        main_layout.addWidget(self.compare_btn)

        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSortingEnabled(True)
        main_layout.addWidget(self.table)

        export_layout = QHBoxLayout()
        self.export_csv_btn = QPushButton("Export CSV")
        self.copy_clipboard_btn = QPushButton("Copy to Clipboard")
        export_layout.addWidget(self.export_csv_btn)
        export_layout.addWidget(self.copy_clipboard_btn)
        main_layout.addLayout(export_layout)

        self.compare_btn.clicked.connect(self.compare)
        self.export_csv_btn.clicked.connect(self.export_csv)
        self.copy_clipboard_btn.clicked.connect(self.copy_clipboard)

    def set_all_props(self, category, checked):
        for chk in self.prop_checkboxes[category]:
            chk.setChecked(checked)

    def filter_properties(self, text):
        text = text.lower()
        for category, chks in self.prop_checkboxes.items():
            for chk in chks:
                chk.setVisible(text in chk.text().lower() or text in chk.toolTip().lower())

    def format_value(self, key, val):
        if val is None:
            return "—"
        meta = PROPERTY_METADATA.get(key, {})
        unit = meta.get("unit", "")
        if isinstance(val, (int, float)):
            return f"{val:,.3f} {unit}".strip()
        if isinstance(val, list):
            return ", ".join(str(x) for x in val)
        return str(val)

    def compare(self):
        elements = [box.currentText().strip() for box in self.element_boxes]
        if len(set(elements)) != len(elements):
            QMessageBox.warning(self, "Invalid Selection", "Please select different elements.")
            return
        for el in elements:
            if el not in self.data:
                QMessageBox.warning(self, "Invalid Element", f"Element '{el}' not found in database.")
                return
        keys = []
        for chks in self.prop_checkboxes.values():
            keys.extend(chk.key for chk in chks if chk.isChecked())

        self.table.clear()
        self.table.setRowCount(len(keys))
        self.table.setColumnCount(len(elements) + 1)
        headers = ["Property"] + elements
        self.table.setHorizontalHeaderLabels(headers)

        for i, key in enumerate(keys):
            meta = PROPERTY_METADATA.get(key, {})
            prop_label = meta.get("label", key)
            item_prop = QTableWidgetItem(prop_label)
            item_prop.setToolTip(meta.get("desc", ""))
            self.table.setItem(i, 0, item_prop)

            vals = []
            for col, el in enumerate(elements, start=1):
                val = self.data[el].get(key)
                fmt_val = self.format_value(key, val)
                item = QTableWidgetItem(fmt_val)
                self.table.setItem(i, col, item)
                vals.append(val)

            # Fixed highlight logic:
            numeric_vals = [v for v in vals if isinstance(v, (int, float))]
            if numeric_vals:
                max_val = max(numeric_vals)
                min_val = min(numeric_vals)
                for col, v in enumerate(vals, start=1):
                    if v is None or not isinstance(v, (int, float)):
                        continue
                    item = self.table.item(i, col)
                    font = item.font()
                    if v == max_val:
                        font.setBold(True)
                        item.setForeground(QBrush(QColor("blue")))
                    elif v == min_val:
                        font.setItalic(True)
                        item.setForeground(QBrush(QColor("red")))
                    item.setFont(font)
            else:
                non_null_vals = [v for v in vals if v is not None]
                if len(set(non_null_vals)) > 1:
                    for col, v in enumerate(vals, start=1):
                        if v is None:
                            continue
                        item = self.table.item(i, col)
                        font = item.font()
                        font.setItalic(True)
                        item.setFont(font)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

        summary = f"Compared elements: {', '.join(elements)} on properties: {', '.join([PROPERTY_METADATA[k]['label'] for k in keys])}"
        log_event("Element Comparator", f"{elements}", summary)

    def export_csv(self):
        import csv
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV files (*.csv)")
        if not path:
            return
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
            writer.writerow(headers)
            for row in range(self.table.rowCount()):
                rowdata = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    rowdata.append(item.text() if item else "")
                writer.writerow(rowdata)

    def copy_clipboard(self):
        from PyQt6.QtGui import QGuiApplication
        data = []
        headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
        data.append('\t'.join(headers))
        for row in range(self.table.rowCount()):
            rowdata = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                rowdata.append(item.text() if item else "")
            data.append('\t'.join(rowdata))
        clipboard = QGuiApplication.clipboard()
        clipboard.setText('\n'.join(data))

def open_comparator(preload=None):
    dlg = ElementComparatorDialog()
    if preload and isinstance(preload, (list, tuple)):
        for i, val in enumerate(preload[:3]):
            dlg.element_boxes[i].setCurrentText(val)
        log_event("Comparator (Chain)", f"{preload}", "Waiting for compare")
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

def parse_formula(formula):
    tokens = re.findall(r'([A-Z][a-z]?|\(|\)|\d+)', formula)
    stack = [defaultdict(int)]
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == '(':
            stack.append(defaultdict(int))
            i += 1
        elif token == ')':
            group = stack.pop()
            i += 1
            mult = 1
            if i < len(tokens) and tokens[i].isdigit():
                mult = int(tokens[i])
                i += 1
            for el, cnt in group.items():
                stack[-1][el] += cnt * mult
        elif re.match(r'[A-Z][a-z]?$', token):
            el = token
            i += 1
            cnt = 1
            if i < len(tokens) and tokens[i].isdigit():
                cnt = int(tokens[i])
                i += 1
            stack[-1][el] += cnt
        else:
            raise ValueError(f"Unexpected token: {token}")
    if len(stack) != 1:
        raise ValueError("Unmatched parentheses")
    return dict(stack[0])

def parse_reaction(reaction):
    sides = re.split(r'->|=', reaction)
    if len(sides) != 2:
        raise ValueError("Reaction must have exactly one '->' or '='")
    reactants = [s.strip() for s in sides[0].split('+') if s.strip()]
    products = [s.strip() for s in sides[1].split('+') if s.strip()]
    return reactants, products

def build_matrix(reactants, products):
    element_set = set()
    all_formulas = reactants + products
    parsed = [parse_formula(f) for f in all_formulas]
    for d in parsed:
        element_set.update(d.keys())
    elements = sorted(element_set)

    matrix_rows = []
    for el in elements:
        row = []
        for d in parsed[:len(reactants)]:
            row.append(d.get(el, 0))
        for d in parsed[len(reactants):]:
            row.append(-d.get(el, 0))
        matrix_rows.append(row)
    return Matrix(matrix_rows), elements

def balance_reaction(reaction):
    reactants, products = parse_reaction(reaction)
    M, elements = build_matrix(reactants, products)
    nullspace = M.nullspace()
    if not nullspace:
        raise ValueError("No solution found")
    vec = nullspace[0]
    lcm_val = lcm([val.q for val in vec])  # LCM of denominators
    coeffs = [abs(int(val * lcm_val)) for val in vec]
    return coeffs, reactants, products

def format_balanced(coeffs, reactants, products):
    def fmt_side(side, coefs):
        parts = []
        for c, f in zip(coefs, side):
            if c == 1:
                parts.append(f)
            else:
                parts.append(f"{c} {f}")
        return ' + '.join(parts)
    left = fmt_side(reactants, coeffs[:len(reactants)])
    right = fmt_side(products, coeffs[len(reactants):])
    return f"{left} -> {right}"

class ReactionBalancerDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reaction Balancer")
        self.setMinimumSize(600, 600)
        layout = QVBoxLayout(self)

        info_label = QLabel(
            "Enter one or more unbalanced reactions, one per line.\n"
            "Use '->' or '=' for reaction arrows, '+' to separate species.\n"
            "Example:\nH2 + O2 -> H2O\nC3H8 + O2 = CO2 + H2O"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        self.input_edit = QTextEdit()
        self.input_edit.setFont(QFont("Courier New", 10))
        layout.addWidget(self.input_edit)

        btn_layout = QHBoxLayout()
        self.balance_btn = QPushButton("Balance All")
        self.copy_btn = QPushButton("Copy Selected")
        btn_layout.addWidget(self.balance_btn)
        btn_layout.addWidget(self.copy_btn)
        layout.addLayout(btn_layout)

        self.result_list = QListWidget()
        layout.addWidget(self.result_list)

        self.balance_btn.clicked.connect(self.balance_all)
        self.copy_btn.clicked.connect(self.copy_selected)

    def balance_all(self):
        self.result_list.clear()
        reactions = self.input_edit.toPlainText().strip().splitlines()
        for reaction in reactions:
            if not reaction.strip():
                continue
            try:
                coeffs, reactants, products = balance_reaction(reaction)
                balanced = format_balanced(coeffs, reactants, products)
                item = QListWidgetItem(balanced)
                self.result_list.addItem(item)
                log_event("Reaction Balancer", reaction, balanced)
            except Exception as e:
                item = QListWidgetItem(f"Error balancing '{reaction}': {e}")
                item.setForeground(QColor(Qt.GlobalColor.red))
                self.result_list.addItem(item)
                log_event("Reaction Balancer", reaction, f"Error: {e}")

    def copy_selected(self):
        selected = self.result_list.selectedItems()
        if not selected:
            QMessageBox.information(self, "Copy", "Select an item to copy.")
            return
        text = "\n".join(item.text() for item in selected)
        clipboard = self.clipboard()
        clipboard.setText(text)

def open_reaction_balancer(preload=None):
    dlg = ReactionBalancerDialog()
    if preload:
        dlg.input_edit.setPlainText(preload)
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

from data_utils import (settings_path, results_dir, ptable_path, element_favs_path, load_element_data)

settings_path = settings_path
results_dir = results_dir
ptable_path = ptable_path
element_favs_path = element_favs_path

class ElementPropertyGrapher(QDialog):
    def __init__(self, preload=None):
        super().__init__()
        self.setWindowTitle("Element Property Grapher")
        self.resize(900, 600)
        self.data = load_element_data()  # No args here, uses internal ptable_path
        self.settings = {}
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                self.settings = json.load(f)
        except Exception:
            pass
        self.favs = self.load_favorites()

        self.all_props = sorted(
            k for k, v in next(iter(self.data.values())).items()
            if k.lower() != "symbol" and not isinstance(v, list)
        )

        self.category_colors = self.get_category_colors()

        self.init_ui()
        if preload:
            self.prop_dd.setCurrentText(str(preload))
            log_event("Property Grapher (Chain)", preload, "Waiting for plot")
        else:
            default_prop = self.settings.get("default_property", "Electronegativity")
            if default_prop in self.all_props:
                self.prop_dd.setCurrentText(default_prop)

    def load_favorites(self):
        try:
            with open(element_favs_path, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
        
    def get_category_colors(self):
        color_map = {
            "alkali metal": "#FF6666",
            "alkaline earth metal": "#FFDEAD",
            "transition metal": "#FFB347",
            "post-transition metal": "#FFD700",
            "metalloid": "#ADFF2F",
            "nonmetal": "#90EE90",
            "halogen": "#87CEFA",
            "noble gas": "#D8BFD8",
            "lanthanide": "#FF69B4",
            "actinide": "#BA55D3",
        }
        return color_map

    def init_ui(self):
        layout = QVBoxLayout(self)

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Property to Graph:"))

        self.prop_dd = QComboBox()
        self.prop_dd.setEditable(True)
        self.prop_dd.addItems(self.all_props)
        self.prop_dd.setMinimumWidth(300)
        top_row.addWidget(self.prop_dd)

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter properties...")
        top_row.addWidget(self.filter_input)

        self.log_x_cb = QCheckBox("Logarithmic X scale")
        top_row.addWidget(self.log_x_cb)

        self.log_y_cb = QCheckBox("Logarithmic Y scale")
        top_row.addWidget(self.log_y_cb)

        self.show_labels_cb = QCheckBox("Show element symbols")
        self.show_labels_cb.setChecked(True)
        top_row.addWidget(self.show_labels_cb)

        layout.addLayout(top_row)

        btn_row = QHBoxLayout()
        self.plot_btn = QPushButton("Plot")
        self.save_btn = QPushButton("Save Plot")
        self.export_btn = QPushButton("Export CSV")
        btn_row.addWidget(self.plot_btn)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.export_btn)
        layout.addLayout(btn_row)

        self.fig, self.ax = plt.subplots(figsize=(10, 5), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.plot_btn.clicked.connect(self.plot)
        self.save_btn.clicked.connect(self.save_plot)
        self.export_btn.clicked.connect(self.export_csv)
        self.filter_input.textChanged.connect(self.filter_properties)

    def filter_properties(self, text):
        text = text.lower()
        self.prop_dd.clear()
        filtered = [p for p in self.all_props if text in p.lower()]
        self.prop_dd.addItems(filtered)
        if filtered:
            self.prop_dd.setCurrentIndex(0)

    def plot(self):
        prop = self.prop_dd.currentText()
        if not prop:
            QMessageBox.warning(self, "Input Error", "Select a property to graph.")
            return

        self.ax.clear()

        xs, ys, symbols, names, colors = [], [], [], [], []

        for el in self.data.values():
            x = el.get("AtomicNumber") or el.get("number")
            y = el.get(prop)
            if x is None or y is None:
                continue
            xs.append(x)
            ys.append(y)
            symbols.append(el["symbol"])
            names.append(el.get("name", ""))
            etype = el.get("Type", "").lower()
            color = self.category_colors.get(etype, "#1f77b4")
            if el["symbol"] in self.favs:
                color = "#FFD700"
            colors.append(color)

        if not xs:
            QMessageBox.information(self, "No Data", f"No data points available for property '{prop}'.")
            return

        order = np.argsort(xs)
        xs = np.array(xs)[order]
        ys = np.array(ys)[order]
        symbols = np.array(symbols)[order]
        names = np.array(names)[order]
        colors = np.array(colors)[order]

        scatter = self.ax.scatter(xs, ys, s=60, c=colors, edgecolors='black', picker=5, zorder=3)

        if self.show_labels_cb.isChecked():
            for i, (x_, y_, sym) in enumerate(zip(xs, ys, symbols)):
                dx = 0.5 if i % 2 == 0 else -0.5
                dy = 0.3 if i % 3 == 0 else -0.3
                self.ax.text(x_ + dx, y_ + dy, sym, fontsize=8, ha='center', va='center', zorder=5)

        self.ax.set_xlabel("Atomic Number")
        self.ax.set_ylabel(prop)
        self.ax.set_title(f"{prop} vs Atomic Number")
        self.ax.grid(True)

        self.ax.set_xscale("log" if self.log_x_cb.isChecked() else "linear")
        self.ax.set_yscale("log" if self.log_y_cb.isChecked() else "linear")

        self.annot = self.ax.annotate(
            "",
            xy=(0, 0), xytext=(15, 15),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->"),
            fontsize=9
        )
        self.annot.set_visible(False)

        def update_annot(ind):
            idx = ind["ind"][0]
            pos = scatter.get_offsets()[idx]
            self.annot.xy = pos
            text = f"{names[idx]} ({symbols[idx]})\nAtomic Number: {xs[idx]}\n{prop}: {ys[idx]}"
            self.annot.set_text(text)
            self.annot.get_bbox_patch().set_facecolor('#FFFFE0')
            self.annot.get_bbox_patch().set_alpha(0.9)

        def hover(event):
            vis = self.annot.get_visible()
            if event.inaxes == self.ax:
                cont, ind = scatter.contains(event)
                if cont:
                    update_annot(ind)
                    self.annot.set_visible(True)
                    self.canvas.draw_idle()
                elif vis:
                    self.annot.set_visible(False)
                    self.canvas.draw_idle()

        self.canvas.mpl_disconnect(getattr(self, '_hover_cid', None))
        self._hover_cid = self.canvas.mpl_connect("motion_notify_event", hover)

        self.canvas.draw()

        log_event("Property Grapher", prop, f"Plotted {len(xs)} elements")

    def save_plot(self):
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        prop = self.prop_dd.currentText()
        filename = f"{prop}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
        path = os.path.join(results_dir, filename)
        self.fig.savefig(path)
        QMessageBox.information(self, "Saved", f"Plot saved to:\n{path}")
        log_event("Property Grapher", prop, f"Plot saved: {path}")

    def export_csv(self):
        prop = self.prop_dd.currentText()
        xs, ys, symbols, names = [], [], [], []
        for el in self.data.values():
            x = el.get("AtomicNumber") or el.get("number")
            y = el.get(prop)
            if x is None or y is None:
                continue
            xs.append(x)
            ys.append(y)
            symbols.append(el["symbol"])
            names.append(el.get("name", ""))
        if not xs:
            QMessageBox.information(self, "No Data", "No data to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", f"{prop}.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            import csv
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["AtomicNumber", "Symbol", "Name", prop])
                for x, sym, name, y in zip(xs, symbols, names, ys):
                    writer.writerow([x, sym, name, y])
            QMessageBox.information(self, "Exported", f"Data exported to:\n{path}")
            log_event("Property Grapher", prop, f"Exported CSV: {path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to export CSV: {e}")

def open_property_grapher(preload=None):
    dlg = ElementPropertyGrapher(preload)
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
