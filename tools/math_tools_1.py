from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
import sympy as sp
from tools.data_utils import log_event, _open_dialogs
import matplotlib.pyplot as plt
import numpy as np
import os
import datetime
from tools.data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data, ai_chatlogs_dir
)

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

# Algebric Calculator

def open_algebric_calc():
    class AlgDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Algebric Calculator")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Enter function of x (e.g., x**2 + 3*x - 2):"))
            self.func_input = QLineEdit()
            layout.addWidget(self.func_input)
            layout.addWidget(QLabel("Enter the Value of X"))
            self.x_input = QLineEdit()
            layout.addWidget(self.x_input)
            btn = QPushButton("Calculate")
            btn.clicked.connect(self.calculate)
            layout.addWidget(btn)
            self.result = QLabel()
            layout.addWidget(self.result)
            self.setMinimumWidth(350)
        def calculate(self):
            user_input = self.func_input.text()
            user_x_input = self.x_input.text()
            try:
                expr = sp.sympify(user_input)
                x = sp.Symbol('x')
                value = float(user_x_input)
                result = expr.subs(x, value).evalf(4)
                if result == int(result):
                    msg = f"f({value}) = {int(result)}"
                else:
                    msg = f"f({value}) = {result.evalf(4)}"
                self.result.setText(msg)
                log_event("Algebric Calculator", expr, msg)
            except Exception:
                msg = "Error with the function"
                self.result.setText(msg)
                log_event("Algebric Calculator", self.func_input.text(), msg)
    dlg = AlgDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

def open_scinot_converter():
    class SciNotDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Scientific Notation Converter")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Enter Decimal Number"))
            self.decimal_input = QLineEdit()
            layout.addWidget(self.decimal_input)
            layout.addWidget(QLabel("Enter Scientific Notation"))
            self.sci_input = QLineEdit()
            layout.addWidget(self.sci_input)
            btn = QPushButton("Convert")
            btn.clicked.connect(self.convert)
            layout.addWidget(btn)
            self.result = QLabel()
            layout.addWidget(self.result)
            self.setMinimumWidth(350)
        def convert(self):
            dec = self.decimal_input.text().strip()
            sci = self.sci_input.text().strip()

            if dec and not sci:
                try:
                    number = float(dec)
                    result = f"{number:.4e}"
                    msg = result
                    self.result.setText(result)
                    log_event("Scientific Notation Converter", f"dec={dec}, sci={sci}", msg)
                except Exception:
                    msg = "Invalid decimal number"
                    self.result.setText(msg)
                    log_event("Scientific Notation Converter", f"dec={dec}, sci={sci}", msg)
            elif sci and not dec:
                try:
                    number = float(sci)
                    result = str(number)
                    msg = result
                    self.result.setText(result)
                    log_event("Scientific Notation Converter", f"dec={dec}, sci={sci}", msg)
                except Exception:
                    msg = "Invalid scientific notation"
                    self.result.setText(msg)
                    log_event("Scientific Notation Converter", f"dec={dec}, sci={sci}", msg)
            elif dec and sci:
                msg = "Enter only one number"
                self.result.setText(msg)
                log_event("Scientific Notation Converter", f"dec={dec}, sci={sci}", msg)
            else:
                msg = "You must enter a number"
                self.result.setText(msg)
                log_event("Scientific Notation Converter", f"dec={dec}, sci={sci}", msg)

    dlg = SciNotDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

