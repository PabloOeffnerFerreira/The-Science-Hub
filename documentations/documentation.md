# Overview of Science Hub
![Science Hub Main Window](images/Main.png)

Science Hub is a modular, desktop-based software platform designed to unify scientific tools, data management, and AI assistance into a single environment for scientific workflows spanning physics, chemistry, biology, geology, mathematics, and programming. It supports independent tool operation and chaining for complex tasks. The platform emphasizes modularity, expandability, and user control.

## Purpose and Scope
Science Hub provides users with tools to perform scientific calculations, organize formulas, manage experimental results and images, search scientific literature, and write and execute Python code. It aims to reduce reliance on multiple separate applications or web services by integrating these functions cohesively.

## User Interface and Experience
The interface features a dark theme with a clean, structured layout designed for efficiency and minimal distraction. Tools open in separate windows with consistent UI elements. Users can customize workflows by chaining outputs between tools. User actions are logged, and session histories can be exported for reproducibility.

## Scientific Domains Covered
- **Physics**: Calculators for mechanics, optics, thermodynamics; unit converters; vector operations.
- **Chemistry**: Periodic table explorer, molecular weight calculator, isotopic notation, molecular assembler.
- **Biology**: DNA/RNA sequence analysis, population growth, codon lookup, transcription tools.
- **Geology**: Mineral identification, radioactive dating, plate velocity calculation.
- **Mathematics & Programming**: Equation solvers, function plotters, code editor with embedded terminal.

## Extensibility and Licensing
The platform is designed for easy expansion. Users can add new tools or extend existing ones, with Python scripting supported via the integrated code editor. Science Hub is MIT licensed, allowing free personal and research use with attribution required for commercial applications.

# Chapter 1: Tools
**In the following chapter is every tool explained.**

## Unit Converter

The Unit Converter is a tool designed to perform conversions between a wide variety of scientific and everyday units across multiple categories. It provides precise and flexible unit conversion functionality as part of the Science Hub’s modular toolset.

### Supported Categories and Units

The converter supports a broad range of unit categories including but not limited to:

- Length (meters, kilometers, miles, light years, parsecs, etc.)  
- Mass (kilograms, grams, pounds, atomic mass units, solar masses, etc.)  
- Time (seconds, minutes, hours, years, centuries, etc.)  
- Temperature (Celsius, Fahrenheit, Kelvin)  
- Area (square meters, hectares, acres, square miles)  
- Volume (cubic meters, liters, gallons, cups)  
- Speed (meters per second, miles per hour, knots, speed of light)  
- Pressure (pascals, atmospheres, bars, psi)  
- Energy (joules, calories, electronvolts, BTU)  
- Power (watts, horsepower, BTU per hour)  
- Electric units (charge, potential, current)  
- Frequency (hertz, kilohertz, rpm)  
- Data size (bits, bytes, kilobytes, megabytes)  
- And more categories such as force, angle, fuel consumption, magnetic field, illuminance, and radioactivity.

### Functionality

- Users select a category, then choose the input unit ("From") and output unit ("To").  
- Input values are accepted as decimal numbers.  
- Temperature conversions apply custom formulas to handle differences between Celsius, Fahrenheit, and Kelvin scales.  
- All other conversions use a base unit factor system, converting input values to a base unit and then to the target unit.  
- The converter displays the result with four decimal places for precision.  
- Invalid inputs or unsupported conversions trigger informative error messages.  
- The interface supports quick updating of units when the category changes.

### User Interface

- The converter opens in a dedicated window with dropdown menus for category and units.  
- A text field accepts the value to convert.  
- The result appears below the input area after conversion.  
- A "Convert" button initiates the calculation.  
- Unit selections update dynamically based on the chosen category.

### Integration

- The Unit Converter supports chaining with other tools in Science Hub, allowing its output to feed into subsequent calculations or analyses.  
- Conversion logs can be saved or exported along with session data for reproducibility.  
- The tool is implemented using PyQt and follows the platform’s consistent UI style and theme.

---

*(Add screenshot of the Unit Converter interface here)*  
