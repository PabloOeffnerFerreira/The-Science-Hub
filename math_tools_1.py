from utils import register_window  # [AUTO-REFRACTORED]
import tkinter as tk
from tkinter import ttk
import sympy as sp
from utils import log_event

# 1. Quadratic Solver
def open_quadratic_solver(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Quadratic Solver")

        tk.Label(win, text="ax² + bx + c = 0").pack()
        a = tk.Entry(win)
        b = tk.Entry(win)
        c = tk.Entry(win)
        for entry, label in zip([a, b, c], ["a:", "b:", "c:"]):
            tk.Label(win, text=label).pack()
            entry.pack()

        if preload and isinstance(preload, tuple) and len(preload) == 3:
            a.insert(0, str(preload[0]))
            b.insert(0, str(preload[1]))
            c.insert(0, str(preload[2]))
            log_event("Quadratic Solver (Chain)", str(preload), "Waiting for solve")

        result = tk.Label(win, text="")
        result.pack(pady=5)

        def solve():
            try:
                A = float(a.get())
                B = float(b.get())
                C = float(c.get())
                x = sp.symbols('x')
                sol = sp.solve(A*x**2 + B*x + C, x)
                msg = f"Solutions: {sol}"
                result.config(text=msg)
                log_event("Quadratic Solver", f"a={A}, b={B}, c={C}", msg)
            except Exception:
                msg = "Invalid input."
                result.config(text=msg)
                log_event("Quadratic Solver", f"a={a.get()}, b={b.get()}, c={c.get()}", msg)

        tk.Button(win, text="Solve", command=solve).pack(pady=5)
        return win

    register_window("Quadratic Solver", create_window)


# 2. Function Plotter
def open_function_plotter(preload=None):
    def create_window():
        import matplotlib.pyplot as plt
        import numpy as np
        import os, datetime

        win = tk.Toplevel()
        win.title("Function Plotter")

        tk.Label(win, text="Enter function of x (e.g., x**2 + 3*x - 2):").pack()
        entry = tk.Entry(win, width=40)
        entry.pack(pady=5)

        if preload:
            entry.insert(0, preload)
            log_event("Function Plotter (Chain)", preload, "Waiting for plot")

        def plot():
            try:
                expr = entry.get()
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

                if not os.path.exists("results"):
                    os.makedirs("results")
                filename = f"results/graph_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
                fig.savefig(filename)
                plt.show()

                log_event("Function Plotter", expr, f"Plotted on x ∈ [-10, 10] [IMG:{filename}]")
            except Exception:
                msg = "Error parsing function"
                entry.delete(0, tk.END)
                entry.insert(0, msg)
                log_event("Function Plotter", entry.get(), msg)

        tk.Button(win, text="Plot", command=plot).pack(pady=5)
        return win

    register_window("Function Plotter", create_window)


# 3. Triangle Solver
def open_triangle_solver(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Triangle Side Solver (Pythagorean)")

        tk.Label(win, text="Leave the unknown side blank. a² + b² = c²").pack()
        a = tk.Entry(win)
        b = tk.Entry(win)
        c = tk.Entry(win)
        for entry, label in zip([a, b, c], ["a:", "b:", "c (hypotenuse):"]):
            tk.Label(win, text=label).pack()
            entry.pack()

        if preload and isinstance(preload, tuple) and len(preload) == 3:
            a.insert(0, str(preload[0]) if preload[0] is not None else "")
            b.insert(0, str(preload[1]) if preload[1] is not None else "")
            c.insert(0, str(preload[2]) if preload[2] is not None else "")
            log_event("Triangle Solver (Chain)", str(preload), "Waiting for solve")

        result = tk.Label(win, text="")
        result.pack(pady=5)

        def solve():
            try:
                A = a.get()
                B = b.get()
                C = c.get()
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
                result.config(text=msg)
                log_event("Triangle Solver", f"a={A}, b={B}, c={C}", msg)
            except Exception:
                msg = "Invalid input."
                result.config(text=msg)
                log_event("Triangle Solver", f"a={a.get()}, b={b.get()}, c={c.get()}", msg)

        tk.Button(win, text="Solve", command=solve).pack(pady=5)
        return win

    register_window("Triangle Solver", create_window)

#Open Math Tools

def open_math_tools_hub():
        def create_window():
            win = tk.Toplevel()
            win.title("Math Tools")
        
            tk.Label(win, text="Choose a Math Tool:").pack(pady=10)
            options = [
                "Quadratic Solver",
                "Function Plotter",
                "Triangle Side Solver"
            ]
            var = tk.StringVar()
            box = ttk.Combobox(win, textvariable=var, values=options, state="readonly")
            box.pack(pady=5)
            box.set("Select Tool")
        
            def launch():
                sel = var.get()
                if sel == "Quadratic Solver":
                    open_quadratic_solver()
                elif sel == "Function Plotter":
                    open_function_plotter()
                elif sel == "Triangle Side Solver":
                    open_triangle_solver()
        
            tk.Button(win, text="Open", command=launch).pack(pady=10)
            return win
        register_window(open_math_tools_hub.__name__.replace("open_", "").replace("_", " ").title(), create_window)