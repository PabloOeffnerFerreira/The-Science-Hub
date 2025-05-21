from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QFileDialog
)
from data_utils import _open_dialogs, log_event
from data_utils import (settings_path, results_dir, ptable_path, element_favs_path, load_element_data)
import math
import os
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data, ai_chatlogs_dir
)
CODON_TABLE = {
    'UUU': 'Phe', 'UUC': 'Phe', 'UUA': 'Leu', 'UUG': 'Leu',
    'CUU': 'Leu', 'CUC': 'Leu', 'CUA': 'Leu', 'CUG': 'Leu',
    'AUU': 'Ile', 'AUC': 'Ile', 'AUA': 'Ile', 'AUG': 'Met',
    'GUU': 'Val', 'GUC': 'Val', 'GUA': 'Val', 'GUG': 'Val',
    'UCU': 'Ser', 'UCC': 'Ser', 'UCA': 'Ser', 'UCG': 'Ser',
    'CCU': 'Pro', 'CCC': 'Pro', 'CCA': 'Pro', 'CCG': 'Pro',
    'ACU': 'Thr', 'ACC': 'Thr', 'ACA': 'Thr', 'ACG': 'Thr',
    'GCU': 'Ala', 'GCC': 'Ala', 'GCA': 'Ala', 'GCG': 'Ala',
    'UAU': 'Tyr', 'UAC': 'Tyr', 'UAA': 'STOP', 'UAG': 'STOP',
    'CAU': 'His', 'CAC': 'His', 'CAA': 'Gln', 'CAG': 'Gln',
    'AAU': 'Asn', 'AAC': 'Asn', 'AAA': 'Lys', 'AAG': 'Lys',
    'GAU': 'Asp', 'GAC': 'Asp', 'GAA': 'Glu', 'GAG': 'Glu',
    'UGU': 'Cys', 'UGC': 'Cys', 'UGA': 'STOP', 'UGG': 'Trp',
    'CGU': 'Arg', 'CGC': 'Arg', 'CGA': 'Arg', 'CGG': 'Arg',
    'AGU': 'Ser', 'AGC': 'Ser', 'AGA': 'Arg', 'AGG': 'Arg',
    'GGU': 'Gly', 'GGC': 'Gly', 'GGA': 'Gly', 'GGG': 'Gly'
}

