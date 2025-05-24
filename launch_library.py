import sys
from PyQt6.QtWidgets import QApplication
from library import LibraryViewer

def main():
    app = QApplication(sys.argv)
    win = LibraryViewer()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()