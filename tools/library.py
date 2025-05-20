
import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QLabel, QCheckBox, QComboBox, QDialog, QTextEdit,
    QDialogButtonBox, QFileDialog, QMessageBox, QScrollArea, QGridLayout
)
from PyQt6.QtGui import QIcon, QPixmap, QFont
from PyQt6.QtCore import Qt, QSize
from tools.utilities import (
    gallery_dir, exports_dir, library_file
)

LIBRARY_FILE = library_file
GALLERY_DIR = gallery_dir

class LibraryData:
    def __init__(self):
        if not os.path.exists(LIBRARY_FILE):
            with open(LIBRARY_FILE, "w") as f:
                json.dump([], f)
        with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
            self.entries = json.load(f)

    def save(self):
        with open(LIBRARY_FILE, "w") as f:
            json.dump(self.entries, f, indent=2)

    def add_or_update_entry(self, entry):
        for i, e in enumerate(self.entries):
            if e["title"].lower() == entry["title"].lower():
                self.entries[i] = entry
                self.save()
                return
        self.entries.append(entry)
        self.save()

    def delete_entry(self, title):
        self.entries = [e for e in self.entries if e["title"].lower() != title.lower()]
        self.save()

    def get(self):
        return self.entries


class GalleryPicker(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select from Gallery")
        self.setStyleSheet("background-color: #1e1e1e; color: #dddddd;")
        self.resize(600, 500)
        layout = QVBoxLayout()
        self.setLayout(layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll.setWidget(scroll_widget)
        grid = QGridLayout()
        scroll_widget.setLayout(grid)

        layout.addWidget(scroll)

        self.selected_path = None

        row = 0
        col = 0
        for fname in os.listdir(GALLERY_DIR):
            if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(GALLERY_DIR, fname)
                pixmap = QPixmap(path).scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                btn = QPushButton()
                btn.setIcon(QIcon(pixmap))
                btn.setIconSize(QSize(128, 128))
                btn.clicked.connect(lambda _, p=path: self.select(p))
                grid.addWidget(btn, row, col)
                col += 1
                if col >= 4:
                    col = 0
                    row += 1

    def select(self, path):
        self.selected_path = path
        self.accept()


class EntryEditor(QDialog):
    def __init__(self, parent, entry=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Entry" if entry else "Add Entry")
        self.setStyleSheet("background-color: #1e1e1e; color: #dddddd;")
        self.resize(500, 600)
        self.entry = entry or {}

        layout = QVBoxLayout()

        self.title_input = QLineEdit(self.entry.get("title", ""))
        layout.addWidget(QLabel("Title:"))
        layout.addWidget(self.title_input)

        self.formula_input = QLineEdit(self.entry.get("formula", ""))
        layout.addWidget(QLabel("Formula:"))
        layout.addWidget(self.formula_input)

        self.tags_input = QLineEdit(", ".join(self.entry.get("tags", [])))
        layout.addWidget(QLabel("Tags (comma-separated):"))
        layout.addWidget(self.tags_input)

        self.desc_input = QTextEdit(self.entry.get("description", ""))
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.desc_input)

        self.fav_check = QCheckBox("Favorite")
        self.fav_check.setChecked(self.entry.get("favorite", False))
        layout.addWidget(self.fav_check)

        self.img_path = self.entry.get("image", "")
        self.img_label = QLabel(f"Image: {os.path.basename(self.img_path)}" if self.img_path else "No image")
        layout.addWidget(self.img_label)

        pick_img_btn = QPushButton("Pick Image from Gallery")
        pick_img_btn.clicked.connect(self.pick_from_gallery)
        layout.addWidget(pick_img_btn)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def pick_from_gallery(self):
        picker = GalleryPicker(self)
        if picker.exec() and picker.selected_path:
            self.img_path = picker.selected_path
            self.img_label.setText(f"Image: {os.path.basename(self.img_path)}")

    def get_entry(self):
        return {
            "title": self.title_input.text().strip(),
            "formula": self.formula_input.text().strip(),
            "tags": [tag.strip() for tag in self.tags_input.text().split(",") if tag.strip()],
            "description": self.desc_input.toPlainText().strip(),
            "favorite": self.fav_check.isChecked(),
            "image": self.img_path
        }


class EntryViewer(QDialog):
    def __init__(self, parent, entry):
        super().__init__(parent)
        self.setWindowTitle(entry["title"])
        self.setStyleSheet("background-color: #1e1e1e; color: #dddddd;")
        self.resize(600, 700)
        self.entry = entry

        layout = QVBoxLayout()

        title_label = QLabel(f"Title: {entry['title']}")
        title_label.setFont(QFont("Noto Sans Symbols", 10))
        layout.addWidget(title_label)

        formula_label = QLabel(f"Formula: {entry['formula']}")
        formula_label.setFont(QFont("Noto Sans Symbols", 10))
        layout.addWidget(formula_label)

        tags_label = QLabel(f"Tags: {', '.join(entry.get('tags', []))}")
        tags_label.setFont(QFont("Segoe UI", 9))  # Regular font is fine for tags
        layout.addWidget(tags_label)

        layout.addWidget(QLabel("Description:"))
        desc = QTextEdit(entry.get("description", ""))
        desc.setReadOnly(True)
        desc.setFont(QFont("Noto Sans Symbols", 10))
        layout.addWidget(desc)

        if entry.get("image") and os.path.exists(entry["image"]):
            img = QPixmap(entry["image"])
            if not img.isNull():
                img_lbl = QLabel()
                img_lbl.setPixmap(img.scaledToWidth(500, Qt.TransformationMode.SmoothTransformation))
                layout.addWidget(QLabel("Image:"))
                layout.addWidget(img_lbl)

        export_btn = QPushButton("Export to JSON")
        export_btn.clicked.connect(self.export_entry)
        layout.addWidget(export_btn)

        close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn.rejected.connect(self.reject)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    from utilities import exports_dir  # Make sure this is imported!

    def export_entry(self):
        import os
        default_name = f"{self.entry['title']}.json"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Entry",
            os.path.join(exports_dir, default_name),  # Start in the exports folder!
            "JSON Files (*.json)"
        )
        if path:
            with open(path, "w") as f:
                json.dump(self.entry, f, indent=2)
            QMessageBox.information(self, "Exported", "Entry exported successfully.")



class LibraryViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Science Library")
        self.setStyleSheet("background-color: #1e1e1e; color: #dddddd;")
        self.resize(1000, 700)

        self.data = LibraryData()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        controls = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title or tag")
        self.search_input.textChanged.connect(self.refresh)

        self.fav_check = QCheckBox("Only favorites")
        self.fav_check.stateChanged.connect(self.refresh)

        self.sort_mode = QComboBox()
        self.sort_mode.addItems(["Title", "Tags"])
        self.sort_mode.currentTextChanged.connect(self.refresh)

        add_btn = QPushButton("Add Entry")
        add_btn.clicked.connect(self.add_entry)

        controls.addWidget(self.search_input)
        controls.addWidget(self.fav_check)
        controls.addWidget(self.sort_mode)
        controls.addWidget(add_btn)
        self.layout.addLayout(controls)

        self.list = QListWidget()
        self.list.itemClicked.connect(self.view_entry)
        self.layout.addWidget(self.list)

        self.refresh()

    def refresh(self):
        self.list.clear()
        entries = self.data.get()
        query = self.search_input.text().lower()
        fav_only = self.fav_check.isChecked()
        sort_key = "title" if self.sort_mode.currentText() == "Title" else "tags"

        filtered = []
        for e in entries:
            fulltext = f"{e['title']} {' '.join(e.get('tags', []))}".lower()
            if query in fulltext and (not fav_only or e.get("favorite", False)):
                filtered.append(e)

        filtered.sort(key=lambda e: e.get(sort_key, "") or "")

        for entry in filtered:
            item = QListWidgetItem(f"{entry['title']} ({', '.join(entry.get('tags', []))})")
            if entry.get("favorite"):
                item.setText(f"★ {item.text()}")
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.list.addItem(item)

    def view_entry(self, item):
        QFont("Noto Sans Symbols", 10)
        entry = item.data(Qt.ItemDataRole.UserRole)
        dlg = EntryViewer(self, entry)
        dlg.exec()

    def add_entry(self):
        dlg = EntryEditor(self)
        if dlg.exec():
            entry = dlg.get_entry()
            if not entry["title"]:
                QMessageBox.warning(self, "Missing Title", "Entry must have a title.")
                return
            self.data.add_or_update_entry(entry)
            self.refresh()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = LibraryViewer()
    viewer.show()
    sys.exit(app.exec())