from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QDialogButtonBox

import re
from gui.gui_acctedit import  Ui_AccountEditor
from util.Accounts import Account, SavingAccount
from main import application
from util.Application import FC_NewAccount, FC_UpdateAccount
import logic.logic_misc as logic_misc

class AcctEdit(QtWidgets.QDialog, Ui_AccountEditor):
    def __init__(self, acct:Account, parent=None):
        super(AcctEdit, self).__init__(parent)
        self.setupUi(self)
        self.groupBox.setTitle("Edit Account...")
        self.setWindowTitle("Edit Account...")
        self.accountName = acct.get_name()
        self.buttonBox.clicked.connect(self.buttonClick)

        if (type(acct) == SavingAccount):
            self.rb_savings.setChecked(True)
        else:
            self.rb_acct.setChecked(True)

        self.buttonBox.clicked.connect(self.buttonClick)

    def buttonClick(self, button:QDialogButtonBox.StandardButton):
        if button == QDialogButtonBox.StandardButton.Save:
            self.accept()
        else:
            self.reject()

    def accept(self):
        newacct: Account = None
        if (self.rb_savings.isChecked()):
            newacct = SavingAccount(self.accountName)
        else:
            newacct = Account(self.accountName)

        print(application.bank.openAccount(newacct))
        application.flagFloatingChange()
        super().accept()

    def reject(self):
        super().reject()



class AcctEdit_New(QtWidgets.QDialog, Ui_AccountEditor):
    def __init__(self, parent=None):
        super(AcctEdit_New, self).__init__(parent)
        self.setupUi(self)
        self.groupBox.setTitle("New Account...")
        self.setWindowTitle("New Account...")
        self.balance.setEnabled(False)
        self.balance.setToolTip("New accounts must start from the minimum balance.")
        self.buttonBox.clicked.connect(self.buttonClick)

    def buttonClick(self, button:QDialogButtonBox.StandardButton):

        if button == QDialogButtonBox.StandardButton.Save:
            self.accept()
        else:
            self.reject()


    def accept(self):
        match = re.fullmatch("[a-zA-Z0-9 ]{0,20}", self.accountName.text())
        if (match == None):
            logic_misc.infoDialog("Only spaces, letters and numbers are allowed for account names.")
            return

        if (application.bank.fetchAccount(self.accountName.text()) != None):
            logic_misc.infoDialog("Account name in use. Try another name.")
            return

        newacct: Account = None
        type = 0
        if (self.rb_savings.isChecked()):
            type = 1
            newacct = SavingAccount(self.accountName.text())
        elif (self.rb_acct.isChecked()):
            newacct = Account(self.accountName.text())


        application.bank.openAccount(newacct)
        super().accept()

    def reject(self):
        super().reject()