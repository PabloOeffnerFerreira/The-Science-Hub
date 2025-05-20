from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
import sympy as sp
from tools.data_utils import log_event, _open_dialogs
import matplotlib.pyplot as plt
import numpy as np
import os
import datetime
from tools.utilities import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path
)

# Quadratic Solver
def open_quadratic_solver():
    class QuadDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Quadratic Solver")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("ax² + bx + c = 0"))
            self.a = QLineEdit()
            self.b = QLineEdit()
            self.c = QLineEdit()
            for entry, label in zip([self.a, self.b, self.c], ["a:", "b:", "c:"]):
                row = QHBoxLayout()
                row.addWidget(QLabel(label))
                row.addWidget(entry)
                layout.addLayout(row)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Solve")
            btn.clicked.connect(self.solve)
            layout.addWidget(btn)
            self.setMinimumWidth(300)
        def solve(self):
            try:
                A = float(self.a.text())
                B = float(self.b.text())
                C = float(self.c.text())
                x = sp.symbols('x')
                sol = sp.solve(A*x**2 + B*x + C, x)
                msg = f"Solutions: {sol}"
                self.result.setText(msg)
                log_event("Quadratic Solver", f"a={A}, b={B}, c={C}", msg)
            except Exception:
                msg = "Invalid input."
                self.result.setText(msg)
                log_event("Quadratic Solver", f"a={self.a.text()}, b={self.b.text()}, c={self.c.text()}", msg)
    dlg = QuadDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

# Function Plotter
def open_function_plotter():
    class PlotDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Function Plotter")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Enter function of x (e.g., x**2 + 3*x - 2):"))
            self.entry = QLineEdit()
            layout.addWidget(self.entry)
            btn = QPushButton("Plot")
            btn.clicked.connect(self.plot)
            layout.addWidget(btn)
            self.setMinimumWidth(350)
        def plot(self):
            try:
                expr = self.entry.text()
                x = sp.symbols('x')
                f = sp.lambdify(x, sp.sympify(expr), "numpy")
                xs = np.linspace(-10, 10, 400)
                ys = f(xs)
                fig, ax = plt.subplots()
                ax.plot(xs, ys)
                ax.set_title(f"y = {expr}")
                ax.set_xlabel("x")
                ax.set_ylabel("y")
                ax.grid(True)
                fig.tight_layout()

                if not os.path.exists(results_dir):
                    os.makedirs(results_dir)
                filename = f"graph_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
                fig.savefig(filename)
                plt.show()
                msg = f"Plotted on x ∈ [-10, 10] [IMG:{filename}]"
                log_event("Function Plotter", expr, msg)
            except Exception:
                msg = "Error parsing function"
                self.entry.setText(msg)
                log_event("Function Plotter", self.entry.text(), msg)
    dlg = PlotDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

# Triangle Solver
def open_triangle_solver():
    class TriDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Triangle Side Solver (Pythagorean)")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Leave the unknown side blank. a² + b² = c²"))
            self.a = QLineEdit()
            self.b = QLineEdit()
            self.c = QLineEdit()
            for entry, label in zip([self.a, self.b, self.c], ["a:", "b:", "c (hypotenuse):"]):
                row = QHBoxLayout()
                row.addWidget(QLabel(label))
                row.addWidget(entry)
                layout.addLayout(row)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Solve")
            btn.clicked.connect(self.solve)
            layout.addWidget(btn)
            self.setMinimumWidth(300)
        def solve(self):
            try:
                A = self.a.text()
                B = self.b.text()
                C = self.c.text()
                if C == '':
                    value = (float(A)**2 + float(B)**2)**0.5
                    msg = f"c = {value:.2f}"
                elif A == '':
                    value = (float(C)**2 - float(B)**2)**0.5
                    msg = f"a = {value:.2f}"
                elif B == '':
                    value = (float(C)**2 - float(A)**2)**0.5
                    msg = f"b = {value:.2f}"
                else:
                    msg = "Leave one field blank"
                self.result.setText(msg)
                log_event("Triangle Solver", f"a={A}, b={B}, c={C}", msg)
            except Exception:
                msg = "Invalid input."
                self.result.setText(msg)
                log_event("Triangle Solver", f"a={self.a.text()}, b={self.b.text()}, c={self.c.text()}", msg)
    dlg = TriDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
