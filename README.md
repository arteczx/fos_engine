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

FOS Engine is built on the fundamental conservation laws of fluid dynamics and thermodynamics governing solid rocket propulsion.

### 1. Combustion Dynamics (Saint Robert's Law)
The linear regression rate $r$ (how fast the propellant surface recedes) is modeled as a function of chamber pressure $P_c$ using **Saint Robert's Law**:

$$
r = a \cdot P_c^n
$$

*   $a$: Burn rate coefficient (empirical constant).
*   $n$: Pressure exponent (must be $< 1.0$ for stable combustion).

#### **Erosive Burning**
In high L/D motors, high-velocity gas flow across the propellant surface increases heat transfer, accelerating the burn rate. FOS Engine implements a threshold-based flux model:

$$
r_{total} = r_{base} \cdot [1 + k_{erosive}(G - G_{crit})]
$$

Where $G$ is the mass flux ($kg/m^2s$) and $G_{crit}$ is the threshold flux (typically 250-300 $kg/m^2s$ for sugar propellants).

### 2. Internal Ballistics (Mass Balance)
The core simulation solves the differential equation for the rate of change of Chamber Pressure ($dP_c/dt$). This is derived from the Conservation of Mass within the control volume $V_{free}$ (the combustion chamber void).

$$
\frac{dP_c}{dt} = \frac{R T_{flame}}{V_{free}} \cdot (\dot{m}_{in} - \dot{m}_{out})
$$

Where:

*   **Mass In ($\dot{m}_{in}$):** Sum of propellant generation and igniter flux.

    $$
    \dot{m}_{gen} = A_{burn}(x) \cdot r \cdot \rho_{prop}
    $$

*   **Mass Out ($\dot{m}_{out}$):** Mass flow through the nozzle throat (assuming Choked Flow).

    $$
    \dot{m}_{out} = \frac{P_c A_{throat}}{c^*}
    $$

*   **Free Volume ($V_{free}$):** The void volume increases as propellant is consumed.

    $$
    V_{free}(t) = V_{casing} - V_{grain}(t)
    $$

### 3. Nozzle Gas Dynamics (Isentropic Flow)
Thrust is calculated by analyzing the isentropic expansion of gas through the de Laval nozzle.

#### **Step 1: Solve for Exit Mach Number ($M_e$)**
The engine solves the Area Ratio equation iteratively using the Newton-Raphson method:

$$
\frac{A_{exit}}{A_{throat}} = \frac{1}{M_e} \left( \frac{2 + (k-1)M_e^2}{k+1} \right)^{\frac{k+1}{2(k-1)}}
$$

#### **Step 2: Calculate Exit Pressure ($P_e$)**
Using isentropic relations:

$$
\frac{P_e}{P_c} = \left( 1 + \frac{k-1}{2} M_e^2 \right)^{-\frac{k}{k-1}}
$$

#### **Step 3: Calculate Thrust ($F$)**
Total thrust is the sum of momentum thrust and pressure thrust, scaled by nozzle efficiency $\eta_{nozzle}$:

$$
F = \eta_{nozzle} \cdot \left[ \dot{m}_{out} v_e + (P_e - P_{atm}) A_{exit} \right]
$$

### 4. Grain Geometry
The engine calculates the instantaneous burning surface area $A_b$ as a function of the burn depth $x$.

#### **BATES (Ballistic Test and Evaluation System)**
A BATES grain consists of multiple uninhibited cylindrical segments burning on both the inner core and the end faces. This geometry balances the increasing core area with decreasing segment length, often yielding a neutral thrust curve.

$$
A_b(x) = N_{grains} \cdot \left[ \pi(D_{core}+2x)(L_{grain}-2x) + 2 \cdot \frac{\pi}{4}(D_{outer}^2 - (D_{core}+2x)^2) \right]
$$

#### **Star (Finocyl) Geometry**
Star grains allow for **Progressive-Regressive** thrust profiles. FOS Engine models this using a two-phase geometric approximation:
1.  **Star Phase ($x < w$):** The flame front propagates outwards from the star pattern. The perimeter generally increases or stays constant depending on the number of points and angles.
2.  **Sliver Phase ($x > w$):** Once the web thickness $w$ is consumed, the geometry transitions to a set of discontinuous slivers (fillets) burning against the casing wall, causing a rapid regression in thrust (Tail-off).

### 5. Safety Criteria

#### **Burst Pressure**
The casing's maximum safe pressure is calculated using **Barlow's Formula** for thin-walled hoop stress:

$$
P_{burst} = \frac{2 \cdot \sigma_{yield} \cdot t_{wall}}{D_{outer}}
$$

#### **$K_n$ (Klemmung Number)**
The ratio of Burning Area to Throat Area. This is the primary determinant of chamber pressure.

$$
K_n = \frac{A_{burn}}{A_{throat}}
$$

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
        *   **Red:** Head-End Pressure (Lagrange Gradient included).
        *   **Black Dashed:** Casing Burst Pressure.
    *   **Safety Rule:** The Red line must NEVER cross the Black dashed line.

---

## 📄 License
This project is licensed under the MIT License.