def open_transcription_tool():
    class TranscribeDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("DNA Transcription & Translation")
            self.setMinimumWidth(600)

            layout = QVBoxLayout(self)

            layout.addWidget(QLabel("Enter DNA sequence:"))
            self.entry = QLineEdit()
            self.entry.setPlaceholderText("Enter DNA sequence using A, T, C, G only")
            layout.addWidget(self.entry)

            btn_layout = QHBoxLayout()
            self.translate_btn = QPushButton("Translate")
            self.copy_btn = QPushButton("Copy Result")
            self.export_btn = QPushButton("Export Chart")
            btn_layout.addWidget(self.translate_btn)
            btn_layout.addWidget(self.copy_btn)
            btn_layout.addWidget(self.export_btn)
            layout.addLayout(btn_layout)

            self.output = QTextEdit()
            self.output.setReadOnly(True)
            layout.addWidget(self.output)

            # Matplotlib figure and canvas for codon frequency chart
            self.figure, self.ax = plt.subplots(figsize=(8, 3), dpi=100)
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)

            self.saved_img_path = None

            # Connect buttons
            self.translate_btn.clicked.connect(self.transcribe_and_translate)
            self.copy_btn.clicked.connect(self.copy_result)
            self.export_btn.clicked.connect(self.export_chart)

        def transcribe_and_translate(self):
            raw_seq = self.entry.text().strip().upper()
            # Validate DNA sequence
            if not raw_seq:
                self.show_error("Please enter a DNA sequence.")
                return
            if any(ch not in "ATCG" for ch in raw_seq):
                self.show_error("DNA sequence can contain only A, T, C, and G.")
                return

            # Transcription: T -> U
            mrna_seq = raw_seq.replace("T", "U")

            # Translate using global CODON_TABLE, group by 3
            protein = []
            codons = []
            for i in range(0, len(mrna_seq) - 2, 3):
                codon = mrna_seq[i:i+3]
                codons.append(codon)
                amino = CODON_TABLE.get(codon, '?')
                protein.append(amino)

            protein_str = '-'.join(protein)

            # Output text
            output_text = f"mRNA:\n{mrna_seq}\n\nProtein:\n{protein_str}"
            self.output.setPlainText(output_text)

            # Plot codon frequency
            self.plot_codon_frequency(codons)

            # Save chart image if codons exist
            if codons:
                self.saved_img_path = self.save_chart_image()
                self.output.append(f"\n[Chart saved to:\n{self.saved_img_path}]")

            # Log event
            log_event("DNA Transcription & Translation", raw_seq, protein_str)

        def plot_codon_frequency(self, codons):
            self.ax.clear()
            if not codons:
                self.canvas.draw()
                return

            from collections import Counter
            counts = Counter(codons)
            codon_labels = sorted(counts.keys())
            freqs = [counts[c] for c in codon_labels]

            self.ax.barh(codon_labels, freqs, color="#4682B4")
            self.ax.set_xlabel("Frequency")
            self.ax.set_title("Codon Usage Frequency")
            self.ax.grid(axis="x", linestyle='--', alpha=0.7)

            self.figure.tight_layout()
            self.canvas.draw()

        def save_chart_image(self):
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"codon_usage_{timestamp}.png"
            path = os.path.join(results_dir, filename)
            self.figure.savefig(path, dpi=150)
            return path

        def copy_result(self):
            clipboard = self.clipboard()
            clipboard.setText(self.output.toPlainText())
            log_event("DNA Transcription & Translation", "Copy Result", "User copied result text")

        def export_chart(self):
            path, _ = QFileDialog.getSaveFileName(self, "Export Codon Usage Chart", "", "PNG Files (*.png)")
            if path:
                try:
                    self.figure.savefig(path, dpi=150)
                    self.output.append(f"\n[Chart manually exported to:\n{path}]")
                    log_event("DNA Transcription & Translation", "Export Chart", f"Exported to {path}")
                except Exception as e:
                    self.show_error(f"Failed to save chart image: {e}")

        def show_error(self, msg):
            self.output.setPlainText(f"Error: {msg}")
            log_event("DNA Transcription & Translation", "Error", msg)

    dlg = TranscribeDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))


def open_codon_lookup_tool():
    class CodonDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Codon Lookup")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Enter RNA Codon (e.g. AUG):"))
            self.entry = QLineEdit()
            layout.addWidget(self.entry)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Lookup")
            btn.clicked.connect(self.lookup)
            layout.addWidget(btn)
            self.setMinimumWidth(280)
        def lookup(self):
            codon = self.entry.text().upper()
            amino = CODON_TABLE.get(codon, 'Invalid')
            self.result.setText(f"Amino Acid: {amino}")
            log_event("Codon Lookup", codon, amino)
    dlg = CodonDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

def open_osmosis_tool():
    class OsmosisDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Osmosis & Tonicity")
            layout = QVBoxLayout(self)
            row1 = QHBoxLayout()
            row1.addWidget(QLabel("Internal concentration (mM):"))
            self.int_entry = QLineEdit()
            row1.addWidget(self.int_entry)
            row2 = QHBoxLayout()
            row2.addWidget(QLabel("External concentration (mM):"))
            self.ext_entry = QLineEdit()
            row2.addWidget(self.ext_entry)
            layout.addLayout(row1)
            layout.addLayout(row2)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Assess")
            btn.clicked.connect(self.assess)
            layout.addWidget(btn)
            self.setMinimumWidth(350)
        def assess(self):
            try:
                inside = float(self.int_entry.text())
                outside = float(self.ext_entry.text())
                if inside > outside:
                    status = "Hypertonic inside: Water leaves the cell"
                elif inside < outside:
                    status = "Hypotonic inside: Water enters the cell"
                else:
                    status = "Isotonic: No net water movement"
                self.result.setText(status)
                log_event("Osmosis Tool", f"in={inside} mM, out={outside} mM", status)
            except ValueError:
                status = "Invalid input."
                self.result.setText(status)
                log_event("Osmosis Tool", f"in={self.int_entry.text()}, out={self.ext_entry.text()}", status)
    dlg = OsmosisDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

