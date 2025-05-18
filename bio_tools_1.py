from utils import register_window  # [AUTO-REFRACTORED]
import tkinter as tk
from tkinter import ttk
from utils import log_event

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
def open_transcription_tool(preload=None):
    def create_window():
        window = tk.Toplevel()
        window.title("DNA Transcription & Translation")

        tk.Label(window, text="Enter DNA sequence:").pack(pady=5)
        entry = tk.Entry(window, width=60)
        entry.pack(pady=5)

        if preload:
            entry.insert(0, preload)
            log_event("DNA Transcription (Chain)", preload, "Waiting for translation")

        output = tk.Text(window, width=70, height=10)
        output.pack(pady=5)

        def transcribe():
            dna = entry.get().upper().replace("T", "U")
            protein = []
            for i in range(0, len(dna) - 2, 3):
                codon = dna[i:i + 3]
                amino = CODON_TABLE.get(codon, '?')
                protein.append(amino)
            mrna_line = f"mRNA: {dna}"
            protein_line = f"Protein: {'-'.join(protein)}"
            output.delete('1.0', tk.END)
            output.insert(tk.END, mrna_line + "\n")
            output.insert(tk.END, protein_line)
            log_event("DNA Transcription", dna, protein_line)

        tk.Button(window, text="Translate", command=transcribe).pack(pady=5)
        return window

    register_window("Transcription Tool", create_window)


# 2. Codon Lookup Tool
def open_codon_lookup_tool(preload=None):
    def create_window():
        window = tk.Toplevel()
        window.title("Codon Lookup")

        tk.Label(window, text="Enter RNA Codon (e.g. AUG):").pack(pady=5)
        entry = tk.Entry(window, width=10)
        entry.pack(pady=5)

        if preload:
            entry.insert(0, preload)
            log_event("Codon Lookup (Chain)", preload, "Waiting for lookup")

        result = tk.Label(window, text="")
        result.pack(pady=5)

        def lookup():
            codon = entry.get().upper()
            amino = CODON_TABLE.get(codon, 'Invalid')
            result.config(text=f"Amino Acid: {amino}")
            log_event("Codon Lookup", codon, amino)

        tk.Button(window, text="Lookup", command=lookup).pack(pady=5)
        return window

    register_window("Codon Lookup Tool", create_window)


# 3. Osmosis and Tonicity Tool
def open_osmosis_tool(preload=None):
    def create_window():
        window = tk.Toplevel()
        window.title("Osmosis & Tonicity")

        tk.Label(window, text="Enter internal concentration (mM):").pack(pady=2)
        int_entry = tk.Entry(window)
        int_entry.pack(pady=2)

        tk.Label(window, text="Enter external concentration (mM):").pack(pady=2)
        ext_entry = tk.Entry(window)
        ext_entry.pack(pady=2)

        if preload and isinstance(preload, tuple) and len(preload) == 2:
            int_entry.insert(0, str(preload[0]))
            ext_entry.insert(0, str(preload[1]))
            log_event("Osmosis Tool (Chain)", f"{preload}", "Waiting for assessment")

        result = tk.Label(window, text="")
        result.pack(pady=5)

        def assess():
            try:
                inside = float(int_entry.get())
                outside = float(ext_entry.get())
                if inside > outside:
                    status = "Hypertonic inside: Water leaves the cell"
                elif inside < outside:
                    status = "Hypotonic inside: Water enters the cell"
                else:
                    status = "Isotonic: No net water movement"
                result.config(text=status)
                log_event("Osmosis Tool", f"in={inside} mM, out={outside} mM", status)
            except ValueError:
                status = "Invalid input."
                result.config(text=status)
                log_event("Osmosis Tool", f"in={int_entry.get()}, out={ext_entry.get()}", status)

        tk.Button(window, text="Assess", command=assess).pack(pady=5)
        return window

    register_window("Osmosis Tool", create_window)

