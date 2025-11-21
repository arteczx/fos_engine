# FOS Engine - Coding Standards & Conventions

## Unit Systems
*   **Internal Calculations (Core):** All physics calculations inside `fos_engine/core` MUST use **SI Units** (MKS: Meters, Kilograms, Seconds, Pascals, Newtons).
*   **User Interface (GUI):** The UI should display and accept values in **Rocketry Standard** units:
    *   Length: Millimeters (mm)
    *   Pressure: PSI
    *   Force/Thrust: Newtons (N) or lbf (if specified) - Default to Newtons for plots usually, but check user reqs. (Plan says N for output, psi for pressure).
    *   Mass: Grams or Kilograms
    *   Density: g/cm³
*   **Conversion:** Use `fos_engine/core/units.py` for all conversions. Do not hardcode magic numbers like `6894.76` (PSI to Pa) inline.

## Code Structure
*   **Core:** Pure logic. No PyQt imports allowed here.
*   **GUI:** Visualization and Input handling. Imports Core.
*   **Utils:** Helpers.

## Documentation
*   Docstrings for all public methods, especially describing input/output units.
