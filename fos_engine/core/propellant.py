from dataclasses import dataclass

@dataclass
class Propellant:
    name: str
    density: float  # kg/m^3 (Stored in SI)
    c_star: float   # m/s
    burn_rate_a: float  # Coefficient for r = a * P^n (where r is in m/s, P in Pa)
    burn_rate_n: float  # Exponent
    k: float        # Specific heat ratio (gamma)

    @staticmethod
    def create_knsb():
        # Standard KNSB properties (approximate, can be refined)
        # Density ~ 1.84 g/cm3 = 1840 kg/m3
        # C* ~ 850-900 m/s. Let's use 880 m/s
        # Burn rate: r = a P^n.
        # Nakka's KNSB: r = 8.266 * P_mpa ^ 0.319 (mm/s, Mpa)
        # We need to convert these coefficients to SI (m/s, Pa)
        # Or we store them in a way that the simulation handles.
        # Let's stick to SI in the class storage.

        # Converting Nakka's (mm/s, MPa) to (m/s, Pa):
        # r(mm/s) = a_nakka * (P_pa / 1e6)^n
        # r(m/s) * 1000 = a_nakka * (P_pa / 1e6)^n
        # r(m/s) = (a_nakka / 1000) * (1e-6)^n * P_pa^n
        # a_si = (a_nakka / 1000) * (1e-6)^n

        n = 0.319
        a_nakka = 8.266 # mm/s per MPa^n

        a_si = (a_nakka / 1000.0) * (1.0e-6)**n

        return Propellant(
            name="KNSB (Sugar/Nitrate)",
            density=1840.0,
            c_star=895.0, # Nakka cites around 895 m/s
            burn_rate_a=a_si,
            burn_rate_n=n,
            k=1.13
        )
