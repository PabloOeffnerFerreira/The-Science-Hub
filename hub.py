import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt

import data_utils
import utilities
import toolkits
from coder import open_coder

# Panels for integrated central area:

class LastUsedPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Last Used Tool"))

        self.msg_label = QLabel("Loading...")
        self.msg_label.setWordWrap(True)
        layout.addWidget(self.msg_label)

        self.refresh()

    def refresh(self):
        try:
            with open(data_utils.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            msg = lines[-1].strip() if lines else "No entries found."
        except Exception:
            msg = "No log available."
        self.msg_label.setText(msg)


class FavoritesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Favorites"))

        self.fav_list = QListWidget()
        layout.addWidget(self.fav_list)

        self.load_favorites()

    def load_favorites(self):
        self.fav_list.clear()
        import json

        # Mineral favorites
        try:
            with open(data_utils.mineral_favs_path, "r") as f:
                mineral_favs = json.load(f)
        except Exception:
            mineral_favs = []

        if mineral_favs:
            self.fav_list.addItem("★ Mineral Favorites:")
            for item in mineral_favs:
                self.fav_list.addItem(f"  {item}")
        else:
            self.fav_list.addItem("No mineral favorites.")

        # Element favorites (optional, add similarly)
        try:
            with open(data_utils.element_favs_path, "r") as f:
                elem_favs = json.load(f)
        except Exception:
            elem_favs = []

        if elem_favs:
            self.fav_list.addItem("★ Element Favorites:")
            for sym in elem_favs:
                self.fav_list.addItem(f"  {sym}")
        else:
            self.fav_list.addItem("No element favorites.")

        # Could add science library favorites here similarly

from PyQt6.QtCore import QTimer

class WindowManagerPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Window Manager"))

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.focus_btn = QPushButton("Focus")
        self.close_btn = QPushButton("Close")
        self.refresh_btn = QPushButton("Refresh")
        btn_layout.addWidget(self.focus_btn)
        btn_layout.addWidget(self.close_btn)
        btn_layout.addWidget(self.refresh_btn)
        layout.addLayout(btn_layout)

        self.focus_btn.clicked.connect(self.focus_selected)
        self.close_btn.clicked.connect(self.close_selected)
        self.refresh_btn.clicked.connect(self.refresh_windows)

        self.refresh_windows()

        # Optional: auto-refresh every 5 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_windows)
        self.timer.start(5000)

    def refresh_windows(self):
        self.list_widget.clear()
        app = QApplication.instance()
        windows = [
            w for w in app.topLevelWidgets()
            if w.isVisible()
            and w.objectName() != "main_science_hub"
        ]
        for w in windows:
            title = w.windowTitle() or "(Untitled)"
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, w)
            self.list_widget.addItem(item)


    def selected_window(self):
        item = self.list_widget.currentItem()
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def focus_selected(self):
        w = self.selected_window()
        if w:
            w.raise_()
            w.activateWindow()

    def close_selected(self):
        w = self.selected_window()
        if w:
            w.close()
            self.refresh_windows()


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
        self.launch_btn.setEnabled(False)
        item = self.category_list.currentItem()
        if not item:
            return
        launcher = TOOLKIT_LAUNCHERS.get(item.text())
        if launcher:
            launcher()

    def initUI(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Sidebar (unchanged)
        sidebar = QVBoxLayout()
        sidebar.addWidget(QLabel("Categories"))
        self.category_list = QListWidget()
        self.category_list.addItems(["Chemistry", "Biology", "Physics", "Geology", "Math"])
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

        # Central panel with headline, integrated tools, and credits
        central_panel = QVBoxLayout()

        headline = QLabel("Welcome to Science Hub")
        headline.setStyleSheet("font-size: 28px; font-weight: bold;")
        central_panel.addWidget(headline)

        central_panel.addSpacing(16)

        # Add your integrated panels here
        self.last_used_panel = LastUsedPanel()
        self.favorites_panel = FavoritesPanel()
        self.window_manager_panel = WindowManagerPanel()

        central_panel.addWidget(self.last_used_panel)
        central_panel.addWidget(self.favorites_panel)
        central_panel.addWidget(self.window_manager_panel)

        central_panel.addStretch()

        credits = QLabel("Science Hub by Pablo Oeffner Ferreira")
        credits.setStyleSheet("color: #bbb; font-size: 12px; margin-top: 40px;")
        central_panel.addWidget(credits)

        central_panel_frame = QFrame()
        central_panel_frame.setLayout(central_panel)
        central_panel_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Utility panel - remove buttons for "Last Used Tool", "View Favorites", "Window Manager"
        utility_panel = QVBoxLayout()
        utility_panel.addWidget(QLabel("Utility Panel"))

        util_buttons = [
            ("Simple Calculator", utilities.open_simple_calculator),
            ("View Log", utilities.open_log),
            ("Export Log", utilities.export_log_to_md),
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


if data_utils.load_settings().get("clear_log_on_startup", False):
    try:
        with open(data_utils.log_path, "w", encoding="utf-8") as f:
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