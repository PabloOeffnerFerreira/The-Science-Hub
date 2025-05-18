import tkinter as tk
from rdkit import Chem
from rdkit.Chem import Draw
from PIL import Image, ImageTk
import io
import urllib.parse
import urllib.request

import sys
import os
from contextlib import contextmanager

@contextmanager
def suppress_rdkit_warnings():
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    os.dup2(devnull, 2)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(devnull)
        os.close(old_stderr)

SMILES_URL_TEMPLATE = 'http://cactus.nci.nih.gov/chemical/structure/{}/smiles'

def iupac2smiles(iupac_name):
    quoted = urllib.parse.quote(iupac_name)
    url = SMILES_URL_TEMPLATE.format(quoted)
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.read().decode('utf-8')

def open_molecule_assembler():
    win = tk.Toplevel()
    win.title("Molecule Assembler with RDKit & CACTUS")

    tk.Label(win, text="Enter SMILES or IUPAC name:").pack(pady=5)
    entry = tk.Entry(win, width=40)
    entry.pack(pady=5)

    img_label = tk.Label(win)
    img_label.pack(pady=10)

    def draw():
        inp = entry.get().strip()
        if not inp:
            return

        with suppress_rdkit_warnings():
            mol = Chem.MolFromSmiles(inp)

        if mol is None:
            try:
                smiles = iupac2smiles(inp)
                with suppress_rdkit_warnings():
                    mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    img_label.config(text="Could not parse molecule.")
                    return
            except Exception as e:
                img_label.config(text=f"Error retrieving SMILES: {e}")
                return

        Chem.rdDepictor.Compute2DCoords(mol)

        Chem.rdDepictor.Compute2DCoords(mol)
        img = Draw.MolToImage(mol, size=(400, 400))
        bio = io.BytesIO()
        img.save(bio, format='PNG')
        bio.seek(0)
        img_tk = ImageTk.PhotoImage(data=bio.read())
        img_label.config(image=img_tk)
        img_label.image = img_tk

    tk.Button(win, text="Draw Molecule", command=draw).pack(pady=5)

    return win