def open_molecular_weight_calculator(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Molecular Weight Calculator")

        tk.Label(win, text="Enter Sequence (DNA or Protein):").pack()
        seq_entry = tk.Text(win, width=50, height=5)
        seq_entry.pack(pady=5)

        result_label = tk.Label(win, text="")
        result_label.pack(pady=10)

        def compute():
            seq = seq_entry.get("1.0", tk.END).strip().upper()
            if not seq:
                result_label.config(text="Please enter a sequence.")
                return

            # Approximate average weights (Daltons)
            dna_weights = {
                "A": 313.21, "T": 304.2, "G": 329.21, "C": 289.18, "U": 290.17
            }
            protein_weights = {
                # Average amino acid weights; simplified
                "A": 89.09, "R": 174.2, "N": 132.12, "D": 133.1, "C": 121.15,
                "E": 147.13, "Q": 146.15, "G": 75.07, "H": 155.16, "I": 131.17,
                "L": 131.17, "K": 146.19, "M": 149.21, "F": 165.19, "P": 115.13,
                "S": 105.09, "T": 119.12, "W": 204.23, "Y": 181.19, "V": 117.15
            }

            # Decide if DNA/RNA or protein by letters
            if all(base in dna_weights for base in seq):
                weight = sum(dna_weights.get(base, 0) for base in seq)
                result_label.config(text=f"Approximate DNA/RNA Molecular Weight: {weight:.2f} Da")
            elif all(aa in protein_weights for aa in seq):
                weight = sum(protein_weights.get(aa, 0) for aa in seq)
                result_label.config(text=f"Approximate Protein Molecular Weight: {weight:.2f} Da")
            else:
                result_label.config(text="Sequence contains invalid characters.")

        tk.Button(win, text="Calculate", command=compute).pack(pady=5)
        return win

    register_window("Molecular Weight Calculator", create_window)

import math

def open_ph_calculator(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("pH Calculator")

        tk.Label(win, text="Enter H⁺ concentration [mol/L] (leave blank if calculating pOH):").pack()
        h_entry = tk.Entry(win, width=30)
        h_entry.pack(pady=5)

        tk.Label(win, text="Enter OH⁻ concentration [mol/L] (leave blank if calculating pH):").pack()
        oh_entry = tk.Entry(win, width=30)
        oh_entry.pack(pady=5)

        result_label = tk.Label(win, text="")
        result_label.pack(pady=10)

        def compute():
            try:
                h_conc = h_entry.get().strip()
                oh_conc = oh_entry.get().strip()
                if h_conc and oh_conc:
                    result_label.config(text="Enter only one concentration at a time.")
                    return
                if h_conc:
                    h = float(h_conc)
                    if h <= 0:
                        raise ValueError
                    pH = -math.log10(h)
                    result_label.config(text=f"pH = {pH:.2f}")
                elif oh_conc:
                    oh = float(oh_conc)
                    if oh <= 0:
                        raise ValueError
                    pOH = -math.log10(oh)
                    pH = 14 - pOH
                    result_label.config(text=f"pOH = {pOH:.2f}, pH = {pH:.2f}")
                else:
                    result_label.config(text="Enter at least one concentration.")
            except:
                result_label.config(text="Invalid input.")

        tk.Button(win, text="Calculate", command=compute).pack(pady=5)
        return win

    register_window("pH Calculator", create_window)
import math

def open_population_growth_calculator(preload=None):
    def create_window():
        win = tk.Toplevel()
        win.title("Population Growth Calculator")

        tk.Label(win, text="Initial Population (N₀):").pack()
        n0_entry = tk.Entry(win, width=30)
        n0_entry.pack(pady=5)

        tk.Label(win, text="Growth Rate (r) [per time unit]:").pack()
        r_entry = tk.Entry(win, width=30)
        r_entry.pack(pady=5)

        tk.Label(win, text="Time (t):").pack()
        t_entry = tk.Entry(win, width=30)
        t_entry.pack(pady=5)

        result_label = tk.Label(win, text="")
        result_label.pack(pady=10)

        def compute():
            try:
                N0 = float(n0_entry.get())
                r = float(r_entry.get())
                t = float(t_entry.get())
                N = N0 * math.exp(r * t)
                result_label.config(text=f"Population after {t} time units: {N:.2f}")
                log_event("Population Growth Calculator", f"N0={N0}, r={r}, t={t}", N)
            except Exception as e:
                result_label.config(text=f"Error: {e}")

        tk.Button(win, text="Calculate", command=compute).pack(pady=5)
        return win

    register_window("Population Growth Calculator", create_window)

def open_bio_tools_hub(preload=None):
    def create_window():
        bio = tk.Toplevel()
        bio.title("Biology Tools")

        tk.Label(bio, text="Choose a Biology Tool:").pack(pady=10)
        choices = [
            "DNA Transcription & Translation",
            "Codon Lookup",
            "Osmosis & Tonicity",
            "Molecular Weight Calculator",
            "pH Calculator",
            "Population Growth Calculator",
        ]
        var = tk.StringVar()
        box = ttk.Combobox(bio, textvariable=var, values=choices, state="readonly")
        box.pack(pady=5)
        box.set("Select a Tool")

        def launch():
            selection = var.get()
            if selection == "DNA Transcription & Translation":
                open_transcription_tool()
            elif selection == "Codon Lookup":
                open_codon_lookup_tool()
            elif selection == "Osmosis & Tonicity":
                open_osmosis_tool()
            elif selection == "Molecular Weight Calculator":
                open_molecular_weight_calculator()
            elif selection == "pH Calculator":
                open_ph_calculator()
            elif selection == "Population Growth Calculator":
                open_population_growth_calculator()

        tk.Button(bio, text="Open", command=launch).pack(pady=10)
        return bio

    register_window(open_bio_tools_hub.__name__.replace("open_", "").replace("_", " ").title(), create_window)
