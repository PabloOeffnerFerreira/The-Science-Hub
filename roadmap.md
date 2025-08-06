# A Science Hub – Tool Rewrite Roadmap

This document outlines the rewrite plan for each tool included in A Science Hub. For each tool, the goals, changes, and features are listed clearly and concisely. This file is meant to evolve with development.

---

## Unit Converter

**Status**: Keep and improve

### Purpose
Convert values between physical and scientific units, across a wide set of categories. Used both as a standalone calculator and as a chained helper in other tools.

### Improvements
- Separate logic, data, and UI into different files/modules
- Support for scientific notation input
- Searchable unit selection dropdowns
- Realtime result updates (no button required)
- Flip input/output units button
- Input validation with error hints
- Support for chaining into other tools (returns numeric result + unit)
- Log to central session
- Optionally export conversion results
- Session history list (optional)
- Centralized result formatting with sig figs or decimal control

### Output / Export
- String output (e.g. "3.5 km = 3500 m")
- JSON for chaining and structured use
- Can generate preview image if needed (optional)

---

<!-- Next tool starts below -->