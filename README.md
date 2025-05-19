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
> **Performance:** Local models can be slow depending on your hardware. Lighter models are available and automatically suggested.

### What can the AI do?

- Answer science questions in natural language.
- Summarize your experiment logs or data.
- Explain concepts or formulas step by step (“Learn” mode).
- Give direct answers for fast lookups (“Use” mode).
- Chat naturally and help brainstorm ideas (“Casual” mode).
- Understand and suggest built-in tools in Science Hub.
- Fully runs offline. No cloud. No accounts. Just local compute.

### Model Management Features (NEW)

- **Dolphin3:8b** is now the default assistant model, selected for its balanced speed and reasoning across all systems.
- **Model Hover Tooltips:** When choosing a model, hover to see a quick description of what it does best and its hardware requirements.
- **Wide Range of Models:** From ultra-light (`tinyllama:1.1b`) to advanced logic models (`phi4-reasoning:14b`), with full control over speed vs intelligence.

### Hardware requirements

- **Recommended:**  
  12–16 GB RAM, 8+ GB VRAM (for mid-size models like Dolphin3, Qwen3:8b, or Phi4).
- **Minimum:**  
  8 GB RAM, 4 GB VRAM — use lighter models like `gemma3:2b`, `phi4-mini:3.8b`, or `tinyllama:1.1b`.

### How to enable AI assistant

1. **Install Ollama:**  
   [Download Ollama](https://ollama.com/download) and install it (Windows, Mac, or Linux).
2. **Pull a model:**  
   In your terminal, run  
   ```sh
   ollama pull dolphin3:8b


(or try others: `mathstral:7b`, `codegemma:2b`, `phi4-reasoning:14b`, etc.)
3\. **Set up Science Hub as usual.**
4\. **Launch the AI Assistant from the main window.**
5\. **Choose your model and mode** (Learn, Use, Casual) in the chatbox.
6\. \*\*Ask questions, get explanations, and explore science with 100% local LLMs.

> Emojis are automatically removed to keep the interface clean and consistent across platforms.

### Models:

#### `dolphin3:8b`  
A highly balanced model for general-purpose science interaction, combining fluent language output with strong logic and contextual awareness. Works well in all three modes (Learn, Use, Casual), making it the default model for most users. Good performance on systems with 8–12 GB RAM and a mid-range GPU.

#### `gemma3:12b`  
Large and accurate, ideal for detailed step-by-step explanations in Learn mode. Handles scientific reasoning with clarity, but requires a system with significant RAM and VRAM. Use when performance isn’t a concern and quality is top priority.

#### `qwen3:14b`  
An advanced multilingual reasoning model by Alibaba, suitable for deep factual knowledge, logic chains, and high-accuracy science questions. It is very slow on most machines and best reserved for top-end systems with plenty of RAM and GPU bandwidth.

#### `deepseek-r1:14b`  
Designed to mimic OpenAI’s GPT-style reasoning with strong performance in deduction and long-form explanation. Especially good for complex reasoning tasks or when reviewing multi-step answers. Heavy on resources, like qwen3:14b.

#### `mistral-small3.1`  
A lightweight yet surprisingly capable model that supports long context (up to 128k tokens). Fast to load and good for day-to-day queries. Best suited for users on laptops or CPUs who still want decent fluency and science output.

#### `qwen3:8b`  
A great middle-tier model that offers a good blend of response quality and performance. Suitable for more complex prompts without overwhelming slower systems. Especially good for structured replies and formal tones.

#### `gemma3:4b`  
Compact, efficient, and surprisingly accurate for its size. Great choice for direct answers or light reasoning tasks. Recommended for laptops or devices with limited VRAM.

#### `phi4-mini:3.8b`  
Extremely fast and lightweight, built for reasoning at scale on weak hardware. Handles factual answers and light logic chains very well. Ideal fallback model when speed matters more than detail.

#### `gemma3:2b`  
Ultra-light and very fast to load. Good for short, simple replies or fallback use on systems without a GPU. Use for casual queries or minimal science interaction when resources are scarce.

#### `tinyllama:1.1b`  
The absolute lightest model included. While it lacks reasoning power, it’s extremely fast and functional for basic natural language responses or simple definitions. Great for testing, diagnostics, or fallback when nothing else loads.

#### `phi4:14b`  
Microsoft’s most advanced open model for reasoning and factual accuracy. It’s large and slow, but excellent in Learn mode or when detailed breakdowns are needed in math, logic, or concept clarification.

#### `phi4-reasoning:14b`  
A variant of Phi-4 focused entirely on logical problem solving, calculations, and multi-step science tasks. Ideal for use in tutoring-style interactions or when verifying scientific reasoning.

#### `mathstral:7b`  
A Mistral-tuned model dedicated to math and science logic. Best for formula explanation, symbolic reasoning, unit conversion breakdowns, and math-heavy prompts. Good performance on mid-range setups.

#### `deepseek-r1:7b`  
A smaller sibling to the 14B version with much faster response time and reduced memory usage. Keeps most of its logical strengths and works well across all AI modes.

#### `codegemma:2b`  
Fast-loading coding assistant focused on Python, scripting, and basic logic generation. Useful for tool expansion, AI script help, or lightweight logic debugging. Friendly to low-end machines.

#### `codegemma:7b`  
A stronger code-focused model with better reasoning and cleaner completions. Great for extending Science Hub with new Python tools or writing helper functions. Works well with modern GPUs and mid-tier laptops.

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
