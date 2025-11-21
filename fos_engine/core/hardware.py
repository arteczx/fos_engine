import numpy as np

class Hardware:
    def __init__(self, throat_diameter, exit_diameter, casing_diameter, casing_thickness, casing_yield_strength=276e6):
        """
        Hardware constraints.
        Units: Meters, Pascals.
        Default yield strength is for Al 6061-T6 (~276 MPa or 40000 psi).
        """
        self.throat_diameter = throat_diameter
        self.exit_diameter = exit_diameter
        self.casing_diameter = casing_diameter
        self.casing_thickness = casing_thickness
        self.casing_yield_strength = casing_yield_strength

        self.throat_area = np.pi * (self.throat_diameter / 2)**2
        self.exit_area = np.pi * (self.exit_diameter / 2)**2

    def get_burst_pressure(self):
        """
        Calculate burst pressure using thin-wall hoop stress formula (or similar).
        P_burst = (2 * sigma * t) / D
        """
        # Sutton Ch 3 / Barlow's Formula approximation
        # D is usually mean diameter or OD. For thin wall, OD is close.
        return (2 * self.casing_yield_strength * self.casing_thickness) / self.casing_diameter

    def get_kn(self, burn_area):
        """
        Calculate Kn = Ab / At
        """
        if self.throat_area <= 0:
            return 0
        return burn_area / self.throat_area
