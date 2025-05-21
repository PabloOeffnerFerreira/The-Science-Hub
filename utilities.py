from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit,
    QMessageBox, QWidget, QTableWidget, QTableWidgetItem, QFrame, QCheckBox,
    QApplication, QListWidget, QListWidgetItem, QComboBox,
)
from PyQt6.QtCore import Qt, QTimer
import json
import subprocess
import sys
import os
import datetime

from data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data, ai_chatlogs_dir
)


def log_chain(text):
    with open(chain_log_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {text}\n")

from chemtools import (
    open_mass_calculator,
    open_isotope_tool,
    open_shell_visualizer,
    open_phase_predictor,
    open_comparator,
    open_reaction_balancer,
    open_property_grapher,
)
from element_viewer import open_element_viewer
from mol_assembler import open_molecule_assembler

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
    open_speed_calculator,
    open_ferromagnetism_helper
)

from math_tools_1 import (
    open_function_plotter,
    open_quadratic_solver,
    open_triangle_solver,
)

from geo_tools_1 import (
    open_mineral_id_tool,
    open_radioactive_dating_tool,
    open_plate_boundary_tool,
    open_mineral_explorer,
    open_plate_velocity_calculator,
)

from data_utils import _open_dialogs, register_window, log_event

def open_simple_calculator(preload=None):
    class CalculatorDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Simple Calculator")
            self.setMinimumWidth(350)
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Enter expression:"))
            self.expr_input = QLineEdit()
            layout.addWidget(self.expr_input)
            self.result_label = QLabel()
            layout.addWidget(self.result_label)
            calc_btn = QPushButton("Calculate")
            calc_btn.clicked.connect(self.compute)
            layout.addWidget(calc_btn)

            if preload:
                self.expr_input.setText(str(preload))
                # Optional: auto-calculate on preload
                self.compute()

        def compute(self):
            expr = self.expr_input.text()
            try:
                result = eval(expr)
                self.result_label.setText(f"Result: {result}")
                log_event("Simple Calculator", expr, result)
            except Exception as e:
                self.result_label.setText("Invalid expression.")
                log_event("Simple Calculator", expr, "Invalid expression")

    dlg = CalculatorDialog()
    dlg.show()
    register_window("Simple Calculator", dlg)


def open_log():
    class LogDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Session Log")
            self.setMinimumSize(600, 500)
            vbox = QVBoxLayout(self)
            search_layout = QHBoxLayout()
            search_label = QLabel("Search:")
            search_layout.addWidget(search_label)
            self.search_input = QLineEdit()
            search_layout.addWidget(self.search_input)
            reload_btn = QPushButton("Reload")
            reload_btn.clicked.connect(self.load_log)
            search_layout.addWidget(reload_btn)
            clear_btn = QPushButton("Clear Log")
            clear_btn.clicked.connect(self.clear_log)
            search_layout.addWidget(clear_btn)
            vbox.addLayout(search_layout)
            self.log_box = QTextEdit()
            self.log_box.setReadOnly(True)
            vbox.addWidget(self.log_box)
            self.load_log()
            self.search_input.textChanged.connect(self.filter_log)

        def load_log(self):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except FileNotFoundError:
                content = "No logs found."
            self.full_log = content
            self.log_box.setText(content)

        def filter_log(self):
            keyword = self.search_input.text().strip().lower()
            if not keyword:
                self.log_box.setText(self.full_log)
                return
            filtered = "\n".join(
                line for line in self.full_log.splitlines()
                if keyword in line.lower()
            )
            self.log_box.setText(filtered)

        def clear_log(self):
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("")
            self.load_log()

    dlg = LogDialog()
    dlg.show()
    register_window("Session Log", dlg)

def show_last_used():
    try:
        with open(log_path, "r", encoding="utf-8") as f:  # Use the built path
            lines = f.readlines()
        msg = lines[-1].strip() if lines else "No entries found."
        print("MSG:", repr(msg))  # For debugging
    except FileNotFoundError:
        msg = "No log available."
        print("MSG:", repr(msg))  # For debugging
    dlg = QMessageBox()
    dlg.setWindowTitle("Last Used Tool")
    dlg.setText(msg)
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

