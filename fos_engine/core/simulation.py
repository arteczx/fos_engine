import numpy as np
from fos_engine.core.units import Units

class Simulation:
    def __init__(self, propellant, grain, hardware, time_step=0.001):
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
        self.gamma_func = np.sqrt(k) * (2/(k+1)) ** ((k+1)/(2*(k-1)))
        self.RT = (self.propellant.c_star * self.gamma_func)**2

    def _calculate_cf(self, P_chamber, P_atm, epsilon):
        """
        Calculate Thrust Coefficient Cf using full isentropic flow equations.
        """
        if P_chamber <= P_atm:
            return 0.0

        k = self.propellant.k

        # Solve for Exit Pressure Pe iteratively or use Approximation?
        # Equation: epsilon = G(k) / ( (Pe/Pc)^(1/k) * sqrt(2k/(k-1) * (1 - (Pe/Pc)^((k-1)/k))) )
        # This is computationally expensive to solve exactly every step (Newton Raphson).
        # However, for 'Production Grade' we should try or use a high-fidelity approx.

        # Let's use a simplified accurate model for Me (Exit Mach) if we assume supersonic.
        # Or just use the standard formula assuming Pe = P_atm (Optimal) and correct? No.

        # Let's use the standard theoretical Cf equation:
        # Cf = sqrt( (2k^2/(k-1)) * (2/(k+1))^((k+1)/(k-1)) * [1 - (Pe/Pc)^((k-1)/k)] ) + (Pe - Pa)/Pc * epsilon
        # We still need Pe.

        # Approximation for Pe/Pc based on Epsilon:
        # For typical solid rocket epsilon (4-10), Pe/Pc is usually 0.05 - 0.15.
        # We can use a pre-computed look-up or a simple fit.
        # Let's use the hall-of-fame approximation or just assume Pe ~ Patm for the main term if we can't solve it?
        # No, "Improve Math Core" means do it right.
        # I will implement a fast Newton-Raphson solver for Mach number at exit.

        # 1. Solve Area Ratio for Mach (Me)
        # A/A* = 1/M * [(2 + (k-1)M^2) / (k+1)] ^ ((k+1)/(2(k-1)))
        # This function has a minimum at M=1 (A/A*=1). We are supersonic, so M > 1.

        # Initial guess for M:
        # For epsilon=4 -> M~2.5, Epsilon=10 -> M~3.5.
        # Simple guess: M = 1 + epsilon/2?
        M = 2.5 # Initial guess

        # Newton-Raphson
        for _ in range(5): # 5 Iterations is usually plenty for Mach
            f = (1/M) * ((2 + (k-1)*M**2)/(k+1))**((k+1)/(2*(k-1))) - epsilon
            # Derivative df/dM is complex, finite difference is faster to code and robust enough here.
            delta = 0.001
            f_plus = (1/(M+delta)) * ((2 + (k-1)*(M+delta)**2)/(k+1))**((k+1)/(2*(k-1))) - epsilon
            df = (f_plus - f) / delta
            if df == 0: break
            M_new = M - f / df
            if M_new < 1.0: M_new = 1.001 # Stay supersonic
            if abs(M_new - M) < 0.001:
                M = M_new
                break
            M = M_new

        # 2. Calculate Pe/Pc from M
        # P/P0 = (1 + (k-1)/2 * M^2) ^ (-k/(k-1))
        Pe_ratio = (1 + (k-1)/2 * M**2) ** (-k / (k-1))
        Pe = Pe_ratio * P_chamber

        # 3. Calculate Cf
        term1 = np.sqrt((2*k**2 / (k-1)) * (2/(k+1))**((k+1)/(k-1)) * (1 - (Pe/P_chamber)**((k-1)/k)))
        term2 = (Pe - P_atm) / P_chamber * epsilon

        Cf = term1 + term2
        return Cf

    def _derivatives(self, t, state, current_throat_area, use_erosive, erosion_rate):
        """
        Calculate derivatives for RK4 solver.
        State: [Pressure (Pa), BurnDepth (m)]
        Returns: [dP/dt, dr/dt]
        """
        P_c = state[0]
        burn_depth = state[1]

        if P_c < 100.0: P_c = 100.0 # Clamp slightly above 0 to avoid math errors

        # 1. Calculate Burn Rate (r)
        r_base = self.propellant.burn_rate_a * (P_c**self.propellant.burn_rate_n)
        r = r_base

        if use_erosive:
             current_core_d = self.grain.core_diameter + 2 * burn_depth
             if current_core_d < self.grain.outer_diameter: # Only if valid geometry
                 A_port = np.pi * (current_core_d / 2)**2
                 m_flow_approx = (P_c * current_throat_area) / self.propellant.c_star
                 G = m_flow_approx / A_port
                 G_crit = 250.0
                 k_erosive = 0.002
                 if G > G_crit:
                     r = r_base * (1 + k_erosive * (G - G_crit))

        # 2. Mass Gen
        Ab = self.grain.get_burn_area(burn_depth)
        m_dot_gen = Ab * r * self.propellant.density

        # 3. Mass Out
        m_dot_out = (P_c * current_throat_area) / self.propellant.c_star

        # 4. dP/dt
        # Need Free Volume. V_free = V_init + Volume_burned
        # Approximating Volume Burned is tricky inside RK step without tracking it as state.
        # Ideally, Free Volume should be a state variable.
        # Let's calculate Free Volume based on Geometry (Burn Depth) to be stateless dependent.

        grain_vol = self.grain.num_grains * (np.pi * (self.grain.outer_diameter/2)**2 - np.pi * ((self.grain.core_diameter + 2*burn_depth)/2)**2) * (self.grain.length - 2*burn_depth)
        if grain_vol < 0: grain_vol = 0

        # Total Chamber Vol
        casing_id = self.hardware.casing_diameter - 2 * self.hardware.casing_thickness
        L_total = self.grain.length * self.grain.num_grains # Simplified chamber length
        chamber_volume_total = np.pi * (casing_id/2)**2 * L_total

        V_free = chamber_volume_total - grain_vol
        if V_free < 0.0001: V_free = 0.0001

        dp_dt = ((m_dot_gen - m_dot_out) * self.RT) / V_free

        return np.array([dp_dt, r]) # Return derivatives

    def run(self, use_erosive_burning=False):
        self.t = 0.0
        self.results = {"time": [], "pressure": [], "thrust": [], "kn": [], "burn_area": [], "mass_flow_out": []}

        # Initial Conditions
        P_atm = 101325.0
        P_c = 200000.0 # Start with ignition pressure (2 bar)
        burn_depth = 0.0

        # Setup Erosion
        initial_throat_diameter = self.hardware.throat_diameter
        erosion_rate = 0.0001 if use_erosive_burning else 0.0

        running = True

        while running:
            # Update Throat
            current_throat_diameter = initial_throat_diameter + (erosion_rate * self.t)
            current_throat_area = np.pi * (current_throat_diameter / 2)**2

            # RK4 Step
            # State = [P_c, burn_depth]
            y = np.array([P_c, burn_depth])

            k1 = self._derivatives(self.t, y, current_throat_area, use_erosive_burning, erosion_rate)
            k2 = self._derivatives(self.t + self.dt/2, y + k1 * self.dt/2, current_throat_area, use_erosive_burning, erosion_rate)
            k3 = self._derivatives(self.t + self.dt/2, y + k2 * self.dt/2, current_throat_area, use_erosive_burning, erosion_rate)
            k4 = self._derivatives(self.t + self.dt, y + k3 * self.dt, current_throat_area, use_erosive_burning, erosion_rate)

            dy = (k1 + 2*k2 + 2*k3 + k4) * (self.dt / 6.0)

            P_c_new = P_c + dy[0]
            burn_depth_new = burn_depth + dy[1]

            # Physics Constraints
            if P_c_new < P_atm: P_c_new = P_atm

            # Calculate Outputs for storage (using new state)
            epsilon = self.hardware.exit_area / current_throat_area
            Cf = self._calculate_cf(P_c_new, P_atm, epsilon)
            thrust = Cf * current_throat_area * P_c_new

            Ab = self.grain.get_burn_area(burn_depth_new)
            m_dot_out = (P_c_new * current_throat_area) / self.propellant.c_star

            # Update State
            self.t += self.dt
            P_c = P_c_new
            burn_depth = burn_depth_new

            # Store
            self.results["time"].append(self.t)
            self.results["pressure"].append(P_c)
            self.results["thrust"].append(thrust)
            self.results["kn"].append(self.hardware.get_kn(Ab))
            self.results["burn_area"].append(Ab)
            self.results["mass_flow_out"].append(m_dot_out)

            # Stop Conditions
            if self.grain.is_burned_out(burn_depth) and P_c < P_atm * 1.05:
                running = False
            if self.t > 10.0:
                running = False

        return self.results
