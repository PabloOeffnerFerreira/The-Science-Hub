import os
import json
import requests
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QWidget, QScrollArea, QMessageBox, QCheckBox,
    QFileDialog
)
from PyQt6.QtCore import Qt
from data_utils import register_window

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"


class FilterRow(QWidget):
    def __init__(self, definition, remove_callback):
        super().__init__()
        self.definition = definition
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(3, 3, 3, 3)

        self.prop = definition["property"]

        self.operator_box = QComboBox()
        self.operator_box.addItems(definition["operators"])

        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("value...")

        self.remove_btn = QPushButton("✕")
        self.remove_btn.setFixedWidth(30)
        self.remove_btn.clicked.connect(lambda: remove_callback(self))

        self.layout.addWidget(QLabel(definition["label"]))
        self.layout.addWidget(self.operator_box)
        self.layout.addWidget(self.value_input)
        self.layout.addWidget(self.remove_btn)

    def to_sparql(self):
        op = self.operator_box.currentText()
        val = self.value_input.text().strip()
        if op == "exists":
            return f"FILTER EXISTS {{ ?item {self.prop} ?x }}"
        elif op == "not exists":
            return f"FILTER NOT EXISTS {{ ?item {self.prop} ?x }}"
        elif op == "equals":
            return f'?item {self.prop} "{val}"'
        elif op == "contains":
            return f'FILTER(CONTAINS(LCASE(STR(?itemLabel)), "{val.lower()}"))'
        elif op == "starts with":
            return f'FILTER(STRSTARTS(LCASE(STR(?itemLabel)), "{val.lower()}"))'
        return ""


class ToolMaker(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wikidata Tool Maker")
        self.setMinimumSize(900, 700)

        self.main_layout = QVBoxLayout(self)

        self.tool_name = QLineEdit()
        self.category = QComboBox()
        self.category.addItems(["Physics", "Chemistry", "Biology", "Math", "Geology", "Misc"])

        self.result_fields = QLineEdit()
        self.result_fields.setPlaceholderText("label, image, description...")

        self.chainable = QCheckBox("Chainable Output")

        self.filter_defs = self.load_filters()

        self.filter_rows = []

        self.main_layout.addWidget(QLabel("Tool Name:"))
        self.main_layout.addWidget(self.tool_name)
        self.main_layout.addWidget(QLabel("Scientific Category:"))
        self.main_layout.addWidget(self.category)
        self.main_layout.addWidget(QLabel("Result Fields:"))
        self.main_layout.addWidget(self.result_fields)
        self.main_layout.addWidget(self.chainable)

        self.filter_container = QWidget()
        self.filter_layout = QVBoxLayout(self.filter_container)
        self.filter_scroll = QScrollArea()
        self.filter_scroll.setWidgetResizable(True)
        self.filter_scroll.setWidget(self.filter_container)

        self.main_layout.addWidget(QLabel("Filters:"))
        self.main_layout.addWidget(self.filter_scroll)

        self.add_filter_btn = QPushButton("Add Filter")
        self.add_filter_btn.clicked.connect(self.add_filter)
        self.main_layout.addWidget(self.add_filter_btn)

        self.generate_btn = QPushButton("Generate Tool")
        self.generate_btn.clicked.connect(self.generate_tool)
        self.main_layout.addWidget(self.generate_btn)

    def load_filters(self):
        try:
            with open("filters.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load filters.json: {e}")
            return []

    def add_filter(self):
        if not self.filter_defs:
            return
        definition = self.filter_defs[len(self.filter_rows) % len(self.filter_defs)]
        row = FilterRow(definition, self.remove_filter)
        self.filter_rows.append(row)
        self.filter_layout.addWidget(row)

    def remove_filter(self, row):
        self.filter_rows.remove(row)
        row.setParent(None)
        row.deleteLater()

    def generate_tool(self):
        name = self.tool_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", "Enter a tool name.")
            return

        class_name = name.replace(" ", "") + "Tool"
        function_name = "open_" + name.lower().replace(" ", "_")
        file_name = function_name + ".py"

        sparql_filters = "\\n".join(row.to_sparql() for row in self.filter_rows)
        result_fields = self.result_fields.text().strip().split(",")
        result_fields = [f.strip() for f in result_fields if f.strip()]

        content = f"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QListWidget, QTextBrowser, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
import requests
from data_utils import register_window

class {class_name}(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("{name}")
        self.resize(1000, 600)
        self.setStyleSheet("background-color: #121212; color: #ffffff;")

        layout = QVBoxLayout()
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in results...")
        self.search_input.textChanged.connect(self.filter_list)
        search_row.addWidget(QLabel("Search:"))
        search_row.addWidget(self.search_input)
        layout.addLayout(search_row)

        self.list = QListWidget()
        self.viewer = QTextBrowser()
        self.viewer.setStyleSheet("background:#1e1e1e; color:#dddddd;")
        self.list.currentItemChanged.connect(self.show_details)

        row = QHBoxLayout()
        row.addWidget(self.list, 2)
        row.addWidget(self.viewer, 4)
        layout.addLayout(row)
        self.setLayout(layout)

        self.data = []
        self.load_data()

    def filter_list(self):
        text = self.search_input.text().lower()
        self.list.clear()
        for item in self.data:
            if "{result_fields[0]}" in item and text in item["{result_fields[0]}"].lower():
                self.list.addItem(item["{result_fields[0]}"])

    def show_details(self, current, _):
        if not current:
            return
        selected = current.text()
        match = next((d for d in self.data if d.get("{result_fields[0]}") == selected), None)
        if match:
            html = "<h3>" + match.get("{result_fields[0]}", "") + "</h3><ul>"
            for field in {result_fields}:
                html += f"<li><b>{{field}}:</b> {{match.get(field, '')}}</li>"
            html += "</ul>"
            self.viewer.setHtml(html)

    def load_data(self):
        query = f\"""SELECT ?item ?itemLabel WHERE {{
  ?item rdfs:label ?itemLabel .
  FILTER(LANG(?itemLabel) = 'en')
  {sparql_filters}
}} LIMIT 100\"""
        try:
            r = requests.get("https://query.wikidata.org/sparql",
                             params={{"query": query}}, headers={{"Accept": "application/sparql-results+json"}})
            data = r.json()
            self.data = [{{var: row[var]["value"] for var in row}} for row in data["results"]["bindings"]]
            for entry in self.data:
                if "{result_fields[0]}" in entry:
                    self.list.addItem(entry["{result_fields[0]}"])
        except Exception as e:
            self.viewer.setPlainText("Failed to fetch data: " + str(e))

def {function_name}():
    dlg = {class_name}()
    dlg.show()
    register_window("{name}", dlg)
"""

        save_path = QFileDialog.getSaveFileName(self, "Save Tool File", file_name, "Python Files (*.py)")[0]
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(content)
            QMessageBox.information(self, "Tool Created", f"Tool saved to: {save_path}")