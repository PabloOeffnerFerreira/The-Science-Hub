import tkinter as tk
from tkinter import ttk, messagebox
import gempy as gp
import numpy as np
import pandas as pd

# Optional: For advanced 2D/3D visualization (see note at end)
try:
    import gempy_viewer as gpv  # The official GemPy 3 plotting library
except ImportError:
    gpv = None
from tools.utilities import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path
)

class GeoModelTool:
    """
    Interactive GUI tool for building a simple geological model using GemPy 3.x.
    The user can define layers (name, thickness, color) and generate a basic block model.
    Surface points are assigned at the base of each layer. At least two layers are required.
    """

    def __init__(self, master):
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.title("Geology Model Tool")
        self.window.geometry("600x550")

        self.layers = []  # Each entry: (name, thickness, color)
        self.setup_ui()

    def setup_ui(self):
        top = tk.Frame(self.window)
        top.pack(pady=10)
        tk.Label(top, text="Define Geological Layers").pack()

        entry_row = tk.Frame(self.window)
        entry_row.pack()
        self.name_var = tk.StringVar()
        self.thickness_var = tk.DoubleVar()
        self.color_var = tk.StringVar(value="#FFD700")
        tk.Label(entry_row, text="Name:").pack(side="left")
        tk.Entry(entry_row, textvariable=self.name_var, width=12).pack(side="left", padx=5)
        tk.Label(entry_row, text="Thickness:").pack(side="left")
        tk.Entry(entry_row, textvariable=self.thickness_var, width=7).pack(side="left", padx=5)
        tk.Label(entry_row, text="Color (hex):").pack(side="left")
        tk.Entry(entry_row, textvariable=self.color_var, width=9).pack(side="left", padx=5)
        tk.Button(entry_row, text="Add Layer", command=self.add_layer).pack(side="left", padx=10)

        self.layers_listbox = tk.Listbox(self.window, height=8, width=50)
        self.layers_listbox.pack(pady=8)
        tk.Button(self.window, text="Remove Selected Layer", command=self.remove_layer).pack(pady=2)
        tk.Button(self.window, text="Generate Model", command=self.generate_model).pack(pady=15)

    def add_layer(self):
        name = self.name_var.get().strip()
        try:
            thickness = float(self.thickness_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid thickness value.")
            return
        color = self.color_var.get().strip() or "#FFD700"
        if not name or thickness <= 0:
            messagebox.showerror("Error", "Layer name and thickness required.")
            return
        self.layers.append((name, thickness, color))
        self.refresh_layers()

    def remove_layer(self):
        sel = self.layers_listbox.curselection()
        if sel:
            del self.layers[sel[0]]
            self.refresh_layers()

    def refresh_layers(self):
        self.layers_listbox.delete(0, tk.END)
        for i, (name, thickness, color) in enumerate(self.layers):
            self.layers_listbox.insert(tk.END, f"{name} ({thickness} units) [{color}]")

    def generate_model(self):
        """
        Generate the GemPy 3 geological model and visualize it.
        """
        if not self.layers or len(self.layers) < 2:
            messagebox.showerror("Error", "At least two layers required.")
            return

        # Model extent and grid setup (fixed X/Y, Z from layers)
        from gempy.core.data.structural_frame import StructuralFrame

        extent = [0, 1000, 0, 1000, 0, sum(t for _, t, _ in self.layers)]
        resolution = [50, 50, 50]

        # Create structural frame
        structural_frame = StructuralFrame.initialize_default_structure()

        # (Optional: try to set extent and resolution if possible in your version)
        if hasattr(structural_frame, 'extent'):
            structural_frame.extent = extent
        if hasattr(structural_frame, 'resolution'):
            structural_frame.resolution = resolution

        geo_model = gp.create_geomodel(
            structural_frame=structural_frame
        )


        # Build surface points DataFrame (bottom of each layer, at X=500, Y=500)
        thicknesses = np.cumsum([0] + [t for _, t, _ in self.layers])
        data = []
        for i, (name, _, _) in enumerate(self.layers):
            # X, Y, Z (bottom of layer), formation name
            data.append([500.0, 500.0, thicknesses[i+1], name])
        df = pd.DataFrame(data, columns=["X", "Y", "Z", "surface"])

        # Set points in model
        geo_model.surface_points.df = df

        # Simple: let GemPy assign series based on order; advanced users can edit groups
        # Compute the model
        try:
            sol = gp.compute_model(geo_model)  # Modern call:contentReference[oaicite:1]{index=1}
        except Exception as e:
            messagebox.showerror("Compute Error", f"Could not compute model:\n{e}")
            return

        # Visualization using gempy_viewer if available
        try:
            if gpv is not None:
                gpv.plot_2d(geo_model, show_data=True)
            else:
                messagebox.showinfo("Result", "Model computed. To visualize, install 'gempy_viewer' (pip install gempy_viewer).")
        except Exception as e:
            messagebox.showerror("Plot Error", f"Could not plot the model:\n{e}")
            return

        messagebox.showinfo("Model Generated", "The geological model was generated successfully.")

def open_geo_model_tool(master):
    GeoModelTool(master)