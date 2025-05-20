import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QFrame, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt
import data_utils
import utilities
from data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data, ai_chatlogs_dir
)

import tkinter as tk
_hidden_tk_root = tk.Tk()
_hidden_tk_root.withdraw()

import toolkits
from coder import open_coder


TOOLKIT_LAUNCHERS = {
    "Math": toolkits.open_math_tools_hub,
    "Physics": toolkits.open_physics_tools_hub,
    "Chemistry": toolkits.open_chemistry_tools_hub,
    "Biology": toolkits.open_biology_tools_hub,
    "Geology": toolkits.open_geology_tools_hub,
}
class ScienceHub(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The Science Hub")
        self.setObjectName("main_science_hub")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow { background: #23272E; }
            QLabel, QListWidget, QPushButton {
                color: #EEE;
                font-size: 14px;
            }
            QPushButton {
                background: #444; 
                border-radius: 8px;
                padding: 10px 18px;
                margin: 4px 0;
            }
            QPushButton:hover {
                background: #333;
            }
            QListWidget {
                background: #1A1A1A;
                border: none;
                min-width: 160px;
            }
            QFrame#UtilityPanel {
                background: #292d36;
                border-radius: 18px;
                padding: 16px;
            }
        """)
        self.initUI()

    def update_launch_btn_state(self):
        self.launch_btn.setEnabled(self.category_list.currentItem() is not None)


    def launch_toolkit(self):
        self.launch_btn.setEnabled(False)  # prevent accidental double launch
        item = self.category_list.currentItem()
        if not item:
            return
        category = item.text()
        launcher = TOOLKIT_LAUNCHERS.get(category)
        if launcher:
            launcher()


    def initUI(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        sidebar = QVBoxLayout()
        sidebar.addWidget(QLabel("Categories"))

        self.category_list = QListWidget()
        self.category_list.addItems([
            "Chemistry", "Biology", "Physics", "Geology", "Math"
        ])
        sidebar.addWidget(self.category_list)

        self.launch_btn = QPushButton("Launch Toolkit")
        self.launch_btn.setEnabled(False)
        sidebar.addWidget(self.launch_btn)

        self.category_list.itemSelectionChanged.connect(self.update_launch_btn_state)
        self.launch_btn.clicked.connect(self.launch_toolkit)

        sidebar.addStretch()

        sidebar_frame = QFrame()
        sidebar_frame.setLayout(sidebar)
        sidebar_frame.setFixedWidth(200)


        central_panel = QVBoxLayout()
        headline = QLabel("Welcome to Science Hub")
        headline.setStyleSheet("font-size: 28px; font-weight: bold;")
        central_panel.addWidget(headline)
        central_panel.addSpacing(16)
        subtext = QLabel("Your personal modular science environment.")
        central_panel.addWidget(subtext)
        # You can add screenshots, images, or embed widgets here
        central_panel.addSpacing(24)
        credits = QLabel("Science Hub by Pablo Oeffner Ferreira")
        credits.setStyleSheet("color: #bbb; font-size: 12px; margin-top: 40px;")
        central_panel.addWidget(credits)
        central_panel.addStretch()

        central_panel_frame = QFrame()
        central_panel_frame.setLayout(central_panel)
        central_panel_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        utility_panel = QVBoxLayout()
        utility_panel.addWidget(QLabel("Utility Panel"))

        util_buttons = [
            ("Simple Calculator", utilities.open_simple_calculator),
            ("View Log", utilities.open_log),
            ("Last Used Tool", utilities.show_last_used),
            ("View Favorites", utilities.show_favorites),
            ("Export Log", utilities.export_log_to_md),
            ("Window Manager", utilities.show_window_manager),
            ("Chain Mode", utilities.open_chain_mode),
            ("Gallery", utilities.launch_gallery),
            ("AI Assistant", utilities.launch_ai_assistant_subprocess),
            ("OpenAlex Browser", utilities.launch_openalex_browser),
            ("Molecule Library", utilities.launch_molecule_library),
            ("Science Library", utilities.launch_library),
            ("Settings", data_utils.open_settings),
            ("Code Editor", open_coder),
        ]

        for label, func in util_buttons:
            btn = QPushButton(label)
            btn.clicked.connect(func)
            utility_panel.addWidget(btn)
        utility_panel.addStretch()

        utility_panel_frame = QFrame()
        utility_panel_frame.setLayout(utility_panel)
        utility_panel_frame.setObjectName("UtilityPanel")
        utility_panel_frame.setFixedWidth(240)

        main_layout.addWidget(sidebar_frame)
        main_layout.addWidget(central_panel_frame)
        main_layout.addWidget(utility_panel_frame)

from data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data, ai_chatlogs_dir
)

if load_settings().get("clear_log_on_startup", False):
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("")
    except Exception:
        pass

def main():
    app = QApplication(sys.argv)
    win = ScienceHub()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()