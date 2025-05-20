import os
import json
import re
import datetime
from tools.utilities import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file
)

def load_element_data():
    with open(ptable_path, "r", encoding="utf-8") as f:
        return {el["symbol"]: el for el in json.load(f)["elements"]}

def parse_formula(formula):
    """
    Parses a chemical formula string and returns a dict of element counts.
    Supports nested parentheses like Fe2(SO4)3 → {'Fe':2, 'S':3, 'O':12}
    """
    def multiply_counts(counts, factor):
        return {el: val * factor for el, val in counts.items()}

    def parse_chunk(s, i=0):
        elements = {}
        while i < len(s):
            if s[i] == '(':
                sub_counts, i = parse_chunk(s, i + 1)
                match = re.match(r'\d+', s[i:])
                mult = int(match.group()) if match else 1
                i += len(match.group()) if match else 0
                for el, count in multiply_counts(sub_counts, mult).items():
                    elements[el] = elements.get(el, 0) + count
            elif s[i] == ')':
                return elements, i + 1
            else:
                match = re.match(r'([A-Z][a-z]?)(\d*)', s[i:])
                if not match:
                    raise ValueError(f"Invalid element symbol at: {s[i:]}")
                symbol = match.group(1)
                count = int(match.group(2)) if match.group(2) else 1
                elements[symbol] = elements.get(symbol, 0) + count
                i += len(match.group(0))
        return elements, i

    return parse_chunk(formula)[0]

_open_dialogs = []
_open_windows_registry = {}  # name: dialog instance

def register_window(name, dialog):
    _open_dialogs.append(dialog)
    _open_windows_registry[name] = dialog
    # Remove from both on close
    def cleanup():
        if dialog in _open_dialogs:
            _open_dialogs.remove(dialog)
        if name in _open_windows_registry and _open_windows_registry[name] is dialog:
            del _open_windows_registry[name]
    dialog.finished.connect(lambda _: cleanup())


def log_event(tool, input_value, output_value):
    """Append a formatted log entry to the Science Hub session log."""
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            line = f"{timestamp} {tool} Input: {input_value} Output: {output_value}\n"
            f.write(line)
    except Exception as e:
        print("Logging failed:", e)