def open_vector_calculator():
    class VectorCalc(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Vector Calculator")
            layout = QVBoxLayout(self)
            self.operation_select = QComboBox()
            self.operation_select.addItems([
                "Dot Product",
                "Cross Product",
                "Angle Between",
                "Magnitude of A",
                "Magnitude of B",
                "Normalize A",
                "Normalize B"
            ])
            layout.addWidget(self.operation_select)
            layout.addWidget(QLabel("Vector A, coordinates seperated by commas"))
            self.vector_a_input = QLineEdit()
            layout.addWidget(self.vector_a_input)
            layout.addWidget(QLabel("Vector B, coordinates seperated by commas"))
            self.vector_b_input = QLineEdit()
            layout.addWidget(self.vector_b_input)
            btn = QPushButton("Calculate")
            btn.clicked.connect(self.calculate)
            layout.addWidget(btn)
            self.result = QLabel()
            layout.addWidget(self.result)
            self.setMinimumWidth(350)
        def calculate(self):
            try:
                from tools.data_utils import load_settings  # ensures settings can be read
                settings = load_settings()

                A = self.parse_vector(self.vector_a_input.text())
                B = self.parse_vector(self.vector_b_input.text())
                operation = self.operation_select.currentText()
                result = None  # holds scalar or vector result

                if operation == "Dot Product":
                    result = float(np.dot(A, B))
                    self.result.setText(f"Result: {result:.4f}")

                elif operation == "Cross Product":
                    if A.size == 3 and B.size == 3:
                        result = np.cross(A, B)
                        vec = ", ".join(f"{v:.2f}" for v in result)
                        self.result.setText(f"Result: [{vec}]")
                    else:
                        raise ValueError("Cross product only works for 3D vectors.")

                elif operation == "Angle Between":
                    cos_theta = np.dot(A, B) / (np.linalg.norm(A) * np.linalg.norm(B))
                    angle_rad = np.arccos(np.clip(cos_theta, -1.0, 1.0))
                    angle_deg = np.degrees(angle_rad)
                    result = angle_deg
                    self.result.setText(f"Angle: {angle_deg:.2f}°")

                elif operation == "Magnitude of A":
                    result = np.linalg.norm(A)
                    self.result.setText(f"Magnitude of A: {result:.4f}")

                elif operation == "Magnitude of B":
                    result = np.linalg.norm(B)
                    self.result.setText(f"Magnitude of B: {result:.4f}")

                elif operation == "Normalize A":
                    norm = np.linalg.norm(A)
                    if norm == 0:
                        raise ValueError("Cannot normalize a zero vector.")
                    result = A / norm
                    vec = ", ".join(f"{v:.2f}" for v in result)
                    self.result.setText(f"Normalized A: [{vec}]")

                elif operation == "Normalize B":
                    norm = np.linalg.norm(B)
                    if norm == 0:
                        raise ValueError("Cannot normalize a zero vector.")
                    result = B / norm
                    vec = ", ".join(f"{v:.2f}" for v in result)
                    self.result.setText(f"Normalized B: [{vec}]")

                # Optional plotting
                if settings.get("plot_vectors_3d", False):
                    if A.size == 3 and B.size == 3:
                        # Only plot the result vector if it's a 3D vector (e.g., cross product or normalized vector)
                        img_path = self.plot_vectors(A, B, result if isinstance(result, np.ndarray) and result.shape == (3,) else None)
                input_str = f"A={A.tolist()}, B={B.tolist()}, op={operation}"

                if isinstance(result, (int, float, np.float64, np.float32)):
                    msg = f"{result:.4f}"
                elif isinstance(result, np.ndarray):
                    msg = "[" + ", ".join(f"{v:.2f}" for v in result) + "]"
                else:
                    msg = str(result)
                msg_log = msg
                if 'img_path' in locals():
                    msg_log += f" [IMG:{img_path}]"
                log_event("Vector Calculator", input_str, msg_log)

                log_event("Vector Calculator", input_str, msg + f" [IMG:{img_path}]")
            except Exception as e:
                self.result.setText(f"Error: {e}")

            
        def parse_vector(self,text):
            parts = text.split(",")
            return np.array([float(x.strip()) for x in parts])  
        def plot_vectors(self, A, B, R=None):
            from mpl_toolkits.mplot3d import Axes3D
            import matplotlib.pyplot as plt
            import numpy as np

            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

            ax.quiver(0, 0, 0, A[0], A[1], A[2], color='blue', label='A')
            ax.quiver(0, 0, 0, B[0], B[1], B[2], color='green', label='B')

            if R is not None and isinstance(R, np.ndarray) and R.shape == (3,):
                ax.quiver(0, 0, 0, R[0], R[1], R[2], color='red', label='Result')

            ax.set_xlim([-10, 10])
            ax.set_ylim([-10, 10])
            ax.set_zlim([-10, 10])
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")
            ax.legend()
            ax.set_title("3D Vector Visualization")
            plt.show(block=False)
            if A.size != 3 or B.size != 3:
                return  # Skip plotting for non-3D vectors
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            img_path = os.path.join(results_dir, f"vector_plot_{timestamp}.png")
            plt.savefig(img_path, dpi=150)
            return img_path

    dlg = VectorCalc()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))