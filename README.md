# FOS Engine - Solid Motor Design Software

**FOS Engine** is a production-grade Internal Ballistics Simulator for amateur solid rocket motors. It is designed to help engineers and hobbyists design, simulate, and verify solid motors (specifically Sugar Rockets like KNSB/KNDX) using standard engineering principles.

## Features

*   **Propellant Library:** Pre-loaded with standard KNSB data (Nakka). Customizable burn rate parameters ($a$, $n$), density, and $c^*$.
*   **Grain Design:** BATES grain geometry solver. Calculates burning area evolution ($A_b$ vs $x$).
*   **Hardware Safety:** Checks casing Burst Pressure and Kn (Klemmung Number).
*   **Advanced Simulation:**
    *   **Runge-Kutta (RK4)** time-stepping physics engine.
    *   **Isentropic Flow** Thrust Coefficient ($C_f$) solver.
    *   **Erosive Burning** (Flux-based) and **Nozzle Erosion** models.
    *   **Lagrange Gradient** correction for head-end pressure safety.
*   **Export:** Generate `.eng` files compatible with OpenRocket.

## Installation

### Prerequisites
*   Python 3.8+
*   Pip

### Install via Pip (Local)
```bash
git clone https://github.com/yourusername/fos_engine.git
cd fos_engine
pip install .
```

### Development Setup
```bash
pip install -r requirements.txt
python main.py
```

## Usage

1.  **Run the Application:**
    ```bash
    fos-engine
    # OR if running from source
    python main.py
    ```
2.  **Workflow:**
    *   **Tab 1 (Propellant):** Select "KNSB" or enter custom fuel data.
    *   **Tab 2 (Grain):** Define your BATES grain geometry (OD, Core ID, Length, Count).
    *   **Tab 3 (Hardware):** Define Nozzle Throat/Exit and Casing dimensions.
    *   **Tab 4 (Simulation):** Click "Run Simulation". View Thrust/Pressure curves.
    *   **Safety Check:** Ensure the Red Pressure Curve (Head-End) stays below the Black Dashed Line (Burst Pressure).

## Theory
The engine uses **Saint Robert's Law** ($r = aP^n$) coupled with the mass conservation equation:
$$ V_c \frac{dP}{dt} = (\dot{m}_{gen} - \dot{m}_{out}) \frac{RT}{V_{free}} $$
Thrust is calculated using Isentropic Flow theory, solving for Exit Mach number iteratively.

## License
MIT License.