def open_molecular_weight_calculator():
    class MWDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Molecular Weight Calculator")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Enter Sequence (DNA/RNA or Protein):"))
            self.seq_entry = QTextEdit()
            self.seq_entry.setFixedHeight(50)
            layout.addWidget(self.seq_entry)
            self.result_label = QLabel("")
            layout.addWidget(self.result_label)
            btn = QPushButton("Calculate")
            btn.clicked.connect(self.compute)
            layout.addWidget(btn)
            self.setMinimumWidth(420)
        def compute(self):
            seq = self.seq_entry.toPlainText().strip().upper()
            if not seq:
                self.result_label.setText("Please enter a sequence.")
                return
            dna_weights = {
                "A": 313.21, "T": 304.2, "G": 329.21, "C": 289.18, "U": 290.17
            }
            protein_weights = {
                "A": 89.09, "R": 174.2, "N": 132.12, "D": 133.1, "C": 121.15,
                "E": 147.13, "Q": 146.15, "G": 75.07, "H": 155.16, "I": 131.17,
                "L": 131.17, "K": 146.19, "M": 149.21, "F": 165.19, "P": 115.13,
                "S": 105.09, "T": 119.12, "W": 204.23, "Y": 181.19, "V": 117.15
            }
            if all(base in dna_weights for base in seq):
                weight = sum(dna_weights.get(base, 0) for base in seq)
                msg = f"Approximate DNA/RNA Molecular Weight: {weight:.2f} Da"
            elif all(aa in protein_weights for aa in seq):
                weight = sum(protein_weights.get(aa, 0) for aa in seq)
                msg = f"Approximate Protein Molecular Weight: {weight:.2f} Da"
            else:
                msg = "Sequence contains invalid characters."
            self.result_label.setText(msg)
            log_event("Molecular Weight Calculator", seq, msg)
    dlg = MWDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

def open_ph_calculator():
    class PHDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("pH Calculator")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Enter H⁺ concentration [mol/L] (leave blank if calculating pOH):"))
            self.h_entry = QLineEdit()
            layout.addWidget(self.h_entry)
            layout.addWidget(QLabel("Enter OH⁻ concentration [mol/L] (leave blank if calculating pH):"))
            self.oh_entry = QLineEdit()
            layout.addWidget(self.oh_entry)
            self.result_label = QLabel("")
            layout.addWidget(self.result_label)
            btn = QPushButton("Calculate")
            btn.clicked.connect(self.compute)
            layout.addWidget(btn)
            self.setMinimumWidth(400)
        def compute(self):
            try:
                h_conc = self.h_entry.text().strip()
                oh_conc = self.oh_entry.text().strip()
                if h_conc and oh_conc:
                    msg = "Enter only one concentration at a time."
                elif h_conc:
                    h = float(h_conc)
                    if h <= 0:
                        raise ValueError
                    pH = -math.log10(h)
                    msg = f"pH = {pH:.2f}"
                elif oh_conc:
                    oh = float(oh_conc)
                    if oh <= 0:
                        raise ValueError
                    pOH = -math.log10(oh)
                    pH = 14 - pOH
                    msg = f"pOH = {pOH:.2f}, pH = {pH:.2f}"
                else:
                    msg = "Enter at least one concentration."
            except:
                msg = "Invalid input."
            self.result_label.setText(msg)
            log_event("pH Calculator", f"H={self.h_entry.text()}, OH={self.oh_entry.text()}", msg)
    dlg = PHDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

def open_population_growth_calculator():
    class PopDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Population Growth Calculator")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Initial Population (N₀):"))
            self.n0_entry = QLineEdit()
            layout.addWidget(self.n0_entry)
            layout.addWidget(QLabel("Growth Rate (r) [per time unit]:"))
            self.r_entry = QLineEdit()
            layout.addWidget(self.r_entry)
            layout.addWidget(QLabel("Time (t):"))
            self.t_entry = QLineEdit()
            layout.addWidget(self.t_entry)
            self.result_label = QLabel("")
            layout.addWidget(self.result_label)
            btn = QPushButton("Calculate")
            btn.clicked.connect(self.compute)
            layout.addWidget(btn)
            self.setMinimumWidth(350)
        def compute(self):
            try:
                N0 = float(self.n0_entry.text())
                r = float(self.r_entry.text())
                t = float(self.t_entry.text())
                N = N0 * math.exp(r * t)
                msg = f"Population after {t} time units: {N:.2f}"
            except Exception as e:
                msg = f"Error: {e}"
            self.result_label.setText(msg)
            log_event("Population Growth Calculator", f"N0={self.n0_entry.text()}, r={self.r_entry.text()}, t={self.t_entry.text()}", msg)
    dlg = PopDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
