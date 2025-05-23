# The Science Hub

![Main Image](images/Main.png)

---

## What is Science Hub?

**Science Hub** is a modular, offline science platform built for learning, experimenting, researching, visualizing, and organizing scientific concepts on your computer, with dedicated tools, a fully local AI assistant, and complete data integration.

You can simulate phenomena, solve problems in physics, chemistry, biology, geology, and math, save results, organize formulas, manage scientific images, and search for articles—all in a single system designed to let you explore science your way.

---
- [README em Português Brasileiro](README.pt-BR.md)
---

## Main Features

- **Science Library:** Register, search, and filter your own formulas, concepts, descriptions, images, and tags. Create your personal science encyclopedia, with batch export/import and smart linking.
- **Results Gallery:** Manage, view, and organize images, charts, experiment outputs, and results, all with favorites, tags, and automatic metadata.
- **Molecular Search:** Find compounds using PubChem, view structures, formulas, and detailed data.
- **Academic Search:** Find scientific articles directly via OpenAlex, including title, authors, DOI, abstract, and open-access links.
- **Local AI Assistant:** A true science assistant running offline via Ollama, with multiple models and modes (explanation, direct answer, or casual conversation).
- **Full Integration:** All tools, results, and references are connected—save, share, export, and retrieve your discoveries with ease.
- **Chain Mode:** Tools can pass outputs directly between each other to build custom workflows.
- **Modern Interface:** Fully redesigned in PyQt6 with unified layouts, reliable error handling, smart filtering and a persistent dark theme.
- **Code Editor:** Write, run, and test Python code with syntax highlighting, embedded terminal, and offline AI code generation using Qwen models.

---

## Included Tools

Every tool launches in its own window and can be used independently. Most support preload, result saving, and chaining. They cover the most essential areas of science.  
Here are the main included tools, grouped by subject:


### Math & Physics

- **Simple Calculator** – Preload-enabled, now supports Chain Mode.
- **Quadratic Solver** – Solves quadratic equations, error-handled.
- **Triangle Solver** – Basic trigonometric resolution.
- **Function Plotter** – Improved visuals; interactive graphing.
- **Projectile Motion** – Full input validation, output logging.
- **Terminal Velocity** – Calculates final speed with air drag.
- **Speed, Force, Acceleration, Kinetic Energy** – Classical mechanics pack.
- **Ohm’s Law** – Voltage-current-resistance calculator.
- **Lens & Mirror Equation** – Optical modeling.
- **Unit Converter** – Between physical and scientific units.
- **Unit Multiplier** – Mass, moles, volume (STP) from any two values.
- **Property Grapher** – Interactive element graphs, hover data.
- **Comparator Tool** – Property comparison between elements.
- **Algebric Calculator** - Simplify and calculate algebric function
- **Scientific Notation Converter** - Convert decimal Numbers to scientific notation and vice versa.
- **Half-Life Calculator** – Calculate remaining quantity based on half-life and elapsed time, with optional decay plot.
- **Vector Calculator** – Perform vector operations such as dot product, cross product, magnitude, normalization, and angle calculation, with optional 3D plot.

### Chemistry

- **Element Viewer** – Searchable periodic table with favourites.
- **Isotopic Notation Tool** – Preload, neutron/proton view.
- **Shell Visualiser** – Electron shell output with image export.
- **Phase Predictor** – Predicts states using atomic data.
- **Molecular Assembler** – Draws molecules from IUPAC/SMILES.
- **Molecular Weight Calculator** – Basic formula weight tool.

### Biology

- **Transcription Tool**
- **Codon Lookup**
- **GC Content Tool**
- **Reverse Complement**
- **Translate DNA Tool**
- **Sequence File Parser**
- **Pairwise Alignment Tool**
- **Population Growth Calculator**
- **pH Calculator**

*(All adapted for PyQt6 and preload/chain support where relevant.)*

### Geology

- **Mineral Explorer** – Highlight, sort, and favourite entries.
- **Radioactive Dating**
- **Plate Velocity**
- **Mineral ID Tool**


### Miscellaneous

