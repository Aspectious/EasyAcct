"""
logic_misc.py

Miscellaneous logic for GUIs, such as confirmation dialog, and other quick dialogs.

"""
from PyQt6.QtWidgets import QMessageBox

def confirmDialog(message:str):
    result = QMessageBox.question(None, "Confirm", message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    if (result == QMessageBox.StandardButton.Yes):
        return True
    else:
        return False

def infoDialog(message:str):
    QMessageBox.information(None, "Information", message)


def checkString(string:str):
    try:
        str(string)
        return True
    except:
        QMessageBox.critical(None, "Invalid Input", "Invalid Input")
        return False