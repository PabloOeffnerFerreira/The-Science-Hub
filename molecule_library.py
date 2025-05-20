import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QTextBrowser, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data, ai_chatlogs_dir
)


class MoleculeLibrary(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Molecule Library (PubChem)")
        self.resize(800, 500)
        self.setStyleSheet("background-color: #1e1e1e; color: #dddddd;")

        layout = QVBoxLayout()

        # Search bar
        search_layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter molecule name, e.g. aspirin")
        self.input.setStyleSheet("background-color: #2a2a2a; color: #ffffff;")
        search_layout.addWidget(self.input)

        self.search_btn = QPushButton("Search")
        self.search_btn.setStyleSheet("background-color: #444444; color: #ffffff;")
        self.search_btn.clicked.connect(self.search_pubchem)
        search_layout.addWidget(self.search_btn)

        layout.addLayout(search_layout)

        # Output area
        self.viewer = QTextBrowser()
        self.viewer.setOpenExternalLinks(True)
        self.viewer.setStyleSheet("background-color: #121212; color: #dddddd; font-family: Consolas;")
        layout.addWidget(self.viewer)

        self.setLayout(layout)

    def search_pubchem(self):
        name = self.input.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Required", "Please enter a molecule name.")
            return

        self.viewer.setText("Searching PubChem...")

        try:
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/JSON"
            r = requests.get(url)
            data = r.json()

            props = data["PC_Compounds"][0]["props"]
            results = {p['urn']['label']: p.get('value', {}).get('sval') or p.get('value', {}).get('fval')
                       for p in props if 'value' in p and 'urn' in p and 'label' in p['urn']}

            cid = data['PC_Compounds'][0]['id']['id']['cid']
            compound_url = f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"

            lines = [f"<b>Molecule:</b> {name.title()}<br><b>CID:</b> {cid}<br>", f"<b>Link:</b> <a href='{compound_url}'>{compound_url}</a><br><hr>"]

            for label, val in results.items():
                lines.append(f"<b>{label}:</b> {val}<br>")

            self.viewer.setHtml("".join(lines))

        except Exception as e:
            self.viewer.setText(f"Error retrieving data: {str(e)}")


if __name__ == "__main__":
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = MoleculeLibrary()
    window.show()
    if not QApplication.instance().startingUp():  # prevents redundant exec()
        sys.exit(app.exec())