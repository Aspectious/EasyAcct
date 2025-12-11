# main.py
# Main file for program "EasyAcct"
# aspectious.dev


"""
This stores a static reference of the Application class to
handle connections and the floating bank reference outside 
of GUI logic scripts.
"""
from util.Application import Application
application: Application = Application()


if __name__ == '__main__':
    from PyQt6 import QtWidgets

    from logic.logic_main import MainWindow
    from util.db.Connection import *

    program = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(program.exec())
