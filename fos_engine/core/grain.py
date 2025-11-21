import numpy as np

class BatesGrain:
    def __init__(self, outer_diameter, core_diameter, length, num_grains):
        """
        Initialize BATES grain geometry.
        All units in Meters.
        """
        self.outer_diameter = outer_diameter
        self.core_diameter = core_diameter
        self.length = length
        self.num_grains = int(num_grains)

    def get_burn_area(self, burn_depth):
        """
        Calculate the total burning area at a given burn depth (x).
        burn_depth: distance burned from the initial surface (meters).
        Returns area in m^2.
        """
        current_core_d = self.core_diameter + 2 * burn_depth
        current_length = self.length - 2 * burn_depth

        # Burnout check
        if current_core_d >= self.outer_diameter or current_length <= 0:
            return 0.0

        # Cylinder Inner Surface Area: Pi * D * L
        # Note: The length of the core decreases as ends burn back
        area_core = np.pi * current_core_d * current_length

        # End Faces Area: 2 * (Pi/4 * (OD^2 - ID^2)) per grain
        # But we have num_grains
        area_ends = 2 * (np.pi / 4) * (self.outer_diameter**2 - current_core_d**2)

        # Total area = Sum of all grains
        total_area_per_grain = area_core + area_ends
        return total_area_per_grain * self.num_grains

    def is_burned_out(self, burn_depth):
        current_core_d = self.core_diameter + 2 * burn_depth
        current_length = self.length - 2 * burn_depth
        return (current_core_d >= self.outer_diameter) or (current_length <= 0)
