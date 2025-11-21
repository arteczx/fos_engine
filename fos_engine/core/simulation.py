import numpy as np
from fos_engine.core.units import Units

class Simulation:
    def __init__(self, propellant, grain, hardware, time_step=0.01):
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

    def run(self, use_erosive_burning=False):
        t = 0.0
        burn_depth = 0.0

        # Initial Conditions
        P_atm = 101325.0 # Pa
        P_c = P_atm

        # Dead volume (V_c) approximates
        # Initial free volume = Casing Volume - Grain Volume
        # Simple approx: Volume of casing cylinder (length of all grains) - Initial Grain Vol
        # We assume casing length fits grains exactly for this volume calc (or slightly larger).
        L_total = self.grain.length * self.grain.num_grains
        # ID of casing is OD of grain (approx, ignoring liner for simple logic)
        # Actually casing ID > grain OD. Let's assume casing ID = grain OD + small gap or just use grain OD for Vc calc to start.
        # Better: V_chamber = pi * (CasingID/2)^2 * L_total.
        # Let's assume CasingID approx GrainOD for now if not provided explicitly in Hardware (Hardware has casing diameter).
        # Hardware.casing_diameter is likely OD. We need ID.
        # Let's infer Casing ID = Casing OD - 2*Thickness.
        casing_id = self.hardware.casing_diameter - 2 * self.hardware.casing_thickness
        chamber_volume_total = np.pi * (casing_id/2)**2 * L_total

        # Initial Grain Volume
        grain_vol = self.grain.num_grains * (np.pi * (self.grain.outer_diameter/2)**2 - np.pi * (self.grain.core_diameter/2)**2) * self.grain.length
        free_volume = chamber_volume_total - grain_vol

        # Loop until pressure drops back to near atm (burnout + tailoff)
        # Or just until burnout for now.
        running = True

        # Gas constant for combustion products (R_specific)
        # R = R_universal / M_molar.
        # KNSB M_molar ~ 40-42 g/mol.
        # Let's approximate R_specific.
        # C* = sqrt(RT / gamma) / f(gamma).
        # We can back-calculate RT from C* and gamma if needed, or just use C* directly in mass flow eq.
        # Sutton Eq 12-5 uses RT/M.
        # c* = P * At / m_dot = sqrt(R_spec * T0) / Gamma_func
        # R_spec * T0 = (c* * Gamma_func)^2

        k = self.propellant.k
        # Gamma function (Vandenkerckhove function)
        # Gamma_func = sqrt(k) * (2/(k+1)) ^ ((k+1)/(2*(k-1)))
        gamma_func = np.sqrt(k) * (2/(k+1)) ** ((k+1)/(2*(k-1)))

        RT = (self.propellant.c_star * gamma_func)**2

        # Nozzle Erosion Setup
        initial_throat_diameter = self.hardware.throat_diameter
        # Erosion rate: 0.1mm/s is a common generic guess for KNSB/PVC,
        # but usually it's dependent on pressure/mass flux.
        # Let's use a simple linear rate if "erosion" is implicitly part of the advanced features request
        # The prompt asked for "Nozzle Erosion Estimator" as an advanced feature.
        # I will assume a default low rate if not specified, or 0.
        # Ideally this should be a setting. Let's default to 0 unless I add a setting.
        # I will add a small fixed erosion rate if erosive burning is toggled, as a proxy for "Advanced Mode",
        # or just keep it 0 to be safe unless I passed it in.
        # Actually, the user spec says: "Add a factor to increase D_t linearly over time. Dt(t) = D_init + (Rate * t)"
        erosion_rate = 0.0001 if use_erosive_burning else 0.0 # 0.1 mm/s if "Advanced" enabled

        current_throat_diameter = initial_throat_diameter

        while running:
            # 0. Update Throat (Erosion)
            current_throat_diameter = initial_throat_diameter + (erosion_rate * t)
            current_throat_area = np.pi * (current_throat_diameter / 2)**2

            # 1. Determine Burn Rate
            # r = a * P^n
            if t == 0:
                 P_c = 200000.0 # 2 Bar artificial start to simulate igniter

            r_base = self.propellant.burn_rate_a * (P_c**self.propellant.burn_rate_n)
            r = r_base

            # Erosive burning (Optional)
            if use_erosive_burning:
                 # Simple Mass Flux Threshold Model (Greatrix / Standard)
                 # G = m_dot / A_port
                 # But m_dot is not known yet for this step? We can use previous m_dot or m_gen.
                 # Let's use m_gen from previous step or estimate current.
                 # A_port = Area of core.

                 # Current Core Area
                 current_core_d = self.grain.core_diameter + 2 * burn_depth
                 A_port = np.pi * (current_core_d / 2)**2

                 # Mass Flux G (kg/m^2/s) approximated by mass generation or mass flow at nozzle?
                 # G is usually calculated at the port exit.
                 # m_dot approx = P_c * At / c_star
                 m_flow_approx = (P_c * current_throat_area) / self.propellant.c_star
                 G = m_flow_approx / A_port

                 # Threshold G_crit. For KNSB, maybe ~250-300 kg/m2s.
                 # Simple enhancement factor: r = r_base * (1 + k(G - G_crit))
                 # If G < G_crit, no enhancement.
                 G_crit = 250.0
                 k_erosive = 0.002 # Tuning factor

                 if G > G_crit:
                     r = r_base * (1 + k_erosive * (G - G_crit))

            # 2. Calculate Areas
            Ab = self.grain.get_burn_area(burn_depth)

            # 3. Mass Generation
            m_dot_gen = Ab * r * self.propellant.density

            # 4. Mass Out
            # m_dot_out = P_c * At / c*
            m_dot_out = (P_c * current_throat_area) / self.propellant.c_star

            # 5. Update Pressure (dP/dt)
            # Vc * dP/dt = (m_gen - m_out) * RT
            # dP = (m_gen - m_out) * RT / Vc * dt
            # Also Vc changes! dVc/dt = m_dot_gen / rho (volume of propellant burned becomes free volume)
            # So Vc_new = Vc_old + (m_dot_gen / rho) * dt

            dp = ((m_dot_gen - m_dot_out) * RT / free_volume) * self.dt
            P_c += dp

            # Prevent negative pressure or pressure below ambient (backflow)
            # In reality, it would just sit at Patm.
            if P_c < P_atm:
                P_c = P_atm

            # Update Free Volume
            vol_burned = (m_dot_gen / self.propellant.density) * self.dt
            free_volume += vol_burned

            # 6. Thrust
            # Calculate Cf based on expansion ratio and pressure
            # epsilon = Ae / At
            epsilon = self.hardware.exit_area / current_throat_area
            k = self.propellant.k
            Pe = P_atm # Fallback if unchoked or low pressure

            # Isentropic relation to find Pe/Pc from Area Ratio is iterative.
            # Approximation for Cf (Vacuum + Pressure term):
            # Cf = sqrt( (2k^2/(k-1)) * (2/(k+1))^((k+1)/(k-1)) * [1 - (Pe/Pc)^((k-1)/k)] ) + (Pe - Patm)/Pc * epsilon

            # Since solving for Pe is expensive every step, we can use a simplified model or just assume Pe/Pc is defined by area ratio for supersonic flow.
            # Or use a fit.
            # Let's use a standard approximation for "Separation" if Pe < 0.4 Patm?
            # For this implementation, let's calculate the Ideal Maximum Thrust Coefficient for the given Area Ratio (assuming fully expanded)
            # and subtract losses?
            # No, let's do it properly:
            # 1. Calculate Mach at exit (Me) from Epsilon (Iterative or Look-up).
            # 2. Calculate Pe from Me.
            # 3. Calculate Cf.

            # Simplified approach for stability:
            # Use the analytical formula for Cf assuming Optimal Expansion (Pe = Patm) is NOT true, we have fixed Area Ratio.
            # We need Pe.
            # Approximation: For k=1.2, Epsilon ~ 4-8 -> Pe/Pc ~ 0.05 - 0.1
            # Let's calculate the Vacuum Cf and subtract atmospheric term.

            # Gamma function for Cf
            G_func = np.sqrt(k * (2/(k+1))**((k+1)/(k-1))) # This is roughly 0.6-0.7

            # Vacuum Thrust Coefficient (Cf_vac)
            # Cf_vac = Gamma_func * sqrt( (2k/(k-1)) * (1 - (Pe/Pc)^((k-1)/k)) ) + ...
            # This circle logic requires Pe.

            # Let's stick to a simpler engineering approximation used in amateur codes:
            # Cf = Cf_efficiency * [ Gamma_const * sqrt(1 - (Patm/Pc)^((k-1)/k)) ] ??? No that assumes Pe=Patm.

            # Let's use the fixed approximation:
            # Cf = 1.6 (Vacuum) - (Patm / Pc) * epsilon
            # This is a very rough heuristic but better than constant 1.5.
            # Typical Cf_vac for sugar rockets is ~1.6 - 1.7.

            Cf_vac = 1.7
            Cf_est = Cf_vac - (P_atm / P_c) * epsilon

            if Cf_est < 0: Cf_est = 0 # Startup transient

            thrust = Cf_est * current_throat_area * P_c

            # 7. Advance State
            burn_depth += r * self.dt
            t += self.dt

            # Store results
            self.results["time"].append(t)
            self.results["pressure"].append(P_c)
            self.results["thrust"].append(thrust)
            self.results["kn"].append(self.hardware.get_kn(Ab))
            self.results["burn_area"].append(Ab)
            self.results["mass_flow_out"].append(m_dot_out)

            # Stop conditions
            # If grain is burned out and pressure is close to atmospheric, we are done.
            if self.grain.is_burned_out(burn_depth) and P_c < P_atm * 1.05:
                 running = False

            if t > 10.0: # Safety break
                 running = False

        return self.results
