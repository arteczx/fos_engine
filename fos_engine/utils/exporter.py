class Exporter:
    @staticmethod
    def export_rasp(filepath, motor_name, results, hardware, propellant):
        """
        Export simulation results to RASP (.eng) format.

        Format:
        ; Comments
        Name Diameter(mm) Length(mm) Delays PropWeight(kg) TotalWeight(kg) Manufacturer
        t(s) F(N)
        ...
        """
        # Calculate summary stats
        times = results["time"]
        thrusts = results["thrust"]

        # Diameter in mm
        diameter_mm = hardware.casing_diameter * 1000.0
        length_mm = 100.0 # Placeholder or calc from grain

        # Weights (approx)
        # Prop weight can be integrated from burn: sum(m_dot_gen * dt)
        # Or just calculate initial mass.
        # Let's allow updating this later.
        prop_mass_kg = 0.0 # Todo: calculate or pass in
        total_mass_kg = 0.0

        with open(filepath, 'w') as f:
            f.write(f"; Exported from FOS Engine\n")
            f.write(f"; {propellant.name}\n")
            f.write(f"{motor_name} {diameter_mm:.1f} {length_mm:.1f} P {prop_mass_kg:.3f} {total_mass_kg:.3f} FOS\n")

            for t, F in zip(times, thrusts):
                # RASP requires positive values.
                if F < 0: F = 0
                f.write(f"{t:.4f} {F:.4f}\n")

            f.write(";\n")