def show_favorites():
    class FavoritesDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Favorites")
            vbox = QVBoxLayout(self)
            vbox.addWidget(QLabel("Favorites"))

            # Mineral favorites
            try:
                with open(mineral_favs_path, "r") as f:
                    mineral_favs = json.load(f)
            except FileNotFoundError:
                mineral_favs = []
            if mineral_favs:
                vbox.addWidget(QLabel("★ Mineral Favorites"))
                for name in mineral_favs:
                    vbox.addWidget(QLabel(name))
            else:
                vbox.addWidget(QLabel("No starred minerals."))

            # Element favorites
            try:
                with open(element_favs_path, "r") as f:
                    elem_syms = json.load(f)
            except FileNotFoundError:
                elem_syms = []
            # Map from symbol to full element name, using your element data
            if elem_syms:
                try:
                    with open(ptable_path, encoding="utf-8") as f:
                        table = json.load(f)
                        sym2name = {el["symbol"]: el["name"] for el in table["elements"]}
                except Exception:
                    sym2name = {sym: "" for sym in elem_syms}
                vbox.addWidget(QLabel("★ Element Favorites"))
                for sym in elem_syms:
                    label = f"{sym} ({sym2name.get(sym, 'Unknown')})"
                    vbox.addWidget(QLabel(label))
            else:
                vbox.addWidget(QLabel("No starred elements."))

            # Science Library favorites
            library_path = library_file
            library_favs = []
            if os.path.exists(library_path):
                for file in os.listdir(library_path):
                    if file.endswith(".json"):
                        try:
                            with open(os.path.join(library_path, file), "r", encoding="utf-8") as f:
                                data = json.load(f)
                                if data.get("favorite"):
                                    library_favs.append(data["title"])
                        except:
                            continue
            if library_favs:
                vbox.addWidget(QLabel("★ Science Library Favorites"))
                for name in library_favs:
                    vbox.addWidget(QLabel(name))
            else:
                vbox.addWidget(QLabel("No starred library entries."))

    dlg = FavoritesDialog()
    dlg.show()
    register_window("Favorites", dlg)

def export_log_to_md():

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            log = f.readlines()
    except FileNotFoundError:
        return
    if not os.path.exists(exports_dir):
        os.makedirs(exports_dir)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(exports_dir, f"session_log_{date_str}.md")
    with open(filename, "w", encoding="utf-8") as out:
        out.write(f"# Science Hub Log Export\n**Date:** {date_str}\n\n---\n\n")
        for line in log:
            if line.strip() == "":
                continue
            if line.startswith("[") and "]" in line:
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
    try:
        os.startfile(exports_dir)
    except Exception:
        pass

