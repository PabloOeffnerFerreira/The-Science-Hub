import sys
import types

# Create dummy PyQt6 modules to satisfy imports in utilities
qtwidgets = types.ModuleType("PyQt6.QtWidgets")
qtcore = types.ModuleType("PyQt6.QtCore")
# Define minimal attributes used in utilities
for attr in [
    "QDialog", "QVBoxLayout", "QHBoxLayout", "QLabel", "QPushButton",
    "QLineEdit", "QTextEdit", "QMessageBox", "QWidget", "QTableWidget",
    "QTableWidgetItem", "QFrame", "QCheckBox", "QApplication",
    "QListWidget", "QListWidgetItem", "QComboBox",
]:
    setattr(qtwidgets, attr, object)
for attr in ["Qt", "QTimer"]:
    setattr(qtcore, attr, object)

sys.modules.setdefault("PyQt6", types.ModuleType("PyQt6"))
sys.modules["PyQt6.QtWidgets"] = qtwidgets
sys.modules["PyQt6.QtCore"] = qtcore

from data_utils import parse_formula


def test_simple_formula():
    assert parse_formula("H2O") == {"H": 2, "O": 1}


def test_nested_formula():
    expected = {"Fe": 2, "S": 3, "O": 12}
    assert parse_formula("Fe2(SO4)3") == expected
