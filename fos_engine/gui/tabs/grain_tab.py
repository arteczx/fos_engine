from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QLabel, QHBoxLayout)
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from fos_engine.core.grain import BatesGrain
from fos_engine.core.star_grain import StarGrain
from fos_engine.core.units import Units
from fos_engine.gui.widgets.grain_visualizer import GrainVisualizer

class GrainTab(QWidget):
    """
    GUI Tab for configuring Propellant Grain Geometry.
    Supports BATES and STAR grains with Real-time Visualization.
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # Left Panel: Inputs
        left_panel = QVBoxLayout()
        form_layout = QFormLayout()

        self.type_combo = QComboBox()
        self.type_combo.addItems(["BATES", "STAR"])
        self.type_combo.currentIndexChanged.connect(self.update_ui_mode)

        # Common Inputs
        self.od_input = QLineEdit("50") # mm
        self.length_input = QLineEdit("100") # mm
        self.count_input = QLineEdit("3")

        # BATES Specific
        self.core_input = QLineEdit("18") # mm
        self.core_label = QLabel("Core Diameter (mm):")

        # STAR Specific (Hidden by default)
        self.web_input = QLineEdit("15") # mm
        self.points_input = QLineEdit("5")
        self.web_label = QLabel("Web Thickness (mm):")
        self.points_label = QLabel("Number of Points:")

        # Validators
        dbl = QDoubleValidator()
        self.od_input.setValidator(dbl)
        self.length_input.setValidator(dbl)
        self.core_input.setValidator(dbl)
        self.web_input.setValidator(dbl)
        self.points_input.setValidator(QIntValidator())
        self.count_input.setValidator(QIntValidator())

        # Connect updates to visualizer
        self.od_input.textChanged.connect(self.update_visualizer)
        self.length_input.textChanged.connect(self.update_visualizer)
        self.core_input.textChanged.connect(self.update_visualizer)
        self.web_input.textChanged.connect(self.update_visualizer)
        self.points_input.textChanged.connect(self.update_visualizer)
        self.count_input.textChanged.connect(self.update_visualizer)

        form_layout.addRow("Grain Type:", self.type_combo)
        form_layout.addRow("Outer Diameter (mm):", self.od_input)
        form_layout.addRow("Length per Grain (mm):", self.length_input)
        form_layout.addRow("Number of Grains:", self.count_input)

        # BATES Row
        form_layout.addRow(self.core_label, self.core_input)

        # STAR Rows
        form_layout.addRow(self.web_label, self.web_input)
        form_layout.addRow(self.points_label, self.points_input)

        left_panel.addLayout(form_layout)
        left_panel.addStretch()

        # Right Panel: Visualizer
        self.visualizer = GrainVisualizer()

        main_layout.addLayout(left_panel, stretch=1)
        main_layout.addWidget(self.visualizer, stretch=1)

        self.setLayout(main_layout)

        # Initialize State
        self.update_ui_mode()

    def update_ui_mode(self):
        mode = self.type_combo.currentText()
        is_bates = (mode == "BATES")

        self.core_label.setVisible(is_bates)
        self.core_input.setVisible(is_bates)

        self.web_label.setVisible(not is_bates)
        self.web_input.setVisible(not is_bates)
        self.points_label.setVisible(not is_bates)
        self.points_input.setVisible(not is_bates)

        self.update_visualizer()

    def update_visualizer(self):
        try:
            mode = self.type_combo.currentText()
            od = float(self.od_input.text() or 0)

            params = {"od": od}

            if mode == "BATES":
                params["core"] = float(self.core_input.text() or 0)
            else:
                params["web"] = float(self.web_input.text() or 0)
                params["points"] = int(self.points_input.text() or 0)

            self.visualizer.update_grain(mode, params)
        except ValueError:
            pass

    def get_grain(self):
        """
        Construct and return the Grain object from UI inputs.
        """
        try:
            mode = self.type_combo.currentText()
            od = Units.mm_to_m(float(self.od_input.text()))
            length = Units.mm_to_m(float(self.length_input.text()))
            count = int(self.count_input.text())

            if mode == "BATES":
                core = Units.mm_to_m(float(self.core_input.text()))
                return BatesGrain(od, core, length, count)
            else:
                web = Units.mm_to_m(float(self.web_input.text()))
                points = int(self.points_input.text())
                return StarGrain(od, web, points, length, count)

        except ValueError:
            return None
