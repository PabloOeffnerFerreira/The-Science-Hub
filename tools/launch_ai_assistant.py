import sys
from PyQt6.QtWidgets import QApplication
from tools.ai_assistant import AIAssistantWindow
from tools.data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data, ai_chatlogs_dir
)

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