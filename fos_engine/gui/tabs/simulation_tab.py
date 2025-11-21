import matplotlib
matplotlib.use('qtagg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QCheckBox)

class SimulationTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.last_results = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Controls
        controls = QHBoxLayout()
        self.run_btn = QPushButton("Run Simulation")
        self.run_btn.clicked.connect(self.run_simulation)

        self.export_btn = QPushButton("Export OpenRocket (.eng)")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.main_window.export_rasp)

        self.erosive_check = QCheckBox("Enable Erosive Burning Model")

        controls.addWidget(self.run_btn)
        controls.addWidget(self.export_btn)
        controls.addWidget(self.erosive_check)
        controls.addStretch()
        layout.addLayout(controls)

        # Plots
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)

        self.ax1 = self.figure.add_subplot(211)
        self.ax2 = self.figure.add_subplot(212)
        self.figure.tight_layout()

        layout.addWidget(self.canvas)

        # Results
        self.results_label = QLabel("Results: Not Run")
        layout.addWidget(self.results_label)

        self.setLayout(layout)

    def run_simulation(self):
        self.main_window.run_simulation_logic()

    def update_results(self, results, metrics, hardware_safety):
        self.last_results = results
        self.export_btn.setEnabled(True)

        # Update Plots
        self.ax1.clear()
        self.ax2.clear()

        t = results["time"]
        f = results["thrust"]
        p = [val * 1.45038e-4 for val in results["pressure"]] # Pa to PSI

        self.ax1.plot(t, f, 'b-')
        self.ax1.set_ylabel("Thrust (N)")
        self.ax1.set_xlabel("Time (s)")
        self.ax1.grid(True)

        burst_pressure_psi = hardware_safety["burst_pressure"] * 1.45038e-4

        self.ax2.plot(t, p, 'r-', label="Chamber Pressure")
        self.ax2.axhline(y=burst_pressure_psi, color='k', linestyle='--', label="Burst Pressure")
        self.ax2.set_ylabel("Pressure (PSI)")
        self.ax2.set_xlabel("Time (s)")
        self.ax2.legend()
        self.ax2.grid(True)

        self.canvas.draw()

        # Update Text
        txt = (f"Max Pressure: {metrics['max_pressure_psi']:.1f} PSI\n"
               f"Max Thrust: {metrics['max_thrust']:.1f} N\n"
               f"Total Impulse: {metrics['total_impulse']:.1f} Ns\n"
               f"Burn Time: {metrics['burn_time']:.2f} s\n"
               f"Isp: {metrics['isp']:.1f} s")
        self.results_label.setText(txt)