def show_window_manager():
    class WindowManagerDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Window Manager")
            self.setMinimumSize(380, 320)
            self.layout = QVBoxLayout(self)
            self.layout.setSpacing(3)
            self.layout.setContentsMargins(8, 8, 8, 8)
            
            self.list = QListWidget()
            self.list.setSpacing(2)
            self.layout.addWidget(self.list)
            
            btn_row = QHBoxLayout()
            self.focus_btn = QPushButton("Focus")
            self.close_btn = QPushButton("Close")
            btn_row.addWidget(self.focus_btn)
            btn_row.addWidget(self.close_btn)
            self.layout.addLayout(btn_row)

            self.focus_btn.clicked.connect(self.focus_window)
            self.close_btn.clicked.connect(self.close_window)

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.refresh)
            self.timer.start(500)  # every 0.5s

            self.refresh()

        def refresh(self):
            # Remember the currently selected window object
            selected_win = self.selected_window()
            self.list.clear()
            app = QApplication.instance()

            # Get the hub/main window (you can set an object name or check type/title)
            # Let's assume your hub window has the title "Science Hub"
            windows = [
                w for w in app.topLevelWidgets()
                if w.isVisible()
                and w != self
                and w.objectName() != "main_science_hub"
                and w.windowTitle() != "Window Manager"
            ]
            selected_row = 0
            for i, w in enumerate(windows):
                win_type = w.metaObject().className().replace("PyQt6.QtWidgets.", "")
                title = w.windowTitle() or "(Untitled)"
                item = QListWidgetItem(f"{title}  [{win_type}]")
                item.setData(Qt.ItemDataRole.UserRole, w)
                item.setToolTip(f"{repr(w)}")
                self.list.addItem(item)
                if selected_win and w is selected_win:
                    selected_row = i
            if self.list.count() > 0:
                self.list.setCurrentRow(selected_row)


        def selected_window(self):
            item = self.list.currentItem()
            return item.data(Qt.ItemDataRole.UserRole) if item else None

        def focus_window(self):
            w = self.selected_window()
            if w:
                w.raise_()
                w.activateWindow()

        def close_window(self):
            w = self.selected_window()
            if w:
                w.close()

    dlg = WindowManagerDialog()
    dlg.show()
    register_window("Window Manager", dlg)
TOOLS = [
    # Chemistry
    ("Mass Calculator", open_mass_calculator, True),
    ("Isotopic Notation", open_isotope_tool, True),
    ("Shell Visualizer", open_shell_visualizer, True),
    ("Phase Predictor", open_phase_predictor, True),
    ("Element Comparator", open_comparator, True),
    ("Reaction Balancer", open_reaction_balancer, True),
    ("Property Grapher", open_property_grapher, False),  # Visualization, not chainable
    ("Molecule Assembler", open_molecule_assembler, True),
    ("Element Viewer", open_element_viewer, False),  # Browsing tool

    # Biology
    ("Transcription Tool", open_transcription_tool, True),
    ("Codon Lookup Tool", open_codon_lookup_tool, True),
    ("Osmosis Tool", open_osmosis_tool, False),  # No direct output chaining
    ("Molecular Weight Calculator (Bio)", open_molecular_weight_calculator, True),
    ("pH Calculator", open_ph_calculator, True),
    ("Population Growth Calculator", open_population_growth_calculator, True),
    ("Reverse Complement Tool", open_reverse_complement_tool, True),
    ("Translate DNA Tool", open_translate_dna_tool, True),
    ("GC Content Tool", open_gc_content_tool, True),
    ("Sequence File Parser Tool", open_seq_file_parser_tool, True),
    ("Pairwise Alignment Tool", open_pairwise_align_tool, True),

    # Physics
    ("Unit Converter", open_unit_converter, True),
    ("Terminal Velocity Calculator", open_terminal_velocity_calculator, True),
    ("Projectile Motion Tool", open_projectile_motion_tool, True),
    ("Ohm’s Law Tool", open_ohms_law_tool, True),
    ("Lens Calculator", open_lens_calculator, True),
    ("Acceleration Calculator", open_acceleration_calculator, True),
    ("Drag Force Calculator", open_drag_force_calculator, True),
    ("Force Calculator", open_force_calculator, True),
    ("Kinetic Energy Calculator", open_kinetic_energy_calculator, True),
    ("Speed Calculator", open_speed_calculator, True),
    ("Ferromagnetism Helper", open_ferromagnetism_helper, False),

    # Math
    ("Function Plotter", open_function_plotter, False),  # Graph only
    ("Quadratic Solver", open_quadratic_solver, True),
    ("Triangle Solver", open_triangle_solver, True),

    # Geology
    ("Mineral ID Tool", open_mineral_id_tool, True),
    ("Radioactive Dating Tool", open_radioactive_dating_tool, True),
    ("Plate Boundary Tool", open_plate_boundary_tool, False),
    ("Mineral Explorer", open_mineral_explorer, False),
    ("Plate Velocity Calculator", open_plate_velocity_calculator, True),

    # Other
    ("Simple Calculator", open_simple_calculator, True),  # No preload
]

