import matplotlib
matplotlib.use('qtagg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QSlider, QLabel, QHBoxLayout)
from PyQt6.QtCore import Qt

class GrainVisualizer(QWidget):
    """
    Widget that visualizes the Grain Cross-Section.
    Features a slider to simulate burnback.
    """
    def __init__(self):
        super().__init__()
        self.grain_data = None # Dictionary of params
        self.burn_percent = 0.0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.figure = Figure(figsize=(4, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_aspect('equal')
        self.ax.axis('off')

        layout.addWidget(self.canvas)

        # Controls
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("Burn Visualization:"))
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.update_burn)
        control_layout.addWidget(self.slider)

        layout.addLayout(control_layout)
        self.setLayout(layout)

    def update_grain(self, grain_type, params):
        """
        Update the visualizer with new grain parameters.
        params: dict of dimensions in mm.
        """
        self.grain_type = grain_type
        self.params = params
        self.plot()

    def update_burn(self, value):
        self.burn_percent = value / 100.0
        self.plot()

    def plot(self):
        self.ax.clear()
        self.ax.set_aspect('equal')
        self.ax.axis('off')

        if not self.params: return

        od = self.params.get("od", 50)
        R = od / 2.0

        # Draw Casing (Outer Circle)
        theta = np.linspace(0, 2*np.pi, 100)
        self.ax.plot(R*np.cos(theta), R*np.sin(theta), 'k-', linewidth=2)

        if self.grain_type == "BATES":
            core_d = self.params.get("core", 15)
            r_core0 = core_d / 2.0

            # Max burn depth = R - r_core0
            max_burn = R - r_core0
            current_burn = max_burn * self.burn_percent

            r_current = r_core0 + current_burn
            if r_current > R: r_current = R

            # Draw Propellant (Annulus)
            # Fill area between R and r_current
            # Matplotlib doesn't have easy annulus fill, so we fill outer black and inner white?
            # Better: use fill_between logic or Wedge.
            # Simple line drawing for MVP

            # Current Burning Surface
            self.ax.plot(r_current*np.cos(theta), r_current*np.sin(theta), 'r--', linewidth=2, label="Burn Front")

            # Fill Propellant (Green)
            # We can just fill circle R (Green) then fill circle r_current (White)
            fill_theta = np.concatenate([theta, theta[::-1]])
            x_outer = R*np.cos(theta)
            y_outer = R*np.sin(theta)
            x_inner = r_current*np.cos(theta[::-1])
            y_inner = r_current*np.sin(theta[::-1])

            self.ax.fill(np.concatenate([x_outer, x_inner]), np.concatenate([y_outer, y_inner]), color='lightgreen')

        elif self.grain_type == "STAR":
            web = self.params.get("web", 15)
            n_points = int(self.params.get("points", 5))

            R_valley = R - web
            R_tip = R_valley * 0.4 # Same heuristic as Core

            # Star Geometry Generation
            # Basic Star Polygon
            angles = np.linspace(0, 2*np.pi, n_points*2 + 1)
            radii = []
            for i in range(len(angles)-1):
                if i % 2 == 0:
                    radii.append(R_valley)
                else:
                    radii.append(R_tip)
            radii.append(R_valley)
            radii = np.array(radii)

            # Burn Offset
            # Expanding a polygon is tricky (Minkowski sum).
            # Simplified Visualization: Just expand radii linearly?
            # No, valleys become circular arcs.
            # MVP Visualization: Just expand tip radius and valley radius?
            # Valid until Tip Radius >= Valley Radius (Circularization).

            # This is hard to draw perfectly accurate without a geometry library like Shapely.
            # I will implement a "Approximate Visual" that expands the star shape.

            # Max Burn is web thickness
            current_burn = web * self.burn_percent

            # New Radii
            # Valley moves out: R_valley_new = R_valley + burn
            # Tip moves out: R_tip_new = R_tip + burn (Until it hits corner logic, but let's ignore corner rounding for viz)

            r_v_curr = R_valley + current_burn
            r_t_curr = R_tip + current_burn

            if r_v_curr > R: r_v_curr = R
            if r_t_curr > R: r_t_curr = R # Actually tips burn faster effectively circularizing.

            # If r_t_curr >= r_v_curr (Circularized)
            # In reality, star shape smooths out.
            # Let's keep the star shape but clamp radii.

            x_star = []
            y_star = []
            for i, ang in enumerate(angles):
                r = radii[i] + current_burn
                if r > R: r = R
                x_star.append(r * np.cos(ang))
                y_star.append(r * np.sin(ang))

            # Fill
            x_outer = R*np.cos(theta)
            y_outer = R*np.sin(theta)

            # Construct polygon path?
            # Fill outer circle Green
            # Fill inner Star White
            self.ax.fill(x_outer, y_outer, 'lightgreen')
            self.ax.fill(x_star, y_star, 'white')
            self.ax.plot(x_star, y_star, 'r--')

        self.canvas.draw()
