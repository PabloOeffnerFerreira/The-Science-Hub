from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, 
    QComboBox, QScrollArea, QMainWindow, QDialog, QApplication
)
from PyQt6.QtCore import Qt
import os
import datetime
from data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data, ai_chatlogs_dir
)

CHAINABLE_TOOLS = {}  # Will be injected dynamically

def log_chain(text):
    with open("chainmode_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {text}\n")

def get_recent_log_outputs(log_path="calchub_log.txt", limit=20):
    if not os.path.exists(log_path):
        return []

    entries = []
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in reversed(lines):
        if "Input:" in line:
            parts = line.strip().split("Input:")
            if len(parts) == 2:
                meta, rest = parts
                if "Output:" in rest:
                    input_part, output = rest.split("Output:", 1)
                    entries.append((meta.strip(), output.strip()))
                else:
                    entries.append((meta.strip(), rest.strip()))
                if len(entries) >= limit:
                    break
    return entries

class ChainModeDialog(QDialog):
    def __init__(self, tool_map, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chain Mode")
        self.tool_map = tool_map
        self.recent_logs = get_recent_log_outputs()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Select a recent result:"))

        self.log_list = QListWidget()
        for meta, output in self.recent_logs:
            self.log_list.addItem(f"{meta} → {output}")
        layout.addWidget(self.log_list)

        layout.addWidget(QLabel("Select destination tool:"))
        self.tool_menu = QComboBox()
        self.tool_menu.addItems(self.tool_map.keys())
        layout.addWidget(self.tool_menu)

        launch_btn = QPushButton("Chain to Tool")
        launch_btn.clicked.connect(self.launch_chain)
        layout.addWidget(launch_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_log)
        layout.addWidget(refresh_btn)

        self.setLayout(layout)

    def refresh_log(self):
        self.log_list.clear()
        self.recent_logs = get_recent_log_outputs()
        for meta, output in self.recent_logs:
            self.log_list.addItem(f"{meta} → {output}")

    def launch_chain(self):
        selected_index = self.log_list.currentRow()
        tool_name = self.tool_menu.currentText()

        if selected_index == -1 or tool_name not in self.tool_map:
            return

        _, output = self.recent_logs[selected_index]
        tool_func = self.tool_map[tool_name]
        tool_func(preload=output)

def open_chain_mode(tool_map):
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    dialog = ChainModeDialog(tool_map)
    dialog.exec()
