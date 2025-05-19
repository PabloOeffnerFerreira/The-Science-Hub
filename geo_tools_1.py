import pandas as pd
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QComboBox, QCheckBox, QFileDialog, QMessageBox, QWidget
)
from data_utils import _open_dialogs, log_event
import json

minerals_df = pd.read_csv("Minerals_Database.csv")
minerals_df.drop(columns=[col for col in minerals_df.columns if ".ru" in col], inplace=True)

# 1. Mineral Identifier Tool
def open_mineral_id_tool():
    class MineralIdDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Mineral Identifier (Fuzzy Matching)")
            layout = QVBoxLayout(self)
            self.hard = QLineEdit()
            self.sg = QLineEdit()
            self.cs = QLineEdit()
            for label, widget in [
                ("Hardness (Mohs):", self.hard),
                ("Specific Gravity:", self.sg),
                ("Crystal Structure (number code):", self.cs),
            ]:
                row = QHBoxLayout()
                row.addWidget(QLabel(label))
                row.addWidget(widget)
                layout.addLayout(row)
            self.result = QTextEdit()
            self.result.setReadOnly(True)
            layout.addWidget(self.result)
            btn = QPushButton("Identify")
            btn.clicked.connect(self.identify)
            layout.addWidget(btn)
            self.setMinimumWidth(620)
        def identify(self):
            try:
                h = float(self.hard.text())
                sg = float(self.sg.text())
                cs = float(self.cs.text())
                matches = minerals_df[
                    (minerals_df['Mohs Hardness'].between(h - 0.5, h + 0.5)) &
                    (minerals_df['Specific Gravity'].between(sg - 0.5, sg + 0.5)) &
                    (minerals_df['Crystal Structure'] == cs)
                ]
                self.result.clear()
                if not matches.empty:
                    for _, row in matches.iterrows():
                        line = f"Name: {row['Name']} | Hardness: {row['Mohs Hardness']} | SG: {row['Specific Gravity']} | Structure: {row['Crystal Structure']}\n"
                        self.result.append(line)
                    log_event("Mineral Identifier", f"H={h}, SG={sg}, CS={cs}", f"Matches found: {len(matches)}")
                else:
                    msg = "No matching minerals found."
                    self.result.setText(msg)
                    log_event("Mineral Identifier", f"H={h}, SG={sg}, CS={cs}", msg)
            except Exception:
                msg = "Invalid input."
                self.result.setText(msg)
                log_event("Mineral Identifier", f"H={self.hard.text()}, SG={self.sg.text()}, CS={self.cs.text()}", msg)
    dlg = MineralIdDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

# 2. Radioactive Dating Tool
def open_radioactive_dating_tool():
    class DatingDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Radioactive Dating")
            layout = QVBoxLayout(self)
            self.half_life = QLineEdit()
            self.percent = QLineEdit()
            for label, widget in [
                ("Half-Life (years):", self.half_life),
                ("Percentage remaining (%):", self.percent),
            ]:
                row = QHBoxLayout()
                row.addWidget(QLabel(label))
                row.addWidget(widget)
                layout.addLayout(row)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Estimate Age")
            btn.clicked.connect(self.calculate_age)
            layout.addWidget(btn)
            self.setMinimumWidth(320)
        def calculate_age(self):
            try:
                hl = float(self.half_life.text())
                rem = float(self.percent.text())
                if not (0 < rem <= 100):
                    msg = "Percentage must be between 0 and 100."
                    self.result.setText(msg)
                    log_event("Radioactive Dating", f"HL={hl}, rem={rem}", msg)
                    return
                import math
                age = -hl * math.log2(rem / 100)
                msg = f"Estimated age: {age:.2f} years"
                self.result.setText(msg)
                log_event("Radioactive Dating", f"HL={hl}, rem={rem}", msg)
            except Exception:
                msg = "Invalid input."
                self.result.setText(msg)
                log_event("Radioactive Dating", f"HL={self.half_life.text()}, rem={self.percent.text()}", msg)
    dlg = DatingDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

