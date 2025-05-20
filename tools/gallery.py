import sys
import os
import json
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QListWidget, QListWidgetItem, QLabel, QPushButton, QFileDialog,
    QTextEdit, QDialog, QDialogButtonBox, QMessageBox, QCheckBox, QInputDialog
)
from PyQt6.QtGui import QPixmap, QIcon, QDragEnterEvent, QDropEvent, QFont
from PyQt6.QtCore import Qt, QMimeData, QSize
from tools.data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data, ai_chatlogs_dir, images_dir, screenshots_dir
)
GALLERY_DIR = gallery_dir
META_FILE = gallery_meta_path
IMPORT_FOLDERS = [images_dir, results_dir, screenshots_dir]

class MetadataManager:
    def __init__(self):
        os.makedirs(GALLERY_DIR, exist_ok=True)
        if not os.path.exists(META_FILE):
            with open(META_FILE, "w") as f:
                json.dump({}, f)
        with open(META_FILE, "r") as f:
            self.meta = json.load(f)

    def save(self):
        with open(META_FILE, "w") as f:
            json.dump(self.meta, f, indent=2)

    def get(self, filename):
        return self.meta.get(filename, {"tags": [], "favorite": False})

    def update(self, filename, key, value):
        self.meta.setdefault(filename, {})[key] = value
        self.save()

    def delete(self, filename):
        if filename in self.meta:
            del self.meta[filename]
            self.save()

    def rename(self, old, new):
        if old in self.meta:
            self.meta[new] = self.meta.pop(old)
            self.save()


class GalleryViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Science Hub Gallery")
        self.resize(1000, 650)
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: #1e1e1e; color: #dddddd;")

        self.meta = MetadataManager()

        layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or tag")
        self.search_input.setStyleSheet("background-color: #2a2a2a; color: #ffffff;")
        self.search_input.textChanged.connect(self.refresh_list)

        self.fav_filter = QCheckBox("Only favorites")
        self.fav_filter.setStyleSheet("color: #cccccc;")
        self.fav_filter.stateChanged.connect(self.refresh_list)

        self.add_button = QPushButton("Add Image")
        self.add_button.setStyleSheet("background-color: #444444; color: #ffffff;")
        self.add_button.clicked.connect(self.import_image)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.fav_filter)
        search_layout.addWidget(self.add_button)
        layout.addLayout(search_layout)

        self.drop_hint = QLabel("Drop images here")
        self.drop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_hint.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.drop_hint.setStyleSheet("color: #888888; padding: 10px;")
        layout.addWidget(self.drop_hint)

        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(128, 128))
        self.list_widget.setStyleSheet("background-color: #1e1e1e; color: #dddddd;")
        self.list_widget.itemClicked.connect(self.view_entry)
        layout.addWidget(self.list_widget)

        self.setLayout(layout)
        self.auto_import_from_folders()
        self.refresh_list()

    def auto_import_from_folders(self):
        for folder in IMPORT_FOLDERS:
            if not os.path.exists(folder):
                continue
            for fname in os.listdir(folder):
                if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                    src_path = os.path.join(folder, fname)
                    dest_path = os.path.join(GALLERY_DIR, fname)
                    if not os.path.exists(dest_path):
                        with open(src_path, "rb") as src_file, open(dest_path, "wb") as dst_file:
                            dst_file.write(src_file.read())

    def refresh_list(self):
        self.list_widget.clear()
        query = self.search_input.text().strip().lower()
        fav_only = self.fav_filter.isChecked()

        for fname in os.listdir(GALLERY_DIR):
            if not fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            info = self.meta.get(fname)
            tags = ", ".join(info.get("tags", []))
            fav = " ★" if info.get("favorite") else ""

            fulltext = f"{fname} {tags}".lower()
            if query in fulltext:
                if fav_only and not info.get("favorite"):
                    continue
                item = QListWidgetItem(f"{fname}{fav}\nTags: {tags}")
                item.setData(Qt.ItemDataRole.UserRole, fname)

                icon_path = os.path.join(GALLERY_DIR, fname)
                if os.path.exists(icon_path):
                    pixmap = QPixmap(icon_path)
                    if not pixmap.isNull():
                        icon = QIcon(pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                        item.setIcon(icon)

                self.list_widget.addItem(item)

    def view_entry(self, item):
        fname = item.data(Qt.ItemDataRole.UserRole)
        full_path = os.path.join(GALLERY_DIR, fname)

        dialog = QDialog(self)
        dialog.setWindowTitle(fname)
        dialog.resize(700, 600)
        dialog.setStyleSheet("background-color: #1e1e1e; color: #dddddd;")

        layout = QVBoxLayout()

        pixmap = QPixmap(full_path).scaledToWidth(600, Qt.TransformationMode.SmoothTransformation)
        img_label = QLabel()
        img_label.setPixmap(pixmap)
        layout.addWidget(img_label)

        tags_box = QTextEdit()
        tags_box.setPlainText(", ".join(self.meta.get(fname).get("tags", [])))
        layout.addWidget(QLabel("Tags (comma-separated):"))
        layout.addWidget(tags_box)

        fav_btn = QPushButton("Toggle Favorite")
        fav_btn.clicked.connect(lambda: self.toggle_fav(fname, dialog))
        layout.addWidget(fav_btn)

        rename_btn = QPushButton("Rename Entry")
        rename_btn.clicked.connect(lambda: self.rename_entry(fname, dialog))
        layout.addWidget(rename_btn)

        delete_btn = QPushButton("Delete Entry")
        delete_btn.clicked.connect(lambda: self.delete_entry(fname, dialog))
        layout.addWidget(delete_btn)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(lambda: self.save_tags(fname, tags_box.toPlainText(), dialog))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec()

    def rename_entry(self, fname, dialog):
        new_name, ok = QInputDialog.getText(self, "Rename", "Enter new filename:", text=fname)
        if ok and new_name:
            new_name = re.sub(r'[<>:"/\\|?*]', '', new_name).strip()
            if not new_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                QMessageBox.warning(self, "Invalid name", "Filename must end with .png, .jpg, or .jpeg")
                return
            if not new_name:
                QMessageBox.warning(self, "Invalid name", "Filename cannot be empty.")
                return
            src_path = os.path.join(GALLERY_DIR, fname)
            dest_path = os.path.join(GALLERY_DIR, new_name)
            if os.path.exists(dest_path):
                QMessageBox.warning(self, "File exists", f"'{new_name}' already exists.")
                return
            os.rename(src_path, dest_path)
            self.meta.rename(fname, new_name)
            self.refresh_list()
            dialog.accept()

    def save_tags(self, fname, tag_string, dialog):
        tags = [tag.strip() for tag in tag_string.split(',') if tag.strip()]
        self.meta.update(fname, "tags", tags)
        self.refresh_list()
        dialog.accept()

    def toggle_fav(self, fname, dialog):
        current = self.meta.get(fname).get("favorite", False)
        self.meta.update(fname, "favorite", not current)
        self.refresh_list()
        dialog.accept()

    def delete_entry(self, fname, dialog):
        full_path = os.path.join(GALLERY_DIR, fname)
        os.remove(full_path)
        self.meta.delete(fname)
        self.refresh_list()
        dialog.accept()

    def import_image(self):
        file_dialog = QFileDialog()
        paths, _ = file_dialog.getOpenFileNames(self, "Import Images", "", "Images (*.png *.jpg *.jpeg)")
        for path in paths:
            base_name = os.path.basename(path)
            dest = os.path.join(GALLERY_DIR, base_name)
            if os.path.exists(dest):
                continue
            with open(path, "rb") as src, open(dest, "wb") as dst:
                dst.write(src.read())
        self.refresh_list()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("background-color: #222222; color: #ffffff;")

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("background-color: #1e1e1e; color: #dddddd;")
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(('.png', '.jpg', '.jpeg')):
                base_name = os.path.basename(path)
                dest = os.path.join(GALLERY_DIR, base_name)
                if not os.path.exists(dest):
                    with open(path, "rb") as src, open(dest, "wb") as dst:
                        dst.write(src.read())
        self.refresh_list()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = GalleryViewer()
    viewer.show()
    sys.exit(app.exec())
