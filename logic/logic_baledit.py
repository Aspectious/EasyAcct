from PyQt6 import QtWidgets
from datetime import datetime

from gui.gui_baledit import Ui_BalEditor
import logic.logic_misc as logic_misc
from util.Application import FC_NewTransaction

from util.Transaction import Transaction
from util.Accounts import Account, SavingAccount
from main import application

"""
This class was originally designed to allow changes to account balances, but ever since the transaction system was implemented
it serves the role of creating and applying the delta to accounts.
"""
class BalEdit(QtWidgets.QDialog, Ui_BalEditor):
    def __init__(self, accountName:str, accountType:str, typesel:int, parent=None):
        super().__init__()
        self.setupUi(self)

        self.t_accountname.setText(accountName)
        self.t_accounttype.setText(accountType)


        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(super().reject)


        if (typesel == 1):
            self.rb_deposit.setChecked(True)
            self.rb_set.setChecked(False)
            self.rb_withdraw.setChecked(False)
        elif (typesel == -1):
            self.rb_deposit.setChecked(False)
            self.rb_set.setChecked(False)
            self.rb_withdraw.setChecked(True)
        elif (typesel == 0):
            self.rb_deposit.setChecked(False)
            self.rb_set.setChecked(True)
            self.rb_withdraw.setChecked(False)
        else:
            self.rb_deposit.setChecked(False)
            self.rb_set.setChecked(False)
            self.rb_withdraw.setChecked(False)


    def fetchTypeSel(self) -> int:
        if (self.rb_deposit.isChecked()):
            return 1
        elif (self.rb_set.isChecked()):
            return 0
        elif (self.rb_withdraw.isChecked()):
            return -1
        else:
            return 99

    """
    Validates input according to the following rules:
    - A type must be selected
    - The input must be greater than zero
    - The input must be greater than the account's minimum balance (if applicable)
    """
    def validateInput(self) -> bool:
        sel = self.fetchTypeSel()
        amt = self.box_amount.value()
        acct = application.bank.fetchAccount(self.t_accountname.text())
        if (sel == 99):
            logic_misc.infoDialog("Please select a transaction type.")
            return False

        # check if above zero
        if (amt <= 0):
            logic_misc.infoDialog("Amount must be greater than zero.")
            return False

        if (sel == -1):
            if (type(acct) == SavingAccount):
                if (acct.get_balance() - amt < SavingAccount.MINIMUM):
                    logic_misc.infoDialog("Cannot overdraw past minimum balance.")
                    return False
            else:
                if (acct.get_balance() - amt < 0):
                    logic_misc.infoDialog("Cannot overdraw on account.")
                    return False

        # check if below minimums

        if (acct is None):
            logic_misc.infoDialog("Account name not found. Please exit and try again.")
            return False
        if (sel == 0):
            if (type(acct) == SavingAccount):
                if (amt < SavingAccount.MINIMUM):
                    logic_misc.infoDialog(f"Amount must be greater than the minimum balance. \n MINIMUM = {SavingAccount.MINIMUM}")
                    return False
        return True




    """
    Handles submission and checks with validation.
    """
    def submit(self):
        val = self.validateInput()
        if (val == False):
            return
        else:
            acctname = self.t_accountname.text()
            dt = datetime.now()
            type = self.fetchTypeSel()
            amt = self.box_amount.value()

            if (type != 0):
                tr = Transaction(acctname, dt, type, amt)
            else:
                currentbal = application.bank.fetchAccount(acctname).get_balance()
                desiredbal = amt
                delta = desiredbal - currentbal
                if (delta <= 0):
                    type = -1
                    delta = delta * -1
                else:
                    type = 1
                tr = Transaction(acctname, dt, type, delta)
            resp = application.bank.writeNewTransaction(tr)
            if (resp == False):
                logic_misc.infoDialog("Something went wrong writing new transaction.")
                return

            super().accept()
