# The Science Hub

A versatile, cross-discipline tool for learning, experimenting, and doing science with Python—now with an optional offline AI assistant.

![MainImage](images/Main.png)

---

## What is The Science Hub?

**The Science Hub** is a modular, self-built desktop application designed to collect, organize, and extend a set of scientific tools under one easy interface.  
Originally a personal project for independent learning, it has grown into a powerful platform for chemistry, biology, math, physics, geology, and now, AI-powered study and exploration.

Whether you want to calculate, visualize, manage results, or ask questions to an AI—**The Science Hub adapts to your workflow.**

---

## Features

- **Science Library:**  
  Organize, search, and filter your own formulas, concepts, notes, and references. Attach images and link entries to experiments.

- **Gallery:**  
  Asset manager for all scientific images (plots, diagrams, experiment photos). Drag-and-drop, tagging, favorites, renaming.

- **Tool Launcher:**  
  Instant access to a growing suite of calculators and utilities: chemistry (molar mass, molecular visualizer), math, physics, biology, geology, and more.

- **Result Storage:**  
  Store and organize generated plots and outputs for reference. Easily connect images to library entries.

- **Batch Import/Export:**  
  Import/export multiple entries and images for backup, sharing, or migration.

- **Customizable & Extensible:**  
  Modular design—add new tools as Python scripts with minimal setup.

- **Integrated Offline AI Assistant (NEW!):**  
  Powered by [Ollama](https://ollama.com/), Science Hub now includes an optional AI assistant that runs entirely on your machine, with no cloud or account needed. The assistant can answer questions, check your work, explain solutions, or simply provide quick facts—with full privacy and customizable modes.

---

## NEW: AI Assistant (Ollama Integration)

> **Note:** The AI assistant is fully optional and only uses system resources (RAM/VRAM) when active.  
> **Performance:** While it works entirely offline, it can be **quite slow**—especially with larger models. This is expected and depends heavily on your hardware.

### What can the AI do?

- Answer science questions in natural language.
- Summarize your experiment logs or data.
- Explain concepts or formulas step by step (“Learn” mode).
- Give direct answers for fast lookups (“Use” mode).
- Chat naturally and help brainstorm ideas (“Casual” mode).
- Understand and suggest built-in tools in Science Hub.

### Hardware requirements

- **Recommended:**  
  12–16 GB RAM, 8+ GB VRAM (for mid-size models like Gemma 4B/12B or Qwen3).
- **Minimum:**  
  8 GB RAM, 4 GB VRAM (use lighter models, fewer features).
- Runs best on systems with modern CPUs and GPUs (NVIDIA or AMD with recent drivers).

### How to enable AI assistant

1. **Install Ollama:**  
   [Download Ollama](https://ollama.com/download) and install it (Windows, Mac, or Linux).
2. **Pull a model:**  
   In your terminal, run  
```

ollama pull gemma3:4b

````
(or try other models: `gemma3:12b`, `qwen3:14b`, etc.)
3. **Set up Science Hub as usual.**
4. **Launch the AI Assistant from the main window.**
5. **Choose your model and mode** (Learn, Use, Casual) in the chatbox.
6. **Ask questions, get explanations, and explore science with LLMs running 100% locally.

---

## Quick Start

_**See above for AI-specific setup.**_

1. **Clone the repository:**
```sh
git clone https://github.com/PabloOeffnerFerreira/The-Science-Hub.git
cd The-Science-Hub
````

2. **(Optional) Create a virtual environment:**

   ```sh
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Install dependencies:**

   ```sh
   pip install Pillow tkinterdnd2
   # and (optional for chemistry) conda install -c conda-forge rdkit
   ```

4. **Run the app:**

   ```sh
   python hub.py
   ```

---

## Toolkits & Modules

* **Chemistry Toolkit:** Molar mass calculator, shell visualizer, isotope tools, and more.
* **Physics Toolkit:** Unit converter, kinematics calculators, energy tools.
* **Biology Toolkit:** DNA/RNA tools, molecular weight, pH calculator.
* **Geology Toolkit:** Mineral explorer, plate tectonics calculators.
* **Math Toolkit:** Function plotter, equation solvers.

---

## Extending The Science Hub

* Add new Python tools/scripts.
* Register in `hub.py`.
* Outputs and images integrate with Gallery and Results folders.

---

## Screenshots

![Main window](screenshots/main_window.png)
![Gallery](screenshots/screenshot_gallery.png)
![Science Library](screenshots/screenshot_library.png)
![AI Assistant](screenshots/AI.png)

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Support

Open issues or suggestions on [GitHub](https://github.com/PabloOeffnerFerreira/The-Science-Hub/issues).

---

*Enjoy building, learning, and exploring—with or without AI. Science Hub adapts to your curiosity.*