- **Code Editor** – Full Python editor with an embedded terminal and local code generation.
- **Window Manager** – List and focus or close any open Science Hub window.
- **Log Exporter** – Save your session history directly to Markdown.
- **Molecule Library** – Search PubChem and keep molecule data offline.
- **OpenAlex Browser** – Dedicated interface for exploring scientific articles.
- **Settings** – Configure options like clearing logs on startup.
- **Chain Mode Log Viewer** – See saved workflow outputs.

---

## Supported AI Models

Science Hub integrates multiple AI models via Ollama, working **100% offline** on your computer.  
Available models include:

- **TinyLlama:** Ultra-fast, perfect for short answers and simple tasks.
- **Phi4, Phi4-Reasoning:** Logic analysis and mathematical problem solving.
- **Phi4-Mini:** Lightweight version for quick reasoning.
- **Dolphin3:** General chat and science.
- **Qwen3:** Advanced language modeling.
- **Gemma3:** Lightweight and efficient for scientific dialogue.
- **DeepSeek-R1:** Reasoning-focused models in 7B and 14B sizes.
- **Mistral Small 3.1:** Fast and fluent with long context.
- **Mathstral:** Advanced math and calculation solving.
- **Code Assistants:** Specific models for programming and scientific automation.

You can switch models at any time, track token usage live, and load previous conversations.

---
## How to Install

**Science Hub** is distributed as a standalone Windows executable (`.exe`).  
Follow these steps to set up and run the program.

---

### 1. Install Ollama (Required for AI Assistant)

Science Hub’s AI features rely on [Ollama](https://ollama.com/).  
Ollama must be installed and running before you launch Science Hub.

- Download and install Ollama for Windows from:  
  [https://ollama.com/download](https://ollama.com/download)

- After installation, run Ollama. It should stay active in the background.

---

### 2. Download Science Hub

- Download the latest Science Hub release ZIP (or EXE) from the [releases page](https://github.com/PabloOeffnerFerreira/The-Science-Hub/releases).

- Extract the ZIP file to any folder on your computer.

- The extracted folder must contain:
    - The main `ScienceHub.exe` (or similar)
    - All required folders:  
      `results`, `exports`, `codes`, `logs`, `interndatabases`, `databases`, `screenshots`, `images`, `gallery`
    - All `.md` and `.py` files in the root (even if just for reference).

---

### 3. Run Science Hub

- **Double-click** the `ScienceHub.exe` file in the extracted folder.

- On first launch, the app may take a few seconds to start as it sets up.

- **Important:** Ollama must be running before you open Science Hub, otherwise AI features will not work.

---

### 4. Troubleshooting

- If the program fails to start or you get errors about missing files, make sure all the required folders and files are present in the same folder as the EXE.

- If you see errors related to Ollama, confirm that the Ollama service is running (you can check in Task Manager, or by visiting [http://localhost:11434/](http://localhost:11434/) in your browser).

---

### 5. Updates

- Check for new versions or bug fixes on the [Science Hub GitHub releases page](https://github.com/PabloOeffnerFerreira/The-Science-Hub/releases).

---

## Screenshots

![Main Window](screenshots/main_window.png)  
*Science Hub main window*

![Scientific Gallery](screenshots/screenshot_gallery.png)  
*Gallery of scientific images, results, and experiments*

![Science Library](screenshots/screenshot_library.png)  
*Library for formulas, concepts, tags, and descriptions*

![AI Assistant](screenshots/AI.png)  
*Local offline AI assistant integrated into Science Hub*

![Mineral Explorer](screenshots/screenshot_mineral_explorer.png)
*Huge Database checker for mineral info*

![Code Editor](screenshots/screenshot_code_editor.png)
*Your very own IDE with integrated shell, terminal and coding AI assistance*
---

## Learn More

- [README em Português Brasileiro](README.pt-BR.md)
- [Guia de Instalação em Português](documentations/INSTALL.pt-BR.md)
- [English Install Guide](documentations/INSTALL.md)
- Report issues or suggest improvements at: [GitHub Issues](https://github.com/PabloOeffnerFerreira/The-Science-Hub/issues)

---

*Science Hub is not just a chatbot—it’s a complete science system for deep curiosity, serious study, and real experimentation, built to work your way.*
