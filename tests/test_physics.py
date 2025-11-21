from fos_engine.core.propellant import Propellant
from fos_engine.core.grain import BatesGrain
from fos_engine.core.star_grain import StarGrain
from fos_engine.core.hardware import Hardware
from fos_engine.core.simulation import Simulation
from fos_engine.core.units import Units

def test_physics():
    # Test BATES (Baseline)
    print("--- Testing BATES Grain ---")
    prop = Propellant.create_knsb()
    grain = BatesGrain(
        outer_diameter=Units.mm_to_m(50),
        core_diameter=Units.mm_to_m(18),
        length=Units.mm_to_m(100),
        num_grains=3
    )
    hw = Hardware(
        throat_diameter=Units.mm_to_m(12),
        exit_diameter=Units.mm_to_m(25),
        casing_diameter=Units.mm_to_m(54),
        casing_thickness=Units.mm_to_m(2)
    )
    sim = Simulation(prop, grain, hw, time_step=0.01)
    results = sim.run(use_erosive_burning=True)

    print(f"Max Pressure: {Units.pa_to_psi(max(results['pressure'])):.2f} PSI")
    print(f"Max Thrust: {max(results['thrust']):.2f} N")
    print(f"Burn Time: {results['time'][-1]:.2f} s")

    # Test STAR
    print("\n--- Testing STAR Grain ---")
    # Same OD, but Star geometry. Web approx (50/2 - 18/2)/2 ~ 8mm?
    # Let's say Web = 15mm (Deep star)
    star_grain = StarGrain(
        outer_diameter=Units.mm_to_m(50),
        web_thickness=Units.mm_to_m(15),
        num_points=5,
        length=Units.mm_to_m(100),
        num_grains=3
    )

    sim_star = Simulation(prop, star_grain, hw, time_step=0.01)
    results_star = sim_star.run()

    print(f"Max Pressure: {Units.pa_to_psi(max(results_star['pressure'])):.2f} PSI")
    print(f"Max Thrust: {max(results_star['thrust']):.2f} N")
    print(f"Burn Time: {results_star['time'][-1]:.2f} s")

if __name__ == "__main__":
    test_physics()
