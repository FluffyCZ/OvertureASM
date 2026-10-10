import sys
from PyQt5.QtWidgets import QApplication
from gui.gui import AssemblerGUI

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AssemblerGUI()
    ex.show()
    sys.exit(app.exec_())