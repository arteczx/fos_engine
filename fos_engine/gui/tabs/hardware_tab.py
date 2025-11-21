from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, QLabel)
from PyQt6.QtGui import QDoubleValidator
from fos_engine.core.hardware import Hardware
from fos_engine.core.units import Units

class HardwareTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.throat_input = QLineEdit("12") # mm
        self.exit_input = QLineEdit("25") # mm
        self.casing_od_input = QLineEdit("54") # mm
        self.casing_thick_input = QLineEdit("2") # mm
        self.yield_strength_input = QLineEdit("40000") # psi (Standard for Al is ~40k psi yield)

        dbl = QDoubleValidator()
        self.throat_input.setValidator(dbl)
        self.exit_input.setValidator(dbl)
        self.casing_od_input.setValidator(dbl)
        self.casing_thick_input.setValidator(dbl)
        self.yield_strength_input.setValidator(dbl)

        form_layout.addRow("Throat Diameter (mm):", self.throat_input)
        form_layout.addRow("Exit Diameter (mm):", self.exit_input)
        form_layout.addRow("Casing Diameter (OD) (mm):", self.casing_od_input)
        form_layout.addRow("Casing Thickness (mm):", self.casing_thick_input)
        form_layout.addRow("Material Yield Strength (psi):", self.yield_strength_input)

        layout.addLayout(form_layout)

        self.calc_label = QLabel("Calculated Safety Metrics will appear here.")
        layout.addWidget(self.calc_label)

        layout.addStretch()
        self.setLayout(layout)

    def get_hardware(self):
        try:
            dt = float(self.throat_input.text())
            if dt <= 0: raise ValueError("Throat diameter must be > 0")

            return Hardware(
                throat_diameter=Units.mm_to_m(dt),
                exit_diameter=Units.mm_to_m(float(self.exit_input.text())),
                casing_diameter=Units.mm_to_m(float(self.casing_od_input.text())),
                casing_thickness=Units.mm_to_m(float(self.casing_thick_input.text())),
                casing_yield_strength=Units.psi_to_pa(float(self.yield_strength_input.text()))
            )
        except ValueError:
            return None
