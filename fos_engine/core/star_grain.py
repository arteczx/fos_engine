import numpy as np

class StarGrain:
    """
    Represents the Geometry of a Star (Finocyl) Grain.

    A Star grain has a complex cross-section that provides a progressive-regressive
    or neutral burn profile depending on geometry.

    Simplified Parameters:
    - Outer Diameter (OD): Casing fit.
    - Web Thickness (w): Distance from star tip to OD.
    - Number of Points (N).
    - Star Radius (r_inner): Radius of the inner circle (tips of the star).
    - Star Angle / Shape is approximated for standard star.
    """

    def __init__(self, outer_diameter, web_thickness, num_points, length, num_grains):
        self.outer_diameter = outer_diameter
        self.web_thickness = web_thickness
        self.num_points = int(num_points)
        self.length = length
        self.num_grains = int(num_grains)

        # Derived for simple star
        # Radius of outer star valleys
        self.radius_valley = (self.outer_diameter / 2) - self.web_thickness
        # Radius of inner star tips (assume 0.5 * valley radius for default shape)
        self.radius_tip = 0.4 * self.radius_valley # Heuristic

        # Calculate initial perimeter
        # This is complex. We will use a simplified "Perimeter Factor" approach
        # or a lookup table if not doing full CSG.
        # Let's try to approximate the perimeter evolution.

        # Phase 1: Star Burn. Perimeter is roughly constant or slightly increasing.
        # Phase 2: Sliver Burn. Perimeter drops rapidly.

        # Initial Perimeter P0 approx:
        # P0 ~ N * (2 * (R_valley - R_tip)) + ...
        # Let's use a simpler heuristic model used in amateur tools:
        # P(y) where y is burn depth.
        pass

    def get_burn_area(self, burn_depth):
        """
        Calculate burn area for Star Grain.
        Approximation:
        Perimeter is roughly 1.5x - 2x Cylinder perimeter initially.
        It burns until 'web' is consumed.
        """
        # Critical dimensions
        R_outer = self.outer_diameter / 2.0
        # The web is the thickness of propellant at the thinnest point (valley to wall).
        # We assume the user inputs 'Web Thickness'.
        # Valley Radius = R_outer - Web
        R_valley = R_outer - self.web_thickness

        # Effective burning limit
        if burn_depth >= self.web_thickness:
             # Slivers might remain, but for MVP let's assume burnout at web thickness
             # or simple linear decay for slivers.
             if burn_depth > self.web_thickness * 1.1:
                 return 0.0
             # Linear decay for sliver phase (10% extra time)
             factor = 1.0 - (burn_depth - self.web_thickness) / (0.1 * self.web_thickness)
             if factor < 0: factor = 0
        else:
            factor = 1.0

        # Perimeter Calculation (Simplified Star Model)
        # Assume Star Points angle is such that burn is Neutral to Progressive.
        # Perimeter approx = (2 * Pi * R_avg) * StarFactor
        # StarFactor decreases as it becomes circular.

        # Initial Star Factor (Perimeter / Circumference of bounding circle)
        # Typically 1.5 to 2.0 for deep stars.
        initial_factor = 1.5 + (self.num_points * 0.1)

        # As burn_depth approaches R_valley (web consumed in tips?), the shape circularizes.
        # Actually star circularizes when burn_depth = R_valley - R_tip ?
        # Let's assume a linear transition from Star Perimeter to Circular Perimeter at some depth.

        # Current mean radius approx
        r_current_mean = R_valley + burn_depth # Very rough

        # BATES Core area (reference)
        # Area if it was just a cylinder with ID = 2*(R_valley)
        # This is the "End of Phase 1" area.
        ref_cylinder_area = np.pi * (2*(R_valley + burn_depth)) * (self.length - 2*burn_depth)

        # Apply Star Enhancement Factor
        # Factor starts high, decays to 1.0 when burn_depth = Radius_valley (fully circularized at wall)
        # But we burnout at web thickness.

        progress = burn_depth / self.web_thickness
        current_factor = initial_factor * (1.0 - 0.5 * progress) # Decays slightly

        area_core = ref_cylinder_area * current_factor * factor

        # Ends
        area_ends = 2 * (np.pi * R_outer**2 * 0.6) # Approx solid face area (minus star hole)

        total = (area_core + area_ends) * self.num_grains
        return total

    def is_burned_out(self, burn_depth):
        return burn_depth > self.web_thickness * 1.1

    def get_propellant_volume(self, burn_depth):
        """
        Calculate current volume of propellant remaining.
        Simplified: Volume = Area_Cross_Section * Length * Num
        """
        # We need the Cross Section Area (Ac)
        # Ac = Area_Outer - Area_Void
        # Area_Void increases with burn_depth.
        # This is essentially the integral of BurnArea(x) dx ? No.

        # Approximation: Vol(x) = Vol_Initial - Integral(Ab(u) du from 0 to x)
        # This requires tracking history or integration.

        # Alternative Approximation:
        # Use BATES equivalent volume scaled?
        # Let's use the explicit simplified geometry model again.

        # Vol = Length * (Area_Circle - Area_Star_Void)
        # Area_Star_Void increases.

        # Let's assume linear removal of web volume.
        # Vol_prop_initial ~ (Pi*R^2 - StarVoid) * L
        # Vol_prop_current = Vol_prop_initial - (Burned_Volume)

        # Let's use a very rough heuristic for MVP since Star geometry is complex.
        # Vol = Vol_Bates_Equivalent * Star_Efficiency_Factor

        R_outer = self.outer_diameter / 2.0
        R_valley = R_outer - self.web_thickness

        # Initial Void Area (Star)
        # Approx: Pi * R_valley^2 * 0.5 (Star fills 50% of the core hole?? No)
        # Star tip radius is small.
        # Let's assume Void Area = Pi * R_valley^2 * 0.4

        # Void Radius Effective = R_valley * 0.6 + burn_depth
        r_eff = (R_valley * 0.6) + burn_depth
        if r_eff > R_outer: r_eff = R_outer

        area_void = np.pi * r_eff**2
        area_outer = np.pi * R_outer**2

        if area_void > area_outer: area_void = area_outer

        # Length decreases?
        # Star grains usually burn on ends too? Yes, we assume ends burn.
        current_length = self.length - 2*burn_depth
        if current_length < 0: current_length = 0

        vol = (area_outer - area_void) * current_length * self.num_grains
        return vol
