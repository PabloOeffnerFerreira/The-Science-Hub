from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import io, os, datetime, urllib.parse, urllib.request

from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')  # Hides ALL warnings, errors, and info from RDKit

from rdkit import Chem
from rdkit.Chem import Draw

from tools.data_utils import log_event, _open_dialogs
from tools.data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data, ai_chatlogs_dir
)

SMILES_URL_TEMPLATE = 'http://cactus.nci.nih.gov/chemical/structure/{}/smiles'

def iupac2smiles(iupac_name):
    quoted = urllib.parse.quote(iupac_name)
    url = SMILES_URL_TEMPLATE.format(quoted)
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.read().decode('utf-8')

def open_molecule_assembler():
    class MolAsmDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Molecule Assembler (RDKit)")
            self.setMinimumWidth(450)
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Enter SMILES or IUPAC name:"))
            self.entry = QLineEdit()
            layout.addWidget(self.entry)

            self.img_label = QLabel("No molecule drawn yet.")
            self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.img_label)

            self.draw_btn = QPushButton("Draw Molecule")
            self.save_btn = QPushButton("Save as PNG")
            self.save_btn.setEnabled(False)
            layout.addWidget(self.draw_btn)
            layout.addWidget(self.save_btn)

            self.draw_btn.clicked.connect(self.draw)
            self.save_btn.clicked.connect(self.save_png)
            self.current_img = None
            self.current_mol = None

        def draw(self):
            inp = self.entry.text().strip()
            if not inp:
                return
            mol = Chem.MolFromSmiles(inp)
            if mol is None:
                try:
                    smiles = iupac2smiles(inp)
                    mol = Chem.MolFromSmiles(smiles)
                    if mol is None:
                        self.img_label.setText("Could not parse molecule.")
                        self.save_btn.setEnabled(False)
                        return
                except Exception as e:
                    self.img_label.setText(f"Error retrieving SMILES: {e}")
                    self.save_btn.setEnabled(False)
                    return
            Chem.rdDepictor.Compute2DCoords(mol)
            img = Draw.MolToImage(mol, size=(400, 400))
            data = io.BytesIO()
            img.save(data, format='PNG')
            data.seek(0)
            pixmap = QPixmap()
            pixmap.loadFromData(data.read())
            self.img_label.setPixmap(pixmap)
            self.current_img = img
            self.current_mol = mol
            self.save_btn.setEnabled(True)
            log_event("Molecule Assembler", inp, "Molecule drawn.")

        def save_png(self):
            if self.current_img is None:
                QMessageBox.warning(self, "No molecule", "Draw a molecule first!")
                return
            if not os.path.exists("results"):
                os.makedirs("results")
            name = self.entry.text().strip() or "molecule"
            fname = f"results/{name.replace(' ','_')}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
            self.current_img.save(fname)
            QMessageBox.information(self, "Image saved", f"Saved to: {fname}")
            log_event("Molecule Assembler", name, f"Saved image {fname}")

    dlg = MolAsmDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
