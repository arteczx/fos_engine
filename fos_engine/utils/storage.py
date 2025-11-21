import json
from fos_engine.core.propellant import Propellant
from fos_engine.core.grain import BatesGrain
from fos_engine.core.hardware import Hardware
from fos_engine.core.units import Units

class DataManager:
    @staticmethod
    def save_motor(filepath, propellant, grain, hardware, settings=None):
        """
        Saves the motor configuration to a JSON file.
        Stores values in SI units (as they are in the classes).
        """
        data = {
            "propellant": {
                "name": propellant.name,
                "density": propellant.density,
                "c_star": propellant.c_star,
                "burn_rate_a": propellant.burn_rate_a,
                "burn_rate_n": propellant.burn_rate_n,
                "k": propellant.k
            },
            "grain": {
                "type": "BATES", # Future proofing
                "outer_diameter": grain.outer_diameter,
                "core_diameter": grain.core_diameter,
                "length": grain.length,
                "num_grains": grain.num_grains
            },
            "hardware": {
                "throat_diameter": hardware.throat_diameter,
                "exit_diameter": hardware.exit_diameter,
                "casing_diameter": hardware.casing_diameter,
                "casing_thickness": hardware.casing_thickness,
                "casing_yield_strength": hardware.casing_yield_strength
            },
            "settings": settings or {}
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_motor(filepath):
        """
        Loads motor configuration from a JSON file.
        Returns (Propellant, BatesGrain, Hardware, SettingsDict)
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
            k=p_data["k"]
        )

        g_data = data["grain"]
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
            casing_yield_strength=h_data.get("casing_yield_strength", 276e6)
        )

        settings = data.get("settings", {})

        return propellant, grain, hardware, settings

    @staticmethod
    def get_default_propellants():
        """
        Returns a list of default Propellant objects.
        """
        return [Propellant.create_knsb()]
