import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QFileDialog, QMenuBar, QMenu, QMessageBox)
from PyQt6.QtGui import QAction

from fos_engine.gui.tabs.propellant_tab import PropellantTab
from fos_engine.gui.tabs.grain_tab import GrainTab
from fos_engine.gui.tabs.hardware_tab import HardwareTab
from fos_engine.gui.tabs.simulation_tab import SimulationTab

from fos_engine.core.simulation import Simulation
from fos_engine.core.units import Units
from fos_engine.utils.storage import DataManager
from fos_engine.utils.exporter import Exporter

class MainWindow(QMainWindow):
    """
    The Main Window of the FOS Engine Application.
    Orchestrates the UI tabs and manages the application state (Simulation Logic).
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FOS Engine - Solid Motor Design")
        self.resize(1000, 700)

        self.init_ui()

    def init_ui(self):
        """Initialize UI components and Tabs."""
        self.tabs = QTabWidget()

        self.propellant_tab = PropellantTab()
        self.grain_tab = GrainTab()
        self.hardware_tab = HardwareTab()
        self.simulation_tab = SimulationTab(self)

        self.tabs.addTab(self.propellant_tab, "1. Propellant")
        self.tabs.addTab(self.grain_tab, "2. Grain Geometry")
        self.tabs.addTab(self.hardware_tab, "3. Hardware")
        self.tabs.addTab(self.simulation_tab, "4. Simulation")

        self.setCentralWidget(self.tabs)

        # Menus
        menu = self.menuBar()
        file_menu = menu.addMenu("File")

        save_action = QAction("Save Motor Design", self)
        save_action.triggered.connect(self.save_design)
        file_menu.addAction(save_action)

        load_action = QAction("Load Motor Design", self)
        load_action.triggered.connect(self.load_design)
        file_menu.addAction(load_action)

    def run_simulation_logic(self):
        """
        Triggered by the Simulation Tab.
        Gathers data from all tabs, instantiates the Simulation engine,
        runs the physics, and updates the results view.
        """
        # 1. Gather Inputs
        prop = self.propellant_tab.get_propellant()
        grain = self.grain_tab.get_grain()
        hw = self.hardware_tab.get_hardware()

        if not (prop and grain and hw):
            QMessageBox.warning(self, "Input Error", "Please check all fields in Tabs 1-3.")
            return

        # 2. Run Simulation
        sim = Simulation(prop, grain, hw, time_step=0.005)
        results = sim.run(use_erosive_burning=self.simulation_tab.erosive_check.isChecked())

        # 3. Process Metrics
        max_p = max(results["pressure"]) if results["pressure"] else 0
        max_f = max(results["thrust"]) if results["thrust"] else 0
        total_impulse = sum(results["thrust"]) * sim.dt
        burn_time = results["time"][-1] if results["time"] else 0

        # Propellant Mass Ejected Summation
        total_mass_ejected = sum(results["mass_flow_out"]) * sim.dt
        isp = (total_impulse / (total_mass_ejected * 9.81)) if total_mass_ejected > 0 else 0

        metrics = {
            "max_pressure_psi": Units.pa_to_psi(max_p),
            "max_thrust": max_f,
            "total_impulse": total_impulse,
            "burn_time": burn_time,
            "isp": isp
        }

        hardware_safety = {
            "burst_pressure": hw.get_burst_pressure()
        }

        # Cache current state for export
        self.current_results = results
        self.current_metrics = metrics
        self.current_hw = hw
        self.current_prop = prop

        # 4. Update GUI
        self.simulation_tab.update_results(results, metrics, hardware_safety)

    def save_design(self):
        """Save current configuration to JSON."""
        fname, _ = QFileDialog.getSaveFileName(self, "Save Motor", "", "JSON Files (*.json)")
        if fname:
            prop = self.propellant_tab.get_propellant()
            grain = self.grain_tab.get_grain()
            hw = self.hardware_tab.get_hardware()
            settings = {"erosive": self.simulation_tab.erosive_check.isChecked()}
            if prop and grain and hw:
                DataManager.save_motor(fname, prop, grain, hw, settings)

    def load_design(self):
        """Load configuration from JSON and populate tabs."""
        fname, _ = QFileDialog.getOpenFileName(self, "Load Motor", "", "JSON Files (*.json)")
        if fname:
            try:
                prop, grain, hw, settings = DataManager.load_motor(fname)

                # Propellant Tab
                self.propellant_tab.name_input.setText(prop.name)
                self.propellant_tab.density_input.setText(str(Units.kg_m3_to_g_cm3(prop.density)))
                self.propellant_tab.cstar_input.setText(str(prop.c_star))
                self.propellant_tab.a_input.setText(str(prop.burn_rate_a))
                self.propellant_tab.n_input.setText(str(prop.burn_rate_n))
                self.propellant_tab.k_input.setText(str(prop.k))

                # Grain Tab
                self.grain_tab.od_input.setText(str(Units.m_to_mm(grain.outer_diameter)))
                self.grain_tab.core_input.setText(str(Units.m_to_mm(grain.core_diameter)))
                self.grain_tab.length_input.setText(str(Units.m_to_mm(grain.length)))
                self.grain_tab.count_input.setText(str(grain.num_grains))

                # Hardware Tab
                self.hardware_tab.throat_input.setText(str(Units.m_to_mm(hw.throat_diameter)))
                self.hardware_tab.exit_input.setText(str(Units.m_to_mm(hw.exit_diameter)))
                self.hardware_tab.casing_od_input.setText(str(Units.m_to_mm(hw.casing_diameter)))
                self.hardware_tab.casing_thick_input.setText(str(Units.m_to_mm(hw.casing_thickness)))
                self.hardware_tab.yield_strength_input.setText(str(Units.pa_to_psi(hw.casing_yield_strength)))

                # Settings
                if "erosive" in settings:
                    self.simulation_tab.erosive_check.setChecked(settings["erosive"])

                QMessageBox.information(self, "Loaded", "Motor design loaded successfully.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load: {e}")

    def export_rasp(self):
        """Export the last simulation result to a .eng file."""
        if not hasattr(self, 'current_results'): return
        fname, _ = QFileDialog.getSaveFileName(self, "Export RASP", "", "Engine Files (*.eng)")
        if fname:
            Exporter.export_rasp(fname, "FOS_Motor", self.current_results, self.current_hw, self.current_prop)
            QMessageBox.information(self, "Exported", f"Saved to {fname}")

def main():
    """Application Entry Point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
