import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QCheckBox, QTextEdit, QMessageBox
)
from PyQt6.QtGui import QFont, QBrush, QColor, QIcon
import os
from tools.utilities import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path
)

ELEMENTS_PATH = ptable_path
FAVS_PATH = element_favs_path

def load_elements():
    with open(ELEMENTS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    # Flatten and convert fields for easy access
    elements = []
    for el in data["elements"]:
        el = el.copy()
        el["search_blob"] = " ".join([
            str(el.get("name", "")),
            str(el.get("symbol", "")),
            str(el.get("number", "")),
            str(el.get("category", "")),
            str(el.get("shells", "")),
            str(el.get("electron_configuration", "")),
            str(el.get("appearance", "")),
            str(el.get("summary", "")),
        ]).lower()
        elements.append(el)
    return elements

def load_favs():
    try:
        with open(FAVS_PATH, "r") as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_favs(favs):
    with open(FAVS_PATH, "w") as f:
        json.dump(list(favs), f, indent=2)

def format_details(el):
    out = [
        f"<b>{el['name']} ({el['symbol']})</b>",
        f"Atomic Number: <b>{el['number']}</b>",
        f"Category: {el.get('category', '—')}",
        f"Atomic Mass: {el.get('atomic_mass', '—')} g/mol",
        f"Shells: {', '.join(str(x) for x in el.get('shells', []))}",
        f"Electron Config: {el.get('electron_configuration', '—')}",
        f"Density: {el.get('density', '—')} g/cm³",
        f"Melting Point: {el.get('melt', '—')} K",
        f"Boiling Point: {el.get('boil', '—')} K",
        f"Appearance: {el.get('appearance', '—')}",
        f"Summary: <br>{el.get('summary', '')}"
    ]
    return "<br><br>".join(out)

def open_element_viewer():
    class ElementViewerDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Element Viewer")
            self.elements = load_elements()
            self.favs = load_favs()
            self.filtered = self.elements.copy()
            self.setMinimumWidth(720)
            self.setMinimumHeight(450)
            main = QVBoxLayout(self)

            bar = QHBoxLayout()
            self.search = QLineEdit()
            self.search.setPlaceholderText("Search name, symbol, number, etc...")
            self.fav_cb = QCheckBox("Show Favorites Only")
            self.refresh_btn = QPushButton("Refresh")
            bar.addWidget(QLabel("Search:"))
            bar.addWidget(self.search)
            bar.addWidget(self.fav_cb)
            bar.addWidget(self.refresh_btn)
            main.addLayout(bar)

            self.list = QListWidget()
            main.addWidget(self.list)

            self.fav_btn = QPushButton("Toggle Favorite")
            main.addWidget(self.fav_btn)

            self.details = QTextEdit()
            self.details.setReadOnly(True)
            font = QFont("Consolas", 10)
            self.details.setFont(font)
            main.addWidget(self.details, 1)

            self.search.textChanged.connect(self.update_list)
            self.fav_cb.stateChanged.connect(self.update_list)
            self.refresh_btn.clicked.connect(self.update_list)
            self.list.currentItemChanged.connect(self.show_details)
            self.fav_btn.clicked.connect(self.toggle_favorite)

            self.update_list()

        def update_list(self):
            text = self.search.text().lower().strip()
            show_favs = self.fav_cb.isChecked()
            self.list.clear()
            self.filtered = []
            for el in self.elements:
                if show_favs and el["symbol"] not in self.favs:
                    continue
                if text and text not in el["search_blob"]:
                    continue
                self.filtered.append(el)
                label = f"{el['symbol']:>3}  {el['name']:<12} ({el['number']})"
                item = QListWidgetItem(label)
                if el["symbol"] in self.favs:
                    item.setForeground(QBrush(QColor("#d4af37")))  # gold
                    item.setFont(QFont("", 10, QFont.Weight.Bold))
                else:
                    item.setFont(QFont("", 10))
                item.setData(32, el)  # Store whole element dict
                self.list.addItem(item)
            if self.filtered:
                self.list.setCurrentRow(0)
            else:
                self.details.clear()

        def show_details(self, item):
            if not item:
                self.details.clear()
                return
            el = item.data(32)
            self.details.setHtml(format_details(el))

        def toggle_favorite(self):
            item = self.list.currentItem()
            if not item:
                QMessageBox.information(self, "No Selection", "Select an element first.")
                return
            el = item.data(32)
            symbol = el["symbol"]
            if symbol in self.favs:
                self.favs.remove(symbol)
            else:
                self.favs.add(symbol)
            save_favs(self.favs)
            self.update_list()

    dlg = ElementViewerDialog()
    dlg.exec()