import sys
from PyQt6.QtWidgets import QApplication
from molecule_library import MoleculeLibrary  # adjust class name as needed

def main():
    app = QApplication(sys.argv)
    win = MoleculeLibrary()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
