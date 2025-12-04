# main.py
# Main file for program "EasyAcct"
# aspectious.dev
import sys
from PyQt6 import QtWidgets

from gui.gui_main_logic import MainWindow
from util.db.connmgr import *

if __name__ == '__main__':

    application = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(application.exec())
