from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton
)
from data_utils import _open_dialogs, log_event
import math

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

# 1. DNA Transcription & Translation Tool
def open_transcription_tool():
    class TranscribeDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("DNA Transcription & Translation")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Enter DNA sequence:"))
            self.entry = QLineEdit()
            layout.addWidget(self.entry)
            self.output = QTextEdit()
            self.output.setReadOnly(True)
            layout.addWidget(self.output)
            btn = QPushButton("Translate")
            btn.clicked.connect(self.transcribe)
            layout.addWidget(btn)
            self.setMinimumWidth(500)
        def transcribe(self):
            dna = self.entry.text().upper().replace("T", "U")
            protein = []
            for i in range(0, len(dna) - 2, 3):
                codon = dna[i:i + 3]
                amino = CODON_TABLE.get(codon, '?')
                protein.append(amino)
            mrna_line = f"mRNA: {dna}"
            protein_line = f"Protein: {'-'.join(protein)}"
            self.output.setText(mrna_line + "\n" + protein_line)
            log_event("DNA Transcription", dna, protein_line)
    dlg = TranscribeDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

# 2. Codon Lookup Tool
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

# 3. Osmosis and Tonicity Tool
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

# 4. Molecular Weight Calculator (DNA/RNA/Protein)
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

# 5. pH Calculator
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

# 6. Population Growth Calculator
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
<<<<<<< HEAD
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
=======
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
>>>>>>> 5896feb1d2c409629c464efb94cc07fa25f91bbc
