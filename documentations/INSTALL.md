# Science Hub Installation Guide (English)

Welcome to Science Hub!  
This guide will help you set up Science Hub on your computer quickly and easily.

Science Hub is a platform for learning and doing science, combining tools, a structured library, image management, and a local AI assistant—all running privately on your own PC, with no cloud required.

---

## Requirements

- **Operating System:** Windows 10 or 11 (also works on Linux and macOS)
- **Memory:** 8 GB RAM (16 GB or more recommended)
- **Graphics Card:** At least 4 GB VRAM (8 GB+ recommended for larger AI models)
- **Python:** Version 3.13.3 (recommended), but any version above 3.10 should work
- **Git:** Required to download the code (see below)
- **Ollama:** Only needed if you want to use the AI Assistant (see extra step below)

---

## Step-by-Step Installation

### 1. Install Python

If you don't already have Python:
- Go to: https://www.python.org/downloads/windows/
- Download **Python 3.13.3**
- During installation, check the box "Add Python to PATH"

### 2. Install Git (if you need it)

- Download from: https://git-scm.com/download/win
- Install as usual

### 3. Download Science Hub

Open **Command Prompt** (or **Terminal**) and type:

```sh
git clone https://github.com/PabloOeffnerFerreira/The-Science-Hub.git
cd The-Science-Hub
````

### 4. (Optional, but recommended) Create a Virtual Environment

This helps avoid conflicts with other Python programs.

```sh
python -m venv venv
venv\Scripts\activate
```

On Linux or Mac:

```sh
source venv/bin/activate
```

### 5. Install Dependencies

In the project folder, run:

```sh
pip install -r requirements.txt
pip install Pillow tkinterdnd2
```

If you get errors about missing packages, try upgrading pip:

```sh
python -m pip install --upgrade pip
```

### 6. (Optional) Install RDKit

RDKit is needed for some chemistry tools:

```sh
conda install -c conda-forge rdkit
```

(You'll need [Anaconda or Miniconda](https://docs.conda.io/en/latest/miniconda.html) for this)

### 7. (Optional) Install Ollama for AI Assistant

If you want to use the AI Assistant offline:

* Go to: [https://ollama.com/download](https://ollama.com/download)
* Download and install for your OS
* After installing, open your terminal and pull a model, for example:

```sh
ollama pull dolphin3:8b
ollama pull tinyllama:1.1b
```

### 8. Run Science Hub

In the project folder, run:

```sh
python hub.py
```

---

## Tips and Troubleshooting

* **"pip" not recognized:** Open a new terminal window or restart your computer.
* **Permission errors:** Try opening Command Prompt as Administrator.
* **Problems installing packages:** Make sure your virtual environment is activated and Python is in your PATH.
* **Something not working?**
  Don’t worry—contact Pablo (the developer) directly for help!

---

## More Information

* Science Hub saves your libraries and images locally—nothing is lost if you close the program.
* The AI Assistant only works if Ollama is running and you have pulled at least one model.
* Want to learn more or contribute? Visit the GitHub page:
  [https://github.com/PabloOeffnerFerreira/The-Science-Hub](https://github.com/PabloOeffnerFerreira/The-Science-Hub)

---

*If you have any questions, just ask!*
