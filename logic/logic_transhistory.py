from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt

from gui.gui_transhistory import Ui_TransHistory
from util.Accounts import Account
from util.Transaction import Transaction
from logic.logic_main import MainWindow as MW

class TransactionTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.header = ["Date", "Type", "Amount"]
        self.columncount = 3
        self.datat = []

    def addRecord(self, record:Transaction):
        self.beginInsertRows(QtCore.QModelIndex(), len(self.datat), len(self.datat))
        transtype = "Other"
        if (record.type == 1):
            transtype = "Deposit"
        else:
            transtype = "Withdraw"
        self.datat.append([record.date, transtype, f'{record.account:.2f}'])
        self.endInsertRows()

    def rowCount(self, parent=None):
        return len(self.datat)

    def columnCount(self, parent=None):
        return self.columncount

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        try:
            self.datat[index.row()][index.column()] = value
            self.dataChanged.emit(index.row(), index.column(), role)
            return True
        except:
            return False

    def fetchAccountList(self):
        return self.datat
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
        super(TransHistory, self).__init__(parent)
        self.setupUi(self)

    def lookupTransactionsForAccount(self, acc:Account):
        conn = MW.CONNECTION
        if (conn.state == "Connected"):
            conn.fetchTransactionsFromAccount()
        else:
            print("uh oh")
            return