# 3. Plate Boundary Tool
def open_plate_boundary_tool():
    class BoundaryDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Plate Boundary Types")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Choose a boundary type:"))
            self.box = QComboBox()
            self.box.addItems(["Select Type", "Convergent", "Divergent", "Transform"])
            layout.addWidget(self.box)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Explain")
            btn.clicked.connect(self.explain)
            layout.addWidget(btn)
            self.setMinimumWidth(400)
        def explain(self):
            selected = self.box.currentText()
            if selected == "Convergent":
                msg = "Plates move toward each other. Mountains, trenches, and volcanoes form."
            elif selected == "Divergent":
                msg = "Plates move apart. Mid-ocean ridges and new crust form."
            elif selected == "Transform":
                msg = "Plates slide past each other. Earthquakes are common."
            else:
                msg = "No boundary type selected."
            self.result.setText(msg)
            log_event("Plate Boundaries", selected, msg)
    dlg = BoundaryDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

# 4. Mineral Explorer
import pandas as pd
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt6.QtGui import QColor, QBrush
import json

MINERAL_DB_PATH = "Minerals_Database.csv"
minerals_df = pd.read_csv(MINERAL_DB_PATH)

def safe(val):
    if pd.isna(val) or val == 0 or val == "0.0":
        return "—"
    if isinstance(val, float):
        return f"{val:.2f}"
    return str(val)

def open_mineral_explorer():
    class ExplorerDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Mineral Explorer")
            layout = QVBoxLayout(self)

            self.search = QLineEdit()
            self.structure = QComboBox()
            self.favs_only = QCheckBox("Show Favorites Only")
            self.refresh_btn = QPushButton("Refresh")
            self.toggle_fav_btn = QPushButton("Toggle Favorite (by name)")
            structures = ["All"] + sorted([
                str(int(x)) for x in minerals_df["Crystal Structure"].dropna().unique() if x != 0
            ])
            self.structure.addItems(structures)

            bar = QHBoxLayout()
            bar.addWidget(QLabel("Search:"))
            bar.addWidget(self.search)
            bar.addWidget(QLabel("Structure:"))
            bar.addWidget(self.structure)
            bar.addWidget(self.favs_only)
            bar.addWidget(self.refresh_btn)
            layout.addLayout(bar)

            # Table Widget
            self.table = QTableWidget()
            self.table.setColumnCount(7)
            self.table.setHorizontalHeaderLabels([
                "Name", "Hardness", "SG", "Struct", "MolMass (g/mol)",
                "MolVol (cm³/mol)", "CalcDens (g/cm³)"
            ])
            self.table.setStyleSheet("""
                QTableWidget::item:selected { 
                    background: #c9a2ff;    /* pastel purple for selected rows */
                    font-weight: bold; 
                }
                QTableWidget::item:hover {
                    outline: 2px solid #8000ff;   /* strong purple outline */
                }
            """)
            self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)

            self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
            self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
            self.table.setAlternatingRowColors(True)
            self.table.verticalHeader().setVisible(False)
            layout.addWidget(self.table)
            layout.addWidget(self.toggle_fav_btn)

            self.favorites_path = "mineral_favorites.json"
            try:
                with open(self.favorites_path, "r") as f:
                    self.favorites = set(json.load(f))
            except Exception:
                self.favorites = set()

            # Connections
            self.search.textChanged.connect(self.update_display)
            self.structure.currentTextChanged.connect(self.update_display)
            self.favs_only.stateChanged.connect(self.update_display)
            self.refresh_btn.clicked.connect(self.update_display)
            self.toggle_fav_btn.clicked.connect(self.toggle_favorite)

            self.setMinimumWidth(920)
            self.setMinimumHeight(550)
            self.update_display()

        def update_display(self):
            query = self.search.text().strip().lower()
            selected_structure = self.structure.currentText()
            show_favs = self.favs_only.isChecked()

            filtered = minerals_df.copy()
            if show_favs:
                filtered = filtered[filtered["Name"].isin(self.favorites)]
            if query:
                filtered = filtered[
                    filtered["Name"].fillna("").str.lower().str.contains(query)
                ]
            if selected_structure != "All":
                try:
                    val = float(selected_structure)
                    filtered = filtered[filtered["Crystal Structure"] == val]
                except Exception:
                    pass

            show_fields = [
                "Name",
                "Mohs Hardness",
                "Specific Gravity",
                "Crystal Structure",
                "Molar Mass",
                "Molar Volume",
                "Calculated Density"
            ]
            from PyQt6.QtGui import QFont

            self.table.setRowCount(len(filtered))
            for rowidx, (_, row) in enumerate(filtered.iterrows()):
                for colidx, field in enumerate(show_fields):
                    value = safe(row[field])
                    item = QTableWidgetItem(value)
                    font = QFont()

                    # Favorites: gold background
                    if row["Name"] in self.favorites:
                        item.setBackground(QBrush(QColor("#ffd700")))

                    # Mohs Hardness: red for hard, blue for soft, bold for >=8
                    if field == "Mohs Hardness" and value not in ("—", ""):
                        try:
                            h = float(value)
                            if h >= 7:
                                item.setForeground(QBrush(QColor("red")))
                            elif h <= 3:
                                item.setForeground(QBrush(QColor("blue")))
                            if h >= 8:
                                font.setBold(True)
                        except: pass

                    # Specific Gravity: green for dense, gray for low
                    if field == "Specific Gravity" and value not in ("—", ""):
                        try:
                            sg = float(value)
                            if sg >= 4:
                                item.setForeground(QBrush(QColor("green")))
                            elif sg < 2.5:
                                item.setForeground(QBrush(QColor("gray")))
                        except: pass

                    # Calculated Density: purple & bold if >=5
                    if field == "Calculated Density" and value not in ("—", ""):
                        try:
                            dens = float(value)
                            if dens >= 5:
                                font.setBold(True)
                                item.setForeground(QBrush(QColor("#990099")))
                        except: pass

                    # Apply font (bold if set above)
                    item.setFont(font)
                    self.table.setItem(rowidx, colidx, item)

            self.table.resizeColumnsToContents()


        def toggle_favorite(self):
            selected = self.search.text().strip()
            if not selected:
                QMessageBox.information(self, "No name", "Enter a mineral name in the search box to star/unstar.")
                return
            # Find closest matching mineral name (case-insensitive)
            matches = minerals_df[minerals_df["Name"].str.lower() == selected.lower()]
            if matches.empty:
                QMessageBox.information(self, "Not found", f"No mineral found with name '{selected}' (case-insensitive).")
                return
            name = matches.iloc[0]["Name"]
            if name in self.favorites:
                self.favorites.remove(name)
            else:
                self.favorites.add(name)
            with open(self.favorites_path, "w") as f:
                json.dump(list(self.favorites), f, indent=2)
            log_event("Favorite Toggled", name, "★" if name in self.favorites else "Unstarred")
            self.update_display()

    dlg = ExplorerDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))


