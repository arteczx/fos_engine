import numpy as np

class BatesGrain:
    """
    Represents the Geometry of a BATES (Ballistic Test and Evaluation System) Grain.
    A BATES grain consists of multiple cylindrical segments that burn on:
    1. The inner core (cylinder wall).
    2. Both end faces.

    This geometry provides a relatively neutral burn profile (constant thrust).
    """

    def __init__(self, outer_diameter, core_diameter, length, num_grains):
        """
        Initialize BATES grain geometry.

        Args:
            outer_diameter (float): Outer diameter of the grain (meters).
            core_diameter (float): Initial inner core diameter (meters).
            length (float): Length of a single grain segment (meters).
            num_grains (int): Total number of grain segments stacked.
        """
        self.outer_diameter = outer_diameter
        self.core_diameter = core_diameter
        self.length = length
        self.num_grains = int(num_grains)

    def get_burn_area(self, burn_depth):
        """
        Calculate the total burning surface area at a specific burn depth.

        As the grain burns:
        - The Core Diameter increases (D + 2x).
        - The Grain Length decreases (L - 2x) because ends burn inward.

        Args:
            burn_depth (float): Distance burned from the initial surface (meters).

        Returns:
            float: Total burning area in m^2. Returns 0.0 if burned out.
        """
        current_core_d = self.core_diameter + 2 * burn_depth
        current_length = self.length - 2 * burn_depth

        # Burnout check
        if current_core_d >= self.outer_diameter or current_length <= 0:
            return 0.0

        # Cylinder Inner Surface Area: Pi * D * L
        area_core = np.pi * current_core_d * current_length

        # End Faces Area: 2 * (Pi/4 * (OD^2 - ID^2)) per grain
        # Multiplied by 2 because each grain has a top and bottom face.
        area_ends = 2 * (np.pi / 4) * (self.outer_diameter**2 - current_core_d**2)

        # Total area = Sum of all grains
        total_area_per_grain = area_core + area_ends
        return total_area_per_grain * self.num_grains

    def is_burned_out(self, burn_depth):
        """
        Check if the grain has completely consumed its web.

        Args:
            burn_depth (float): Current burn depth in meters.

        Returns:
            bool: True if the grain is burned out (web consumed).
        """
        current_core_d = self.core_diameter + 2 * burn_depth
        current_length = self.length - 2 * burn_depth
        return (current_core_d >= self.outer_diameter) or (current_length <= 0)

    def get_propellant_volume(self, burn_depth):
        """
        Calculate current volume of propellant remaining.

        Args:
            burn_depth (float): Current burn depth.

        Returns:
            float: Volume in m^3.
        """
        current_core_d = self.core_diameter + 2 * burn_depth
        current_length = self.length - 2 * burn_depth

        if current_core_d >= self.outer_diameter or current_length <= 0:
            return 0.0

        # Vol = (Area_Outer - Area_Core) * Length * Num
        area_outer = np.pi * (self.outer_diameter / 2)**2
        area_inner = np.pi * (current_core_d / 2)**2

        vol_per_grain = (area_outer - area_inner) * current_length
        return vol_per_grain * self.num_grains
