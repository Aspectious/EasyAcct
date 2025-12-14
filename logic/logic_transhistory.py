from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt
from datetime import datetime

from gui.gui_transhistory import Ui_TransHistory
from util.Accounts import Account
from util.Transaction import Transaction
import logic.logic_misc as logic_misc
from main import application

"""
This class defines how the history of transactions for an account should go.
"""
class TransactionTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.header = ["Date", "Type", "Amount"]
        self.columncount = 3
        self.datat = []

    def resetData(self, data:list[list[str]]):
        self.beginResetModel()
        self.datat.clear()
        self.datat = data
        self.endResetModel()


    def rowCount(self, parent=None):
        return len(self.datat)

    def columnCount(self, parent=None):
        return self.columncount

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if (role == Qt.ItemDataRole.DisplayRole):
            return self.datat[index.row()][index.column()]

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.header[section]
            return section
        return super().headerData(section, orientation, role)



class TransHistory(QtWidgets.QDialog, Ui_TransHistory):
    def __init__(self, acct:Account, parent=None):
        super().__init__()
        self.setupUi(self)
        self.model = TransactionTableModel()

        transactionhistory = application.bank.fetchAllTransactionsFromAccount(acct.get_name())

        strdata:list[list[str]] = []
        for transaction in transactionhistory:
            transtype = "Other"
            if (transaction.getType() == 1):
                transtype = "Deposit"
            elif (transaction.getType() == -1):
                transtype = "Withdraw"
            strdata.append([transaction.getDate().isoformat(), transtype, f'{transaction.getAmount():.2f}'])

        self.model.resetData(strdata)

        self.tableView.setModel(self.model)