# 5. Plate Velocity Calculator
def open_plate_velocity_calculator():
    class PlateVelDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Plate Velocity Calculator")
            layout = QVBoxLayout(self)
            self.dist = QLineEdit()
            self.time = QLineEdit()
            row1 = QHBoxLayout()
            row1.addWidget(QLabel("Distance Moved (cm):"))
            row1.addWidget(self.dist)
            row2 = QHBoxLayout()
            row2.addWidget(QLabel("Time (million years):"))
            row2.addWidget(self.time)
            layout.addLayout(row1)
            layout.addLayout(row2)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Calculate Velocity")
            btn.clicked.connect(self.compute)
            layout.addWidget(btn)
            self.setMinimumWidth(380)
        def compute(self):
            try:
                dist_cm = float(self.dist.text())
                time_myr = float(self.time.text())
                if time_myr == 0:
                    raise ValueError("Time cannot be zero")
                velocity_cm_per_year = dist_cm / (time_myr * 1_000_000)
                velocity_mm_per_year = velocity_cm_per_year * 10  # cm/yr to mm/yr
                msg = f"Plate Velocity ≈ {velocity_mm_per_year:.4f} mm/yr"
                self.result.setText(msg)
                log_event("Plate Velocity Calculator", f"Distance={dist_cm} cm, Time={time_myr} Myr", velocity_mm_per_year)
            except Exception as e:
                self.result.setText(f"Error: {e}")
    dlg = PlateVelDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
