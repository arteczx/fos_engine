from fos_engine.core.propellant import Propellant
from fos_engine.core.grain import BatesGrain
from fos_engine.core.hardware import Hardware
from fos_engine.core.simulation import Simulation
from fos_engine.core.units import Units
import matplotlib.pyplot as plt

def test_simulation():
    # Create KNSB Propellant
    prop = Propellant.create_knsb()

    # Create Grain
    # 20mm Core, 50mm OD, 100mm Length, 3 Grains
    grain = BatesGrain(
        outer_diameter=Units.mm_to_m(50),
        core_diameter=Units.mm_to_m(18),
        length=Units.mm_to_m(100),
        num_grains=3
    )

    # Create Hardware
    # Throat 12mm, Exit 20mm, Casing OD 54mm (ID ~50), Thickness 2mm
    hw = Hardware(
        throat_diameter=Units.mm_to_m(12),
        exit_diameter=Units.mm_to_m(25),
        casing_diameter=Units.mm_to_m(54),
        casing_thickness=Units.mm_to_m(2)
    )

    # Run Simulation
    sim = Simulation(prop, grain, hw, time_step=0.01)
    results = sim.run()

    print("Max Pressure (Pa):", max(results["pressure"]))
    print("Max Pressure (PSI):", Units.pa_to_psi(max(results["pressure"])))
    print("Max Thrust (N):", max(results["thrust"]))
    print("Total Impulse (Ns):", sum(results["thrust"]) * sim.dt)
    print("Burn Time (s):", results["time"][-1])

    # Simple plot check (blocking if run locally, but here just for code correctness check)
    # plt.plot(results["time"], results["pressure"])
    # plt.show()

if __name__ == "__main__":
    test_simulation()
