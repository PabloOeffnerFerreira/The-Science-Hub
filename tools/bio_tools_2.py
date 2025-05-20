from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QFileDialog
)
from tools.data_utils import _open_dialogs, log_event
from tools.data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data, ai_chatlogs_dir
)
import warnings
from Bio import BiopythonDeprecationWarning
warnings.filterwarnings("ignore", category=BiopythonDeprecationWarning)

from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction
from Bio import SeqIO
from Bio import pairwise2
from Bio.pairwise2 import format_alignment

def open_reverse_complement_tool():
    class ReverseDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Reverse Complement")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Enter DNA sequence:"))
            self.seq_entry = QLineEdit()
            layout.addWidget(self.seq_entry)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Compute")
            btn.clicked.connect(self.compute)
            layout.addWidget(btn)
            self.setMinimumWidth(400)
        def compute(self):
            seq = self.seq_entry.text().strip().upper()
            try:
                rc = str(Seq(seq).reverse_complement())
                msg = f"Reverse Complement: {rc}"
                self.result.setText(msg)
                log_event("Reverse Complement", seq, rc)
            except Exception as e:
                self.result.setText(f"Error: {e}")
    dlg = ReverseDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

def open_translate_dna_tool():
    class TranslateDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("DNA to Protein Translation (All Frames)")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Enter DNA sequence:"))
            self.seq_entry = QLineEdit()
            layout.addWidget(self.seq_entry)
            self.result = QTextEdit()
            self.result.setReadOnly(True)
            layout.addWidget(self.result)
            btn = QPushButton("Translate")
            btn.clicked.connect(self.translate)
            layout.addWidget(btn)
            self.setMinimumWidth(430)
        def translate(self):
            seq = Seq(self.seq_entry.text().strip().upper())
            lines = []
            for frame in range(3):
                prot = seq[frame:].translate(to_stop=False)
                lines.append(f"Frame {frame+1}: {prot}")
            self.result.setText("\n".join(lines))
            log_event("DNA to Protein Tool", str(seq), "\n".join(lines))
    dlg = TranslateDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

def open_gc_content_tool():
    class GCDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("GC Content Calculator")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Enter DNA sequence:"))
            self.seq_entry = QLineEdit()
            layout.addWidget(self.seq_entry)
            self.result = QLabel("")
            layout.addWidget(self.result)
            btn = QPushButton("Compute")
            btn.clicked.connect(self.compute)
            layout.addWidget(btn)
            self.setMinimumWidth(400)
        def compute(self):
            seq = self.seq_entry.text().strip().upper()
            try:
                gc = gc_fraction(seq) * 100
                msg = f"GC Content: {gc:.2f}%"
                self.result.setText(msg)
                log_event("GC Content Tool", seq, msg)
            except Exception as e:
                self.result.setText(f"Error: {e}")
    dlg = GCDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

def open_seq_file_parser_tool():
    class SeqParserDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Sequence File Parser (FASTA/GenBank)")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Open a FASTA or GenBank file:"))
            self.result = QTextEdit()
            self.result.setReadOnly(True)
            layout.addWidget(self.result)
            btn = QPushButton("Open File")
            btn.clicked.connect(self.open_file)
            layout.addWidget(btn)
            self.setMinimumWidth(600)
            self.setMinimumHeight(350)
        def open_file(self):
            path, _ = QFileDialog.getOpenFileName(self, "Open FASTA/GenBank File", "", "FASTA/GenBank (*.fasta *.fa *.gb *.gbk)")
            if path:
                try:
                    # Try FASTA first, then GenBank
                    try:
                        records = list(SeqIO.parse(path, "fasta"))
                        if not records:
                            raise ValueError("No records found in FASTA.")
                    except Exception:
                        records = list(SeqIO.parse(path, "genbank"))
                    text = []
                    for rec in records:
                        text.append(f"ID: {rec.id}\nLength: {len(rec.seq)}\nSequence:\n{rec.seq}\n{'-'*30}\n")
                    self.result.setText("".join(text))
                    log_event("Sequence File Parser", path, f"{len(records)} records")
                except Exception as e:
                    self.result.setText(f"Error: {e}\n")
    dlg = SeqParserDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

def open_pairwise_align_tool():
    class AlignDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Pairwise Sequence Alignment")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Sequence 1:"))
            self.seq1_entry = QLineEdit()
            layout.addWidget(self.seq1_entry)
            layout.addWidget(QLabel("Sequence 2:"))
            self.seq2_entry = QLineEdit()
            layout.addWidget(self.seq2_entry)
            self.result = QTextEdit()
            self.result.setReadOnly(True)
            layout.addWidget(self.result)
            btn = QPushButton("Align")
            btn.clicked.connect(self.align)
            layout.addWidget(btn)
            self.setMinimumWidth(650)
        def align(self):
            seq1 = self.seq1_entry.text().strip().upper()
            seq2 = self.seq2_entry.text().strip().upper()
            try:
                alignments = pairwise2.align.globalxx(seq1, seq2)
                if alignments:
                    text = "\n".join(format_alignment(*aln) for aln in alignments[:3])
                    self.result.setText(text)
                else:
                    self.result.setText("No alignment found.\n")
                log_event("Pairwise Alignment Tool", f"{seq1} | {seq2}", "Aligned")
            except Exception as e:
                self.result.setText(f"Error: {e}")
    dlg = AlignDialog()
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
