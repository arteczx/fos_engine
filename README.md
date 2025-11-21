# FOS Engine

**FOS Engine** is a high-fidelity **Internal Ballistics Simulator** for solid rocket motors. Designed for amateur rocketeers and engineers, it provides a comprehensive suite of tools to design, visualize, and simulate solid propellant motors (specifically KNSB/KNDX sugar rockets and APCP) using standard engineering physics.

![FOS Engine](https://img.shields.io/badge/Status-Production%20Ready-green) ![License](https://img.shields.io/badge/License-MIT-blue) ![Python](https://img.shields.io/badge/Python-3.8%2B-yellow)

---

## 🚀 Key Features

### 1. Advanced Physics Engine
*   **Runge-Kutta 4 (RK4) Solver:** High-precision time-stepping simulation that solves the non-linear differential equations of internal ballistics.
*   **Isentropic Flow Model:** Iteratively solves for Exit Mach number ($M_e$) using Newton-Raphson methods to calculate accurate Thrust Coefficients ($C_f$), rather than relying on simple approximations.
*   **Ignition Modeling:** Simulates the startup transient using an igniter mass flux model.

### 2. Complex Grain Geometries
*   **BATES:** Standard multiple-segment cylindrical grains.
*   **Star (Finocyl):** Simulate complex progressive/regressive burn profiles with Star grain geometry.
*   **Visualizer:** Real-time cross-section visualization with an interactive burn-back slider to inspect propellant consumption.

### 3. Safety & Reliability
*   **Burst Pressure Analysis:** Calculates casing safety margins (Hoop Stress) and overlays limits on pressure plots.
*   **Lagrange Gradient:** Automatically estimates Head-End Pressure ($P_{head} \approx 1.05 \times P_{chamber}$) to ensure forward closure safety.
*   **Erosive Burning:** Implements a mass-flux threshold model ($G > G_{crit}$) to predict dangerous pressure spikes in high L/D motors.

### 4. Workflow Integration
*   **Propellant Database:** Pre-loaded with Richard Nakka's experimental data for KNSB (Sugar/Nitrate).
*   **OpenRocket Export:** Generates `.eng` (RASP) files to immediately fly your design in flight simulators.
*   **Efficiency Tuning:** Fine-tune models with Combustion Efficiency ($\eta_{c^*}$) and Nozzle Efficiency factors.

---

## 📦 Installation

### Prerequisites
*   Python 3.8 or higher
*   `pip` (Python Package Installer)

### Installation (User)
To install FOS Engine as a package:

```bash
git clone https://github.com/yourusername/fos_engine.git
cd fos_engine
pip install .
```

Then run it from anywhere:
```bash
fos-engine
```

### Installation (Developer)
If you want to modify the code:

```bash
git clone https://github.com/yourusername/fos_engine.git
cd fos_engine
pip install -r requirements.txt
```

Run the app:
```bash
python main.py
```

---

## 📚 Theory Reference

FOS Engine is built on the fundamental conservation laws of fluid dynamics and thermodynamics.

### 1. Burn Rate (Saint Robert's Law)
The regression rate $r$ of the solid propellant is modeled as a function of chamber pressure $P_c$:

$$ r = a \cdot P_c^n $$

*   $a$: Burn rate coefficient (temperature dependent).
*   $n$: Pressure exponent (stability requires $n < 1$).
*   **Erosive Burning:** If the mass flux $G$ through the core exceeds a critical value $G_{crit}$, the burn rate is enhanced:
    $$ r_{total} = r_{base} \cdot [1 + k(G - G_{crit})] $$

### 2. Mass Balance Equation
The simulation solves for the rate of change of Chamber Pressure ($dP/dt$) using the conservation of mass within the control volume $V_c$ (Combustion Chamber):

$$ \frac{dP_c}{dt} = \frac{R T_{flame}}{V_{free}} \cdot (\dot{m}_{gen} + \dot{m}_{igniter} - \dot{m}_{out}) $$

*   $\dot{m}_{gen} = A_{burn} \cdot r \cdot \rho_{prop}$: Mass generation from burning propellant.
*   $\dot{m}_{out} = \frac{P_c A_t}{c^*}$: Mass flow out the nozzle (choked flow).
*   $V_{free}$: Free volume in the chamber, which increases as propellant burns.

### 3. Thrust Calculation
Thrust is derived from Isentropic Flow relations. The solver first finds the Exit Mach number $M_e$ by solving the Area Ratio equation ($A_e / A_t$) iteratively:

$$ \frac{A_e}{A_t} = \frac{1}{M_e} \left( \frac{2 + (k-1)M_e^2}{k+1} \right)^{\frac{k+1}{2(k-1)}} $$

Once $M_e$ is found, the Exit Pressure $P_e$ is calculated. The Thrust $F$ is then:

$$ F = \lambda \left( \dot{m}_{out} v_e + (P_e - P_{atm}) A_e \right) $$

Where $\lambda$ represents nozzle efficiency losses (friction/divergence).

### 4. Grain Geometry

FOS Engine calculates the burning surface area $A_b$ as a function of the burn depth $x$ (distance regressed).

#### **BATES (Ballistic Test and Evaluation System)**
Analytically solves for the geometry of multiple cylindrical segments burning on both the inner core and end faces. This geometry typically yields a neutral thrust curve.

$$
A_b(x) = N \cdot \left[ \pi(D_{core}+2x)(L-2x) + 2 \cdot \frac{\pi}{4}(D_{outer}^2 - (D_{core}+2x)^2) \right]
$$

#### **Star (Finocyl) Geometry**
Star grains provide a **Progressive-Regressive** burn profile, useful for high-performance motors. The engine models this using a two-phase geometric approximation:
1.  **Star Phase:** The burn front propagates outwards from the star pattern, initially increasing surface area (Progressive).
2.  **Cylindrical/Sliver Phase:** Once the star points are consumed (burn depth > web), the geometry transitions to a cylindrical burn with diminishing slivers (Regressive).

---

## 🛠️ Usage Guide

1.  **Propellant Tab:**
    *   Load "KNSB" from the preset menu.
    *   Adjust `Density` or `a, n` values if your mix differs.
2.  **Grain Tab:**
    *   Choose **BATES** or **STAR**.
    *   Use the **Visualizer Slider** to check how the grain burns back. Ensure you don't have too much Sliver (wasted fuel).
3.  **Hardware Tab:**
    *   Set **Throat Diameter** (Critical for pressure).
    *   Set **Casing Dimensions** to check safety.
4.  **Simulation Tab:**
    *   Click **Run Simulation**.
    *   **Analyze Graphs:**
        *   **Blue:** Thrust Curve.
        *   **Red:** Head-End Pressure.
        *   **Black Dashed:** Casing Burst Pressure.
    *   **Safety Rule:** The Red line must NEVER cross the Black dashed line.

---

## 📄 License
This project is licensed under the MIT License.
