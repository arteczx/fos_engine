from dataclasses import dataclass

@dataclass
class Propellant:
    """
    Data class representing the thermodynamic properties of a Solid Propellant.

    Attributes:
        name (str): Display name of the propellant.
        density (float): Density in kg/m^3.
        c_star (float): Characteristic Velocity (C*) in m/s. Measure of combustion energy.
        burn_rate_a (float): Saint Robert's Law coefficient 'a'. Units: m/s per Pa^n.
        burn_rate_n (float): Saint Robert's Law exponent 'n'. Dimensionless.
        k (float): Specific Heat Ratio (Gamma). Dimensionless.
    """
    name: str
    density: float
    c_star: float
    burn_rate_a: float
    burn_rate_n: float
    k: float

    @staticmethod
    def create_knsb():
        """
        Creates a Propellant instance for Standard KNSB (Potassium Nitrate / Sorbitol).
        Data source based on Richard Nakka's experimental values.

        Returns:
            Propellant: Configured KNSB object.
        """
        # Standard KNSB properties
        # Density ~ 1.84 g/cm3 = 1840 kg/m3
        # C* ~ 895 m/s
        # Burn rate logic:
        # Nakka's KNSB: r = 8.266 * P_mpa ^ 0.319 (mm/s, Mpa)
        # Converted to SI (m/s, Pa):
        # r(m/s) = (a_nakka / 1000) * (1e-6)^n * P_pa^n

        n = 0.319
        a_nakka = 8.266 # mm/s per MPa^n

        a_si = (a_nakka / 1000.0) * (1.0e-6)**n

        return Propellant(
            name="KNSB (Sugar/Nitrate)",
            density=1840.0,
            c_star=895.0,
            burn_rate_a=a_si,
            burn_rate_n=n,
            k=1.13
        )
