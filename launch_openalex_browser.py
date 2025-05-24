import sys
from PyQt6.QtWidgets import QApplication
from openalex_browser import OpenAlexBrowser  # change class name as needed

def main():
    app = QApplication(sys.argv)
    win = OpenAlexBrowser()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
