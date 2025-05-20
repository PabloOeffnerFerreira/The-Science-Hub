import os
import json
import re
import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit,
    QMessageBox, QWidget, QTableWidget, QTableWidgetItem, QFrame, QCheckBox,
    QApplication, QListWidget, QListWidgetItem, QComboBox,)

tools_dir = os.path.dirname(os.path.abspath(__file__))
hub_dir = os.path.normpath(os.path.join(tools_dir, '..'))

# Key folders
logs_dir = os.path.join(hub_dir, 'logs')
exports_dir = os.path.join(hub_dir, "exports")
interndb_dir = os.path.join(hub_dir, 'interndatabases')
databases_dir = os.path.join(hub_dir, 'databases')
results_dir = os.path.join(hub_dir, 'results')
gallery_dir = os.path.join(hub_dir, 'gallery')
screenshots_dir = os.path.join(gallery_dir, 'screenshots')
images_dir = os.path.join(gallery_dir, 'images')
library_file = os.path.join(hub_dir, 'library_entries.json')
ai_chatlogs_dir = os.path.join(exports_dir, "ai_chats")

# Ensure all directories exist when writing files
for directory in [
    logs_dir, exports_dir, interndb_dir, databases_dir, results_dir, gallery_dir,
    screenshots_dir, images_dir, library_file, ai_chatlogs_dir
]:
    os.makedirs(directory, exist_ok=True)

# File paths
log_path = os.path.join(logs_dir, 'calchub_log.txt')
chain_log_path = os.path.join(logs_dir, 'chainmode_log.txt')
settings_path = os.path.join(interndb_dir, 'settings.json')
mineral_favs_path = os.path.join(interndb_dir, "mineral_favorites.json")
element_favs_path = os.path.join(interndb_dir, "element_favorites.json")
ptable_path = os.path.join(databases_dir, "PeriodicTableJSON.json")
mineral_db_path = os.path.join(databases_dir, "Minerals_Database.csv")
gallery_meta_path = os.path.join(interndb_dir, "gallery_meta.json")
knowledge_path = os.path.join(hub_dir, "knowledge.json")
def load_element_data():
    with open(ptable_path, "r", encoding="utf-8") as f:
        return {el["symbol"]: el for el in json.load(f)["elements"]}

def parse_formula(formula):
    """
    Parses a chemical formula string and returns a dict of element counts.
    Supports nested parentheses like Fe2(SO4)3 → {'Fe':2, 'S':3, 'O':12}
    """
    def multiply_counts(counts, factor):
        return {el: val * factor for el, val in counts.items()}

    def parse_chunk(s, i=0):
        elements = {}
        while i < len(s):
            if s[i] == '(':
                sub_counts, i = parse_chunk(s, i + 1)
                match = re.match(r'\d+', s[i:])
                mult = int(match.group()) if match else 1
                i += len(match.group()) if match else 0
                for el, count in multiply_counts(sub_counts, mult).items():
                    elements[el] = elements.get(el, 0) + count
            elif s[i] == ')':
                return elements, i + 1
            else:
                match = re.match(r'([A-Z][a-z]?)(\d*)', s[i:])
                if not match:
                    raise ValueError(f"Invalid element symbol at: {s[i:]}")
                symbol = match.group(1)
                count = int(match.group(2)) if match.group(2) else 1
                elements[symbol] = elements.get(symbol, 0) + count
                i += len(match.group(0))
        return elements, i

    return parse_chunk(formula)[0]

_open_dialogs = []
_open_windows_registry = {}  # name: dialog instance

def register_window(name, dialog):
    _open_dialogs.append(dialog)
    _open_windows_registry[name] = dialog
    # Remove from both on close
    def cleanup():
        if dialog in _open_dialogs:
            _open_dialogs.remove(dialog)
        if name in _open_windows_registry and _open_windows_registry[name] is dialog:
            del _open_windows_registry[name]
    dialog.finished.connect(lambda _: cleanup())


def log_event(tool, input_value, output_value):
    """Append a formatted log entry to the Science Hub session log."""
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            line = f"{timestamp} {tool} Input: {input_value} Output: {output_value}\n"
            f.write(line)
    except Exception as e:
        print("Logging failed:", e)

SETTINGS_PATH = "settings.json"

if not os.path.exists(interndb_dir):
    os.makedirs(interndb_dir)

def load_settings():
    if not os.path.exists(settings_path):
        return {
    "clear_log_on_startup": False,
    "show_half_life_plot": False
}

    with open(settings_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(settings):
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

def open_settings():
    settings = load_settings()
    class SettingsDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Settings")
            layout = QVBoxLayout(self)
            self.clear_log_cb = QCheckBox("Clear log on startup")
            self.clear_log_cb.setChecked(settings.get("clear_log_on_startup", False))
            self.show_plot_cb = QCheckBox("Enable decay curve plot in Half-Life Calculator")
            self.show_plot_cb.setChecked(settings.get("show_half_life_plot", False))
            layout.addWidget(self.show_plot_cb)
            layout.addWidget(self.clear_log_cb)
            btns = QHBoxLayout()
            save_btn = QPushButton("Save")
            save_btn.clicked.connect(self.save_settings)
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(self.close)
            btns.addWidget(save_btn)
            btns.addWidget(cancel_btn)
            layout.addLayout(btns)
        def save_settings(self):
            settings["clear_log_on_startup"] = self.clear_log_cb.isChecked()
            settings["show_half_life_plot"] = self.show_plot_cb.isChecked()
            save_settings(settings)
            self.close()
    dlg = SettingsDialog()
    dlg.show()
    register_window("Settings", dlg)
