import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QLabel, QLineEdit, QComboBox, QFormLayout, QPushButton, QMessageBox, QHBoxLayout)
from PyQt6.QtGui import QDoubleValidator
from fos_engine.core.units import Units
from fos_engine.core.propellant import Propellant
from fos_engine.utils.storage import DataManager

class PropellantTab(QWidget):
    def __init__(self):
        super().__init__()
        self.propellant = Propellant.create_knsb() # Default
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Preset Loader
        preset_layout = QHBoxLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Custom")
        defaults = DataManager.get_default_propellants()
        for p in defaults:
            self.preset_combo.addItem(p.name, p)

        self.preset_combo.currentIndexChanged.connect(self.load_preset)
        preset_layout.addWidget(QLabel("Load Preset:"))
        preset_layout.addWidget(self.preset_combo)
        layout.addLayout(preset_layout)

        # Form
        form_layout = QFormLayout()

        self.name_input = QLineEdit(self.propellant.name)

        self.density_input = QLineEdit(str(Units.kg_m3_to_g_cm3(self.propellant.density)))
        self.cstar_input = QLineEdit(str(self.propellant.c_star))
        self.a_input = QLineEdit(str(self.propellant.burn_rate_a)) # Need to decide units for UI display for 'a'
        # Displaying 'a' is tricky because units depend on 'n'.
        # Let's display it as raw SI for now or try to convert back to Nakka's units (mm/s, MPa) for display?
        # Users usually copy paste 'a' and 'n'.
        # Let's stick to displaying SI but maybe with a tooltip.
        # Actually, displaying 'a' in SI is very small numbers (e.g. 5e-6).
        # Let's verify what user input expects. Prompt says: "a: Burn rate coefficient".
        # Let's keep it simple: raw value for now, maybe scientific notation.

        self.n_input = QLineEdit(str(self.propellant.burn_rate_n))
        self.k_input = QLineEdit(str(self.propellant.k))

        # Validators
        dbl_val = QDoubleValidator()
        self.density_input.setValidator(dbl_val)
        self.cstar_input.setValidator(dbl_val)
        self.a_input.setValidator(dbl_val)
        self.n_input.setValidator(dbl_val)
        self.k_input.setValidator(dbl_val)

        form_layout.addRow("Propellant Name:", self.name_input)
        form_layout.addRow("Density (g/cm³):", self.density_input)
        form_layout.addRow("Characteristic Velocity c* (m/s):", self.cstar_input)
        form_layout.addRow("Burn Rate Coefficient 'a' (SI):", self.a_input)
        form_layout.addRow("Burn Rate Exponent 'n':", self.n_input)
        form_layout.addRow("Specific Heat Ratio k:", self.k_input)

        layout.addLayout(form_layout)
        layout.addStretch()
        self.setLayout(layout)

    def load_preset(self, index):
        if index == 0: return # Custom
        prop = self.preset_combo.itemData(index)
        if prop:
            self.name_input.setText(prop.name)
            self.density_input.setText(str(Units.kg_m3_to_g_cm3(prop.density)))
            self.cstar_input.setText(str(prop.c_star))
            self.a_input.setText(str(prop.burn_rate_a))
            self.n_input.setText(str(prop.burn_rate_n))
            self.k_input.setText(str(prop.k))

    def get_propellant(self):
        try:
            return Propellant(
                name=self.name_input.text(),
                density=Units.g_cm3_to_kg_m3(float(self.density_input.text())),
                c_star=float(self.cstar_input.text()),
                burn_rate_a=float(self.a_input.text()),
                burn_rate_n=float(self.n_input.text()),
                k=float(self.k_input.text())
            )
        except ValueError:
            return None
