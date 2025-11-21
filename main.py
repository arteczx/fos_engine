import sys
import os
# Add the project root to python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from fos_engine.gui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
