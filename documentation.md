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

![Unit Converter for Pressure](screenshots/screenshot_unit_converter.png)

---

## Terminal Velocity Calculator

The Terminal Velocity Calculator estimates the terminal velocity and fall time of an object dropped from a given height, considering air resistance with customizable parameters.

### Inputs

- **Mass:** The mass of the object. Users can input the value and select units (`kg` or `lb`). Internally converted to kilograms.
- **Cross-sectional Area:** The effective area facing airflow. Users input the value and select units (`m²`, `cm²`, or `in²`). Internally converted to square meters.
- **Height:** The drop height. Input value with unit options (`m` or `ft`). Internally converted to meters.
- **Air Density or Altitude:**
  - User can choose to enter the air density directly (`kg/m³`),
  - or provide the altitude in meters to compute air density using a simplified barometric formula,
  - or enter a custom air density value.
- **Drag Coefficient:** Select from presets corresponding to common shapes:
  - Sphere (0.47),
  - Flat Plate (1.28),
  - Cylinder (1.2),
  - Streamlined Body (0.04),
  - or input a custom drag coefficient.

### Calculations

- **Terminal Velocity:** Calculated using the formula  
  \[
  v = \sqrt{\frac{2 m g}{\rho A C_d}}
  \]
  where \(m\) is mass, \(g\) is gravity, \(\rho\) is air density, \(A\) is cross-sectional area, and \(C_d\) is drag coefficient.
  
- **Fall Time with Drag:** Numerically estimated by integrating the equations of motion considering gravitational force and drag force, using a small time step for accuracy.

- **Fall Time without Drag:** Calculated by the standard formula \(t = \sqrt{\frac{2 h}{g}}\) for reference.

### Outputs

- Terminal velocity (m/s)
- Fall time with drag (s)
- Fall time without drag (s)
- A velocity vs. time plot illustrating how velocity approaches terminal velocity during the fall.

### Plot Export

- The velocity vs. time plot is automatically saved as a PNG image in the user’s results directory.
- The filename includes a timestamp, e.g., `terminal_velocity_20250520_153045.png`.
- The saved plot path is displayed alongside calculation results.
- The export process is integrated with the platform’s logging system to record the event.

### User Interface

- Input fields paired with unit selectors provide flexibility and reduce errors.
- Dropdown menus allow easy selection of air density mode and drag coefficient presets.
- The plot updates dynamically upon calculation.
- Clear error messages are shown for invalid inputs.

### Integration

- The calculator supports logging and session export as part of Science Hub’s unified environment.
- The saved plot can be referenced or used in reports, presentations, or further analysis.

---

[Terminal Velocity Calculator](screenshots/screenshot_terminal_velocity_calc.png)

## Projectile Motion Tool

The Projectile Motion tool calculates the trajectory and key parameters of a projectile launched at an initial velocity and angle from a specified height.

### Features

- Input initial velocity with units (m/s, km/h, mph)  
- Input launch angle with units (degrees, radians)  
- Input initial height above ground with units (meters, feet)  
- Calculates:  
  - Range  
  - Maximum height  
  - Total flight time  
  - Time to maximum height  
  - Impact velocity magnitude and components  
- Plots the projectile trajectory (horizontal distance vs. height)  
- Includes an animation of the projectile motion on the plot  
- Automatically saves the trajectory plot as a PNG image in the results folder with a timestamped filename  
- Logs calculation details and export events for reproducibility  

### User Interface

The tool provides labeled input fields with unit selectors, a results display area, and an embedded matplotlib plot. Buttons allow calculation and animation control.

### Usage Notes

- Ensure inputs are valid numbers; units are automatically converted to SI for calculations.  
- The animation visualizes the projectile’s path based on the calculated trajectory points.  
- The exported plot file path is shown in the results area after calculation.

---

[Projectile Motion Tool during an Animation](screenshots/screenshot_proj_mot.png)
