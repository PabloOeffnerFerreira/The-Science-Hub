import sys
from PyQt6.QtWidgets import QApplication
from gallery import GalleryViewer  # replace with your class name if different

def main():
    app = QApplication(sys.argv)
    win = GalleryViewer()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