def open_chain_mode():
    class ChainDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Chain Mode")
            self.setMinimumWidth(350)
            vbox = QVBoxLayout(self)

            self.list = QListWidget()
            vbox.addWidget(self.list)

            row = QHBoxLayout()
            self.tool_box = QComboBox()
            for name, fn, chainable in TOOLS:
                if chainable:
                    self.tool_box.addItem(name, fn)

            row.addWidget(self.tool_box)
            self.add_btn = QPushButton("Add to Chain")
            row.addWidget(self.add_btn)
            vbox.addLayout(row)

            self.start_btn = QPushButton("Start Chain")
            vbox.addWidget(self.start_btn)

            self.add_btn.clicked.connect(self.add_tool)
            self.start_btn.clicked.connect(self.start_chain)

            self.chain = []

        def add_tool(self):
            idx = self.tool_box.currentIndex()
            name = self.tool_box.currentText()
            fn = self.tool_box.currentData()
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, fn)
            self.list.addItem(item)
            self.chain.append((name, fn, True))

        def after_step(self, dlg):
            output = self.extract_output(dlg)
            if output is None:
                log_chain("No usable output. Halting chain.")
                QMessageBox.information(self, "Chain Stopped", "No output was produced by this tool.")
                return
            self.current_preload = output
            log_chain(f"Extracted output: {self.current_preload}")
            self.chain_index += 1
            self.run_next_step()


        def start_chain(self):
            if not self.chain:
                QMessageBox.warning(self, "Empty", "Add tools to the chain first!")
                return

            self.chain_index = 0
            self.current_preload = None

            self.run_next_step()

        def run_next_step(self):
            if self.chain_index >= len(self.chain):
                log_chain("Chain complete.")
                return

            name, fn, _ = self.chain[self.chain_index]
            log_chain(f"Launching: {name} with preload: {self.current_preload}")

            try:
                fn(preload=self.current_preload)
            except TypeError:
                fn()
            dlg = _open_dialogs[-1]
            dlg.finished.connect(lambda _: self.after_step(dlg))

        def extract_output(self, dlg):
            log_chain(f"Scanning output widgets from: {dlg.windowTitle()}")
            for widget_type in (QLabel, QLineEdit, QTextEdit):
                for child in dlg.findChildren(widget_type):
                    if isinstance(child, QLabel):
                        text = child.text()
                        if text.lower().startswith("result:"):
                            clean = text.split(":", 1)[1].strip()
                            log_chain(f"Found QLabel result → '{clean}'")
                            return clean
                    elif isinstance(child, QLineEdit):
                        # Prefer entry only if no result label found
                        entry = child.text().strip()
                        if entry:
                            log_chain(f"  Found QLineEdit → '{entry}'")
                            fallback = entry
                    elif isinstance(child, QTextEdit):
                        txt = child.toPlainText().strip()
                        if txt:
                            log_chain(f"  Found QTextEdit → '{txt}'")
                            fallback = txt
            # If we get here, no 'Result:' label was found
            return fallback if 'fallback' in locals() else None

    dlg = ChainDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))


def launch_gallery():
    script_path = os.path.join(os.path.dirname(__file__), "gallery.py")
    subprocess.Popen([sys.executable, script_path])

def launch_ai_assistant_subprocess():
    script_path = os.path.join(os.path.dirname(__file__), "launch_ai_assistant.py")
    subprocess.Popen([sys.executable, script_path])

def launch_openalex_browser():
    script_path = os.path.join(os.path.dirname(__file__), "openalex_browser.py")
    subprocess.Popen([sys.executable, script_path])

def launch_molecule_library():
    script_path = os.path.join(os.path.dirname(__file__), "molecule_library.py")
    subprocess.Popen([sys.executable, script_path])

def launch_library():
    script_path = os.path.join(os.path.dirname(__file__), "library.py")
    subprocess.Popen([sys.executable, script_path])