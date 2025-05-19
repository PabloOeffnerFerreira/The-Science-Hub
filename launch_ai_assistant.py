<<<<<<< HEAD
# launch_ai_assistant.py

import sys
from PyQt6.QtWidgets import QApplication
from ai_assistant import AIAssistantWindow

def launch_with_args():
    # Parse command-line arguments
    model = sys.argv[1] if len(sys.argv) > 1 else "dolphin3:8b"
    mode_map = {"learn": 0, "use": 1, "casual": 2}
    mode = mode_map.get(sys.argv[2], 2) if len(sys.argv) > 2 else 2

    app = QApplication(sys.argv)
    win = AIAssistantWindow()
    win.model_picker.setCurrentText(model)
    win.mode_selector.setCurrentIndex(mode)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    launch_with_args()
=======
# launch_ai_assistant.py

import sys
from PyQt6.QtWidgets import QApplication
from ai_assistant import AIAssistantWindow

def launch_with_args():
    # Parse command-line arguments
    model = sys.argv[1] if len(sys.argv) > 1 else "dolphin3:8b"
    mode_map = {"learn": 0, "use": 1, "casual": 2}
    mode = mode_map.get(sys.argv[2], 2) if len(sys.argv) > 2 else 2

    app = QApplication(sys.argv)
    win = AIAssistantWindow()
    win.model_picker.setCurrentText(model)
    win.mode_selector.setCurrentIndex(mode)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    launch_with_args()
>>>>>>> 5896feb1d2c409629c464efb94cc07fa25f91bbc
