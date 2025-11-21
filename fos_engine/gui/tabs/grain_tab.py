from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QLabel)
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from fos_engine.core.grain import BatesGrain
from fos_engine.core.units import Units

class GrainTab(QWidget):
    """
    GUI Tab for configuring Propellant Grain Geometry.
    Currently supports BATES grains.
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.type_combo = QComboBox()
        self.type_combo.addItems(["BATES"]) # Placeholder for future grain types

        self.od_input = QLineEdit("50") # mm
        self.core_input = QLineEdit("18") # mm
        self.length_input = QLineEdit("100") # mm
        self.count_input = QLineEdit("3")

        self.od_input.setValidator(QDoubleValidator())
        self.core_input.setValidator(QDoubleValidator())
        self.length_input.setValidator(QDoubleValidator())
        self.count_input.setValidator(QIntValidator())

        form_layout.addRow("Grain Type:", self.type_combo)
        form_layout.addRow("Outer Diameter (mm):", self.od_input)
        form_layout.addRow("Core Diameter (mm):", self.core_input)
        form_layout.addRow("Length per Grain (mm):", self.length_input)
        form_layout.addRow("Number of Grains:", self.count_input)

        layout.addLayout(form_layout)

        # Info / Validation text
        self.info_label = QLabel("Configure the grain geometry.")
        layout.addWidget(self.info_label)

        layout.addStretch()
        self.setLayout(layout)

    def get_grain(self):
        """
        Construct and return the Grain object from UI inputs.
        """
        try:
            return BatesGrain(
                outer_diameter=Units.mm_to_m(float(self.od_input.text())),
                core_diameter=Units.mm_to_m(float(self.core_input.text())),
                length=Units.mm_to_m(float(self.length_input.text())),
                num_grains=int(self.count_input.text())
            )
        except ValueError:
            return None
