import os
import datetime
import numpy as np
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QMessageBox, QSizePolicy
)
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from data_utils import log_event, results_dir, _open_dialogs  # your project utilities

def open_magnoline_tool():
    class MagnolineTool(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Magnoline Tool")
            self.setMinimumSize(600, 500)

            self.magnets = []  # list of (x, y, strength)

            self.main_layout = QVBoxLayout(self)

            # Input rows for magnet properties
            self.inputs = []
            def make_input_row(label_text, placeholder=""):
                row = QHBoxLayout()
                label = QLabel(label_text)
                line_edit = QLineEdit()
                line_edit.setPlaceholderText(placeholder)
                regex = QRegularExpression(r"[-+]?[0-9]*\.?[0-9]+")
                validator = QRegularExpressionValidator(regex)
                line_edit.setValidator(validator)
                row.addWidget(label)
                row.addWidget(line_edit)
                self.main_layout.addLayout(row)
                self.inputs.append(line_edit)
                return line_edit

            self.x_edit = make_input_row("X coordinate:", "e.g. 0")
            self.y_edit = make_input_row("Y coordinate:", "e.g. 0")
            self.strength_edit = make_input_row("Strength:", "e.g. 1 (positive or negative)")

            # Buttons
            btn_layout = QHBoxLayout()
            self.add_btn = QPushButton("Add Magnet")
            self.add_btn.clicked.connect(self.add_magnet)
            btn_layout.addWidget(self.add_btn)

            self.clear_btn = QPushButton("Clear Magnets")
            self.clear_btn.clicked.connect(self.clear_magnets)
            btn_layout.addWidget(self.clear_btn)

            self.calc_btn = QPushButton("Draw Field Lines")
            self.calc_btn.clicked.connect(self.draw_field)
            btn_layout.addWidget(self.calc_btn)

            self.main_layout.addLayout(btn_layout)

            # List to show magnets
            self.magnet_list = QListWidget()
            self.main_layout.addWidget(self.magnet_list)

            # Result label
            self.result_label = QLabel("")
            self.result_label.setWordWrap(True)
            self.main_layout.addWidget(self.result_label)

            # Matplotlib canvas
            self.figure = Figure(figsize=(5, 4))
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.main_layout.addWidget(self.canvas)

        def add_magnet(self):
            try:
                x = float(self.x_edit.text())
                y = float(self.y_edit.text())
                strength = float(self.strength_edit.text())
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Please enter valid numeric values for X, Y, and Strength.")
                return

            self.magnets.append((x, y, strength))
            self.magnet_list.addItem(f"Magnet at ({x}, {y}), strength {strength}")
            self.clear_inputs()
            self.result_label.setText(f"{len(self.magnets)} magnet(s) defined.")
            log_event("Magnoline Tool", "Add Magnet", f"Added magnet at ({x}, {y}) with strength {strength}")

        def clear_inputs(self):
            for edit in self.inputs:
                edit.clear()

        def clear_magnets(self):
            count = len(self.magnets)
            self.magnets.clear()
            self.magnet_list.clear()
            self.result_label.setText("Cleared all magnets.")
            self.figure.clear()
            self.canvas.draw()
            log_event("Magnoline Tool", "Clear Magnets", f"Cleared {count} magnets")

        def draw_field(self):
            if not self.magnets:
                QMessageBox.warning(self, "No Magnets", "Add at least one magnet before drawing.")
                return

            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.set_title("Magnetic Field Lines")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")

            grid_size = 50
            margin = 5
            xs = np.linspace(-margin, margin, grid_size)
            ys = np.linspace(-margin, margin, grid_size)
            X, Y = np.meshgrid(xs, ys)

            Bx = np.zeros_like(X)
            By = np.zeros_like(Y)

            for (mx, my, strength) in self.magnets:
                dx = X - mx
                dy = Y - my
                r_squared = dx**2 + dy**2
                r_squared[r_squared == 0] = 1e-12
                r_five = r_squared ** 2.5  # r^5

                Bx += -3 * strength * dx * dy / r_five
                By += strength * (2 * dy**2 - dx**2) / r_five

            magnitude = np.sqrt(Bx**2 + By**2)
            nonzero = magnitude > 1e-12
            Bx[nonzero] /= magnitude[nonzero]
            By[nonzero] /= magnitude[nonzero]

            ax.streamplot(X, Y, Bx, By, color='b', density=1.5, linewidth=0.7, arrowsize=1)

            for (mx, my, strength) in self.magnets:
                color = 'red' if strength > 0 else 'blue'
                ax.plot(mx, my, 'o', color=color, markersize=8)
                ax.text(mx, my, f"{strength:+.2f}", color=color, fontsize=9, ha='center', va='center')

            ax.set_aspect('equal', 'box')
            ax.set_xlim(-margin, margin)
            ax.set_ylim(-margin, margin)
            ax.grid(True)

            self.canvas.draw()

            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"magnoline_field_{timestamp}.png"
            filepath = os.path.join(results_dir, filename)
            self.figure.savefig(filepath, dpi=150)

            self.result_label.setText(f"Drew field for {len(self.magnets)} magnet(s). Plot saved to:\n{filepath}")
            log_event("Magnoline Tool", "Draw Field", f"Drew field with {len(self.magnets)} magnets. Plot saved: {filepath}")

    dlg = MagnolineTool()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
