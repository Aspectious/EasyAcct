import time

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt, QModelIndex

from gui.gui_main import Ui_MainWindow
from gui.gui_conn_logic import ConnMgr
from gui.gui_acctedit_logic import AcctEdit, AcctEdit_New

from util.db.connmgr import MySQLConnection, SqLiteConnection, Connection, ConnectionState


from util.Accounts import Account, SavingAccount
from util.Bank import Bank
from util.Transaction import Transaction

class AccountTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.header = ["Index","Account","Type","Balance"]
        self.columncount = 4
        self.datat = []

    def addRecord(self, record:Account):
        self.beginInsertRows(QtCore.QModelIndex(), len(self.datat), len(self.datat))
        accounttype = "Account"
        if type(record) is SavingAccount:
            accounttype = "Savings Account"
        self.datat.append([0, record.account_name, accounttype, f'{record.account_balance:.2f}'])
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


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    CONDETAILS = None
    CONTYPE = None
    CONPATH = None
    CONNECTION:Connection = None
    @staticmethod
    def setConnection(type, details):
        MainWindow.CONTYPE = type
        MainWindow.CONDETAILS = details
        if (type == 1):
            MainWindow.CONPATH = "jdbc:mysql://" + MainWindow.CONDETAILS[0] + ":" + str(MainWindow.CONDETAILS[1]) + "/" + MainWindow.CONDETAILS[2]

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.mb_c_connectionoptions.triggered.connect(self.openConnectionOptions)
        self.mb_a_open.triggered.connect(self.openNewAccount)
        self.vD_Table.clicked.connect(self.tableClick)
        self.Bank = Bank()

        # Developer Mode
        self.setConnection(1, ["localhost", 3306, "accountant", "bankingIsEasy123", "EasyAcct", "PrimaryAccounts", "PrimaryAccounts.Transactions"])
        self.connectDatabase()

    def openNewAccount(self):
        dialog = AcctEdit_New()
        dialog.exec()

    def openConnectionOptions(self):
        dialog = ConnMgr()
        dialog.exec()
        if (MainWindow.CONDETAILS != None): #Mysql Start
            self.connectDatabase()

    def addActiontoHistory(self, action):
        self.vS_History.addItem(action)

    def tableClick(self, index: QModelIndex):
        row = index.row()
        print(row)
        self.SelectedAccount:Account = self.ACCOUNTLIST[row]
        self.vP_AccountNameBox.setText(self.SelectedAccount.account_name)
        acctype = "Account"
        if (type(self.SelectedAccount) == SavingAccount):
            acctype = "Savings Account"
        self.vP_AccountTypeBox.setText(acctype)
        self.vP_AccountBalanceBox.setText(str(self.SelectedAccount.account_balance))
        print(self.SelectedAccount.account_name)


    def connectDatabase(self):
        try:
            self.vD_DatabaseTitle.setText("Loading Database from [" + MainWindow.CONPATH + "]...")
            self.vS_ProgressBar.setValue(50)
            if (MainWindow.CONTYPE == 0):
                file = MainWindow.CONDETAILS[0]
                tbl1 = MainWindow.CONDETAILS[1]
                tbl2 = MainWindow.CONDETAILS[2]
                MainWindow.CONNECTION = SqLiteConnection(file, tbl1, tbl2)
            elif (MainWindow.CONTYPE == 1):
                 # For Reference, mysql order is : Host, Port, Schema, Tbl1, Tbl2, username, password
                # but order for connection method is host, port, uname, passwd, db, tbl1, tbl2
                    host = MainWindow.CONDETAILS[0]
                    port = MainWindow.CONDETAILS[1]
                    uname = MainWindow.CONDETAILS[2]
                    passwd = MainWindow.CONDETAILS[3]
                    db = MainWindow.CONDETAILS[4]
                    tbl1 = MainWindow.CONDETAILS[5]
                    tbl2 = MainWindow.CONDETAILS[6]
                    MainWindow.CONNECTION = MySQLConnection(host, port, uname, passwd, db, tbl1, tbl2)
                    conn = MainWindow.CONNECTION.openConnection()
                    if (conn == 0):
                        self.vD_DatabaseTitle.setText("Connection Succeeded")
                        self.vS_ProgressBar.setValue(100)
                        self.addActiontoHistory("Connected to Database " + MainWindow.CONPATH)
                        time.sleep(0.5)
                        self.vD_DatabaseTitle.setText("[" + MainWindow.CONPATH + "] - Loading...")
                        self.vS_ProgressBar.setValue(0)
                        MainWindow.CONNECTION.closeConnection()
                        self.loadUsers()
                    else:
                        self.vD_DatabaseTitle.setText("Failed to Connect to Database [" + MainWindow.CONPATH + "]. Check Connection Settings.")
            else:
                print("idk man")
        except Exception as e:
            print(e)

    def loadAllFromDB(self):
        if (MainWindow.CONTYPE == None):
            return
        conn:Connection = MainWindow.CONNECTION
        if (conn.state == ConnectionState.DISCONNECTED):
            conn.openConnection()
        if conn.state == ConnectionState.CONNECTED:
            try:
                accts = conn.fetchAllAccounts()
                for account in accts:
                    if (account[2] == 1):  # Default Account
                        acctobj = SavingAccount(Account(account[1], account[3]))
                    else:
                        acctobj = Account(account[1], account[3])
                        self.Bank.openAccount(acctobj)
            except Exception as e:
                print(e)

        if conn.state == ConnectionState.CONNECTED:
            try:
                trans = conn.fetchAllTransactions()
                for transaction in trans:
                    transtype = "Other"
                    if (transaction[2] == 1):
                        transtype = "Deposit"
                    else:
                        transtype = "Withdraw"

                    acct = self.Bank.fetchAccount(transaction[1])

                    transactionobj = Transaction(acct, transaction[2], transaction[3], transaction[4])
                    self.Bank.writeTransaction(transaction)
            except Exception as e:
                print(e)

    def loadAcctTable(self, accountlist):
        self.DATAMODEL = AccountTableModel()

        for account in self.Bank.fetchAllAccounts():
            self.DATAMODEL.addRecord(account)

        self.vD_Table.setModel(self.DATAMODEL)




