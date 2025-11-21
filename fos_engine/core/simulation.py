import numpy as np
from fos_engine.core.units import Units

class Simulation:
    """
    The Core Physics Engine for Internal Ballistics Simulation.

    This class handles the time-stepping solution of the motor performance.
    It solves the differential equation for Chamber Pressure (dP/dt) using
    mass conservation and Saint Robert's Law for burn rate.
    """

    def __init__(self, propellant, grain, hardware, time_step=0.001):
        """
        Initialize the Simulation.

        Args:
            propellant (Propellant): Propellant object with thermo properties.
            grain (BatesGrain): Grain geometry object.
            hardware (Hardware): Hardware constraints (nozzle, casing).
            time_step (float): Delta time for integration step (seconds).
        """
        self.propellant = propellant
        self.grain = grain
        self.hardware = hardware
        self.dt = time_step

        self.results = {
            "time": [],
            "pressure": [],
            "thrust": [],
            "kn": [],
            "burn_area": [],
            "mass_flow_out": []
        }

        # Simulation State
        self.t = 0.0
        self.P_c = 101325.0 # Start at Atm
        self.burn_depth = 0.0
        self.free_volume = 0.0 # Calculated in run

        # Constants for solver
        k = self.propellant.k
        # Gamma Function (Vandenkerckhove function)
        self.gamma_func = np.sqrt(k) * (2/(k+1)) ** ((k+1)/(2*(k-1)))

        # Effective C* (Combustion Efficiency)
        self.c_star_eff = self.propellant.c_star * getattr(self.propellant, 'combustion_efficiency', 1.0)

        # Gas Constant * Temperature Term (RT) derived from C*
        # C* = sqrt(RT) / Gamma_func  =>  RT = (C* * Gamma_func)^2
        self.RT = (self.c_star_eff * self.gamma_func)**2

    def _calculate_cf(self, P_chamber, P_atm, epsilon):
        """
        Calculate Thrust Coefficient (Cf) using Isentropic Flow equations.
        Solves for Exit Mach Number (Me) iteratively using Newton-Raphson
        based on the Area Ratio (epsilon).

        Args:
            P_chamber (float): Chamber Pressure (Pa).
            P_atm (float): Ambient Pressure (Pa).
            epsilon (float): Nozzle Expansion Ratio (Ae/At).

        Returns:
            float: Thrust Coefficient Cf (dimensionless).
        """
        if P_chamber <= P_atm:
            return 0.0

        k = self.propellant.k

        # 1. Solve Area Ratio for Mach (Me)
        # A/A* = 1/M * [(2 + (k-1)M^2) / (k+1)] ^ ((k+1)/(2(k-1)))
        # Newton-Raphson Solver
        M = 2.5 # Initial guess for supersonic flow

        for _ in range(5): # 5 Iterations is usually sufficient
            # Function f(M) - epsilon = 0
            f = (1/M) * ((2 + (k-1)*M**2)/(k+1))**((k+1)/(2*(k-1))) - epsilon

            # Finite difference derivative
            delta = 0.001
            f_plus = (1/(M+delta)) * ((2 + (k-1)*(M+delta)**2)/(k+1))**((k+1)/(2*(k-1))) - epsilon
            df = (f_plus - f) / delta

            if df == 0: break

            M_new = M - f / df
            if M_new < 1.0: M_new = 1.001 # Force supersonic solution

            if abs(M_new - M) < 0.001:
                M = M_new
                break
            M = M_new

        # 2. Calculate Pe/Pc from Exit Mach M
        # P/P0 = (1 + (k-1)/2 * M^2) ^ (-k/(k-1))
        Pe_ratio = (1 + (k-1)/2 * M**2) ** (-k / (k-1))
        Pe = Pe_ratio * P_chamber

        # 3. Calculate Cf
        # Cf = Momentum Term + Pressure Term
        term1 = np.sqrt((2*k**2 / (k-1)) * (2/(k+1))**((k+1)/(k-1)) * (1 - (Pe/P_chamber)**((k-1)/k)))
        term2 = (Pe - P_atm) / P_chamber * epsilon

        Cf = term1 + term2
        return Cf

    def _derivatives(self, t, state, current_throat_area, use_erosive, erosion_rate, m_dot_igniter):
        """
        Calculate derivatives for RK4 solver.
        System State: [Pressure (Pa), BurnDepth (m)]
        Returns Derivatives: [dP/dt, dr/dt]
        """
        P_c = state[0]
        burn_depth = state[1]

        if P_c < 100.0: P_c = 100.0 # Clamp to avoid math errors

        # 1. Calculate Burn Rate (r)
        # Saint Robert's Law: r = a * P^n
        r_base = self.propellant.burn_rate_a * (P_c**self.propellant.burn_rate_n)
        r = r_base

        # Erosive Burning Check (Optional)
        if use_erosive:
             # Basic grain validity check
             current_core_d = self.grain.core_diameter + 2 * burn_depth
             if current_core_d < self.grain.outer_diameter:
                 A_port = np.pi * (current_core_d / 2)**2
                 # Mass Flux G approximation
                 m_flow_approx = (P_c * current_throat_area) / self.c_star_eff
                 G = m_flow_approx / A_port

                 G_crit = 300.0 # Critical Flux (kg/m^2s)
                 k_erosive = 0.0005 # Erosion constant (Conservative)
                 if G > G_crit:
                     factor = 1 + k_erosive * (G - G_crit)
                     if factor > 3.0: factor = 3.0 # Safety clamp to prevent numerical explosion
                     r = r_base * factor

        # 2. Mass Generation Rate (kg/s)
        Ab = self.grain.get_burn_area(burn_depth)
        m_dot_gen = Ab * r * self.propellant.density

        # 3. Mass Flow Out Rate (kg/s)
        m_dot_out = (P_c * current_throat_area) / self.c_star_eff

        # 4. Calculate Chamber Pressure Change (dP/dt)
        # Vc * dP/dt = (m_gen + m_igniter - m_out) * RT

        # Calculate Free Volume (Chamber Volume - Grain Volume)
        grain_vol = self.grain.get_propellant_volume(burn_depth)

        casing_id = self.hardware.casing_diameter - 2 * self.hardware.casing_thickness
        L_total = self.grain.length * self.grain.num_grains
        chamber_volume_total = np.pi * (casing_id/2)**2 * L_total

        V_free = chamber_volume_total - grain_vol
        if V_free < 0.0001: V_free = 0.0001

        dp_dt = ((m_dot_gen + m_dot_igniter - m_dot_out) * self.RT) / V_free

        return np.array([dp_dt, r])

    def run(self, use_erosive_burning=False):
        """
        Execute the simulation loop using RK4 integration.

        Args:
            use_erosive_burning (bool): If True, enables erosive burning model.

        Returns:
            dict: Results dictionary containing time series of P, F, Kn, etc.
        """
        self.t = 0.0
        self.results = {"time": [], "pressure": [], "thrust": [], "kn": [], "burn_area": [], "mass_flow_out": []}

        # Initial Conditions
        P_atm = 101325.0
        P_c = P_atm # Start at Ambient (Igniter will pressurize)
        burn_depth = 0.0

        # Setup Erosion
        initial_throat_diameter = self.hardware.throat_diameter
        erosion_rate = 0.0001 if use_erosive_burning else 0.0 # Linear erosion if Advanced

        # Setup Ignition (Simple Mass Flux Model)
        # Assume a small pyrotechnic charge that burns for 0.2s
        # Mass flow ~ 0.01 kg/s (just enough to pressurize)
        t_ignition = 0.2
        m_dot_igniter_avg = 0.05 # Adjust this to get robust ignition

        running = True

        while running:
            # Update Throat (Nozzle Erosion)
            current_throat_diameter = initial_throat_diameter + (erosion_rate * self.t)
            current_throat_area = np.pi * (current_throat_diameter / 2)**2

            # Determine Igniter Flux
            m_dot_igniter = m_dot_igniter_avg if self.t < t_ignition else 0.0

            # RK4 Integration Step
            y = np.array([P_c, burn_depth])

            k1 = self._derivatives(self.t, y, current_throat_area, use_erosive_burning, erosion_rate, m_dot_igniter)
            k2 = self._derivatives(self.t + self.dt/2, y + k1 * self.dt/2, current_throat_area, use_erosive_burning, erosion_rate, m_dot_igniter)
            k3 = self._derivatives(self.t + self.dt/2, y + k2 * self.dt/2, current_throat_area, use_erosive_burning, erosion_rate, m_dot_igniter)
            k4 = self._derivatives(self.t + self.dt, y + k3 * self.dt, current_throat_area, use_erosive_burning, erosion_rate, m_dot_igniter)

            dy = (k1 + 2*k2 + 2*k3 + k4) * (self.dt / 6.0)

            P_c_new = P_c + dy[0]
            burn_depth_new = burn_depth + dy[1]

            # Physics Constraints
            if P_c_new < P_atm: P_c_new = P_atm

            # Calculate Outputs for storage
            epsilon = self.hardware.exit_area / current_throat_area
            Cf = self._calculate_cf(P_c_new, P_atm, epsilon)

            # Apply Nozzle Efficiency
            nozzle_eff = getattr(self.hardware, 'nozzle_efficiency', 0.95)
            thrust = Cf * current_throat_area * P_c_new * nozzle_eff

            Ab = self.grain.get_burn_area(burn_depth_new)
            m_dot_out = (P_c_new * current_throat_area) / self.c_star_eff

            # Update State
            self.t += self.dt
            P_c = P_c_new
            burn_depth = burn_depth_new

            # Store Results
            self.results["time"].append(self.t)
            self.results["pressure"].append(P_c)
            self.results["thrust"].append(thrust)
            self.results["kn"].append(self.hardware.get_kn(Ab))
            self.results["burn_area"].append(Ab)
            self.results["mass_flow_out"].append(m_dot_out)

            # Stop Conditions
            # 1. Grain Burned Out AND Pressure dropped back to near ambient
            if self.grain.is_burned_out(burn_depth) and P_c < P_atm * 1.05 and self.t > t_ignition:
                running = False
            # 2. Safety Timeout
            if self.t > 10.0:
                running = False

        return self.results
