from PyQt6 import QtWidgets

from gui.gui_acctedit import  Ui_AccountEditor
from util.Accounts import Account, SavingAccount

class AcctEdit(QtWidgets.QDialog, Ui_AccountEditor):
    def __init__(self, acct:Account, parent=None):
        super(AcctEdit, self).__init__(parent)
        self.setupUi(self)
        self.groupBox.setTitle("Edit Account...")
        self.setWindowTitle("Edit Account...")
        self.accountName = acct.account_name
        if (type(acct) == SavingAccount):
            self.rb_savings.setChecked(True)
        else:
            self.rb_acct.setChecked(True)

        self.buttonBox.clicked.connect(self.buttonClick)

    def buttonClick(self, button):
        print("buttonClick")
        print(type(button))
        print(button.text())



class AcctEdit_New(QtWidgets.QDialog, Ui_AccountEditor):
    def __init__(self, parent=None):
        super(AcctEdit_New, self).__init__(parent)
        self.setupUi(self)
        self.groupBox.setTitle("New Account...")
        self.setWindowTitle("New Account...")
        self.buttonBox.clicked.connect(self.buttonClick)

    def buttonClick(self, button):
        if (button.text() == "Save"):
            self.close()
        else:
            self.close()