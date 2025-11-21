import json
from fos_engine.core.propellant import Propellant
from fos_engine.core.grain import BatesGrain
from fos_engine.core.star_grain import StarGrain
from fos_engine.core.hardware import Hardware
from fos_engine.core.units import Units

class DataManager:
    """
    Handles the persistence of motor designs.
    Saves and loads the configuration of Propellant, Grain, and Hardware
    to/from JSON files.
    """

    @staticmethod
    def save_motor(filepath, propellant, grain, hardware, settings=None):
        """
        Saves the motor configuration to a JSON file.

        Data is stored in SI units to ensure consistency with the Core engine.

        Args:
            filepath (str): Path to the destination JSON file.
            propellant (Propellant): Propellant object to save.
            grain (Grain): Grain object (BatesGrain or StarGrain) to save.
            hardware (Hardware): Hardware object to save.
            settings (dict, optional): Additional UI settings (e.g., Erosive flag).
        """
        # Determine grain type
        grain_type = "BATES"
        grain_data = {}
        if isinstance(grain, BatesGrain):
            grain_type = "BATES"
            grain_data = {
                "outer_diameter": grain.outer_diameter,
                "core_diameter": grain.core_diameter,
                "length": grain.length,
                "num_grains": grain.num_grains
            }
        elif isinstance(grain, StarGrain):
            grain_type = "STAR"
            grain_data = {
                "outer_diameter": grain.outer_diameter,
                "web_thickness": grain.web_thickness,
                "num_points": grain.num_points,
                "length": grain.length,
                "num_grains": grain.num_grains
            }

        data = {
            "propellant": {
                "name": propellant.name,
                "density": propellant.density,
                "c_star": propellant.c_star,
                "burn_rate_a": propellant.burn_rate_a,
                "burn_rate_n": propellant.burn_rate_n,
                "k": propellant.k,
                "combustion_efficiency": getattr(propellant, "combustion_efficiency", 0.95)
            },
            "grain": {
                "type": grain_type,
                **grain_data
            },
            "hardware": {
                "throat_diameter": hardware.throat_diameter,
                "exit_diameter": hardware.exit_diameter,
                "casing_diameter": hardware.casing_diameter,
                "casing_thickness": hardware.casing_thickness,
                "casing_yield_strength": hardware.casing_yield_strength,
                "nozzle_efficiency": getattr(hardware, "nozzle_efficiency", 0.95)
            },
            "settings": settings or {}
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_motor(filepath):
        """
        Loads motor configuration from a JSON file.

        Args:
            filepath (str): Path to the JSON file to load.

        Returns:
            tuple: (Propellant, Grain, Hardware, dict)
            Returns the reconstructed objects and settings dictionary.
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        p_data = data["propellant"]
        propellant = Propellant(
            name=p_data["name"],
            density=p_data["density"],
            c_star=p_data["c_star"],
            burn_rate_a=p_data["burn_rate_a"],
            burn_rate_n=p_data["burn_rate_n"],
            k=p_data["k"],
            combustion_efficiency=p_data.get("combustion_efficiency", 0.95)
        )

        g_data = data["grain"]
        g_type = g_data.get("type", "BATES")

        if g_type == "STAR":
            grain = StarGrain(
                outer_diameter=g_data["outer_diameter"],
                web_thickness=g_data["web_thickness"],
                num_points=g_data["num_points"],
                length=g_data["length"],
                num_grains=g_data["num_grains"]
            )
        else:
            grain = BatesGrain(
                outer_diameter=g_data["outer_diameter"],
                core_diameter=g_data["core_diameter"],
                length=g_data["length"],
                num_grains=g_data["num_grains"]
            )

        h_data = data["hardware"]
        hardware = Hardware(
            throat_diameter=h_data["throat_diameter"],
            exit_diameter=h_data["exit_diameter"],
            casing_diameter=h_data["casing_diameter"],
            casing_thickness=h_data["casing_thickness"],
            casing_yield_strength=h_data.get("casing_yield_strength", 276e6),
            nozzle_efficiency=h_data.get("nozzle_efficiency", 0.95)
        )

        settings = data.get("settings", {})

        return propellant, grain, hardware, settings

    @staticmethod
    def get_default_propellants():
        """
        Returns a list of pre-configured default Propellants (e.g. KNSB).

        Returns:
            list[Propellant]: List of Propellant objects.
        """
        return [Propellant.create_knsb()]
