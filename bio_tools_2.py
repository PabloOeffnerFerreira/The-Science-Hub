from utils import register_window
import tkinter as tk

# 1. Reverse Complement Tool
from Bio.Seq import Seq
def open_reverse_complement_tool(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Reverse Complement")

        tk.Label(win, text="Enter DNA sequence:").pack()
        seq_entry = tk.Entry(win, width=60)
        seq_entry.pack(pady=5)

        if preload:
            seq_entry.insert(0, preload)

        result_label = tk.Label(win, text="")
        result_label.pack(pady=10)

        def compute():
            seq = seq_entry.get().strip().upper()
            try:
                rc = str(Seq(seq).reverse_complement())
                result_label.config(text=f"Reverse Complement: {rc}")
            except Exception as e:
                result_label.config(text=f"Error: {e}")

        tk.Button(win, text="Compute", command=compute).pack(pady=5)
        return win
    register_window("Reverse Complement Tool", create_window)

# 2. DNA to Protein Translation (all 3 frames)
def open_translate_dna_tool(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("DNA to Protein Translation (All Frames)")

        tk.Label(win, text="Enter DNA sequence:").pack()
        seq_entry = tk.Entry(win, width=60)
        seq_entry.pack(pady=5)
        if preload:
            seq_entry.insert(0, preload)

        result = tk.Text(win, width=70, height=8)
        result.pack(pady=5)

        def translate():
            seq = Seq(seq_entry.get().strip().upper())
            lines = []
            for frame in range(3):
                prot = seq[frame:].translate(to_stop=False)
                lines.append(f"Frame {frame+1}: {prot}")
            result.delete('1.0', tk.END)
            result.insert(tk.END, "\n".join(lines))

        tk.Button(win, text="Translate", command=translate).pack(pady=5)
        return win
    register_window("DNA to Protein Tool", create_window)

# 3. GC Content Calculator
from Bio.SeqUtils import gc_fraction
def open_gc_content_tool(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("GC Content Calculator")

        tk.Label(win, text="Enter DNA sequence:").pack()
        seq_entry = tk.Entry(win, width=60)
        seq_entry.pack(pady=5)
        if preload:
            seq_entry.insert(0, preload)

        result_label = tk.Label(win, text="")
        result_label.pack(pady=10)

        def compute():
            seq = seq_entry.get().strip().upper()
            try:
                gc = gc_fraction(seq) * 100
                result_label.config(text=f"GC Content: {gc:.2f}%")
            except Exception as e:
                result_label.config(text=f"Error: {e}")

        tk.Button(win, text="Compute", command=compute).pack(pady=5)
        return win
    register_window("GC Content Tool", create_window)

# 4. Sequence File Parser (FASTA/GenBank Viewer)
from Bio import SeqIO
from tkinter import filedialog
def open_seq_file_parser_tool(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Sequence File Parser (FASTA/GenBank)")

        tk.Label(win, text="Open a FASTA or GenBank file:").pack()

        result = tk.Text(win, width=70, height=12)
        result.pack(pady=5)

        def open_file():
            path = filedialog.askopenfilename(filetypes=[("FASTA/GenBank files", "*.fasta *.fa *.gb *.gbk")])
            if path:
                try:
                    # Try FASTA first, then GenBank
                    try:
                        records = list(SeqIO.parse(path, "fasta"))
                        if not records:
                            raise ValueError("No records found in FASTA.")
                    except Exception:
                        records = list(SeqIO.parse(path, "genbank"))
                    for rec in records:
                        result.insert(tk.END, f"ID: {rec.id}\nLength: {len(rec.seq)}\nSequence:\n{rec.seq}\n{'-'*30}\n")
                except Exception as e:
                    result.insert(tk.END, f"Error: {e}\n")

        tk.Button(win, text="Open File", command=open_file).pack(pady=5)
        return win
    register_window("Sequence File Parser", create_window)

# 5. Pairwise Sequence Alignment (Needleman-Wunsch, simple global align)
from Bio import pairwise2
from Bio.pairwise2 import format_alignment
def open_pairwise_align_tool(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Pairwise Sequence Alignment")

        tk.Label(win, text="Sequence 1:").pack()
        seq1_entry = tk.Entry(win, width=60)
        seq1_entry.pack(pady=2)

        tk.Label(win, text="Sequence 2:").pack()
        seq2_entry = tk.Entry(win, width=60)
        seq2_entry.pack(pady=2)

        result = tk.Text(win, width=80, height=12)
        result.pack(pady=5)

        def align():
            seq1 = seq1_entry.get().strip().upper()
            seq2 = seq2_entry.get().strip().upper()
            try:
                alignments = pairwise2.align.globalxx(seq1, seq2)
                result.delete('1.0', tk.END)
                if alignments:
                    for aln in alignments[:3]:
                        result.insert(tk.END, format_alignment(*aln) + '\n')
                else:
                    result.insert(tk.END, "No alignment found.\n")
            except Exception as e:
                result.delete('1.0', tk.END)
                result.insert(tk.END, f"Error: {e}")

        tk.Button(win, text="Align", command=align).pack(pady=5)
        return win
    register_window("Pairwise Alignment Tool", create_window)