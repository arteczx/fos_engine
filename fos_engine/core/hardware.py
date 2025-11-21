import numpy as np

class Hardware:
    """
    Represents the Motor Hardware (Casing and Nozzle).
    Stores dimensions and material properties to perform safety calculations.
    """

    def __init__(self, throat_diameter, exit_diameter, casing_diameter, casing_thickness, casing_yield_strength=276e6):
        """
        Initialize Hardware constraints.

        Args:
            throat_diameter (float): Diameter of the nozzle throat (meters).
            exit_diameter (float): Diameter of the nozzle exit (meters).
            casing_diameter (float): Outer diameter of the motor casing (meters).
            casing_thickness (float): Wall thickness of the casing (meters).
            casing_yield_strength (float): Material Yield Strength in Pascals.
                                           Default is Al 6061-T6 (~276 MPa).
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
        Calculate the theoretical Burst Pressure of the casing.
        Uses Barlow's Formula (Thin-walled hoop stress):
        P_burst = (2 * sigma * t) / D_outer

        Returns:
            float: Burst Pressure in Pascals.
        """
        # Sutton Ch 3 / Barlow's Formula approximation
        return (2 * self.casing_yield_strength * self.casing_thickness) / self.casing_diameter

    def get_kn(self, burn_area):
        """
        Calculate the Kn (Klemmung Number) ratio.
        Kn = A_burn / A_throat

        Kn determines the chamber pressure range.

        Args:
            burn_area (float): Current burning surface area (m^2).

        Returns:
            float: Kn ratio (dimensionless).
        """
        if self.throat_area <= 0:
            return 0
        return burn_area / self.throat_area
