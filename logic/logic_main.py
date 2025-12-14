from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import Qt, QModelIndex

from gui.gui_main import Ui_MainWindow
from logic.logic_acctedit import AcctEdit_New, AcctEdit
from logic.logic_connmgr import ConnMgr
from logic.logic_baledit import BalEdit
from logic.logic_transhistory import TransHistory
import logic.logic_misc as logic_misc

from main import application as application

from util.Connection import SqLiteConnection, Connection, ConnectionState


from util.Accounts import Account, SavingAccount
from util.Transaction import Transaction


class AccountTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.header = ["Index","Account","Type","Balance"]
        self.columncount = 4
        self.datat = []

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

    def reload(self):
        try:
            self.beginResetModel()
            strdata = []
            index = 0
            accts = application.bank.fetchAllAccounts()

            for acct in accts:
                typestr = "Account"
                if type(acct) == SavingAccount:
                    typestr = "Savings Account"
                strdata.append([index, acct.account_name, typestr, f'{acct.account_balance:.2f}'])
                index += 1

            print(strdata)
            self.datat = strdata
            self.endResetModel()
        except Exception as e:
            print(e)

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


    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.DB_LOADED = False
        self.model:AccountTableModel = None
        self.selectedAccount:Account = None

        # Button Setup
        self.vD_Table.clicked.connect(self.tableClick)

        self.vP_b_accountDeposit.clicked.connect(self.acctpress0)
        self.vP_b_accountSetBal.clicked.connect(self.acctpress1)
        self.vP_b_accountWithdraw.clicked.connect(self.acctpress2)
        self.vP_b_retrieveAccountHistory.clicked.connect(self.acctpress3)
        self.vP_b_updateAccountInfo.clicked.connect(self.acctpress4)
        self.vP_b_updateAccountInfo.hide()          # Done due to lack of time. Too big of a feature to implement.
        self.vP_b_closeAccount.clicked.connect(self.acctpress5)

        self.commitchanges.clicked.connect(self.pushChangesToDB())

        # Menu Buttons
        self.mb_c_connectionoptions.triggered.connect(self.openConnectionOptions)
        self.mb_a_open.triggered.connect(self.openNewAccount)
        self.mf_b_newdbfile.triggered.connect(self.mf_newdbfile)
        self.actionSync_with_connection.triggered.connect(self.attemptDBFetch)




    """
    This function opens the New Account window.
    """
    def openNewAccount(self):
        if (self.DB_LOADED):
            dialog = AcctEdit_New()
            dialog.exec()
            self.reloadData()
        else:
            logic_misc.infoDialog("No database loaded. Try New -> Database or add a new connection to get started.")

    """
    This handles the button to open the Connection Manager window. After close it should automatically
    fetch all data from the database unless an absense of a selected connection.
    """
    def openConnectionOptions(self):
        try:
            dialog = ConnMgr()

            dialog.exec()
            self.attemptDBFetch()
        except Exception as e:
            print(e)

    def addActiontoHistory(self, action):
        self.vS_History.addItem(action)


    """
    Handles when an account in the table is selected.
    """
    def tableClick(self, index: QModelIndex):
        row = index.row()
        self.vD_Table.selectRow(row)
        acct = application.bank.fetchAccount(self.model.datat[row][1])
        if (self.selectedAccount is None):
            self.selectedAccount = acct
        self.updatePropertiesPanel()

    """
    Handles all the buttons in the "Properties" sidebar. 
    I wanted to make it all in one function but was unsure how to tie it to the buttons.
    ID list:
    0 / 1 / 2 - All correspond to a new transaction window
    3 - Opens list of all transactions on account
    4 - Opens the account editor
    5 - Closes account
    """
    def acctpress0(self):
        self.selAccountAction(0)

    def acctpress1(self):
        self.selAccountAction(1)

    def acctpress2(self):
        self.selAccountAction(2)

    def acctpress3(self):
        self.selAccountAction(3)

    def acctpress4(self):
        self.selAccountAction(4)

    def acctpress5(self):
        self.selAccountAction(5)

    def selAccountAction(self, buttonid):
        if (self.selectedAccount is None):
            logic_misc.infoDialog("No account selected. Select or create an account.\nTo load a database, Try New -> Database or add and select a new connection.")
            return
        accttype = "Account"
        if (type(self.selectedAccount) == SavingAccount):
            accttype = "Savings Account"

        if buttonid == 0:
            dialog = BalEdit(self.selectedAccount.account_name, accttype, 1)
            dialog.exec()
            self.reloadData()
        if buttonid == 1:
            dialog = BalEdit(self.selectedAccount.account_name, accttype, 0)
            dialog.exec()
            self.reloadData()
        if buttonid == 2:
            dialog = BalEdit(self.selectedAccount.account_name, accttype, -1)
            dialog.exec()
            self.reloadData()
        if (buttonid == 3):
            dialog = TransHistory(self.selectedAccount)
            dialog.exec()
            self.reloadData()
        if (buttonid == 4):
            dialog = AcctEdit(self.selectedAccount)
            dialog.exec()
            self.reloadData()

        if (buttonid == 5):
            confirmation = logic_misc.confirmDialog(f"Erase account {self.selectedAccount.account_name} and all associated transactions?")
            if (confirmation == True):
                application.bank.closeAccount(self.selectedAccount.account_name)
                self.reloadData()



    """
    Updates the "Properties" sidebar with information about the selected account.
    """
    def updatePropertiesPanel(self):
        if (self.selectedAccount is None):
            return
        else:
            self.vP_AccountNameBox.setText(self.selectedAccount.account_name)
            totalbal = application.bank.fetchSumBalanceFromAccount(self.selectedAccount.account_name)
            self.vP_AccountBalanceBox.setText(f'{totalbal:.2f}')
            stype = "Account"
            if type(self.selectedAccount) == SavingAccount:
                stype = "Savings Account"
            self.vP_AccountTypeBox.setText(stype)


    """
    Handles logic for the New Menu's Create Blank Database File.
    Creates a new .db file, adds it as a connection, and sets it as the active connection.
    """
    def mf_newdbfile(self):
        try:
            reqpath = QFileDialog.getSaveFileName(self, 'Create File', './', '*.db')
            reqpath = reqpath[0] # According to qt.io documentation it is returned at a tuple of the name and filter. This extracts the name.

            tryconnect = application.createConnectEmptyDB(reqpath)
            if (tryconnect == False):
                logic_misc.infoDialog("Operation Cancelled.")
            else:
                if (type(tryconnect) == SqLiteConnection):
                    application.createConnection(tryconnect)
                    application.selectConnection(application.findConnection(tryconnect))
                    self.attemptDBFetch()
                else:
                    print("Something went wrong");
        except Exception as e:
            print(e)

    def attemptDBFetch(self):
        if application.ActiveConnectionIndex is None:
            return False
        else:
            self.fetchFromDatabase()
            return True

    def fetchFromDatabase(self):
        try:
            self.vD_DatabaseTitle.setText("Fetching data from [" + application.getConnection(application.ActiveConnectionIndex).__str__() + "]...")
            self.vS_ProgressBar.setValue(50)
            application.getSelConnection().test()
            data = application.ConnectionFetchAll()
            self.vS_ProgressBar.setValue(100)

            self.vD_DatabaseTitle.setText("Loading Objects...")

            acctlist = data[0]
            translist = data[1]

            for acct in acctlist:
                application.bank.openAccount(acct)
            for transact in translist:
                application.bank.loadTransaction(transact)

            self.DB_LOADED = True
            self.reloadData()

        except Exception as e:
            self.vD_DatabaseTitle.setText("Failed to Connect to Database [" + application.getSelConnection().__str__() + "]. Check Connection Settings.")
            print(e)

    def reloadData(self):
        try:
            self.vD_DatabaseTitle.setText("Reloading...")
            self.vS_ProgressBar.setValue(100)
            if self.model is None:
                self.model = AccountTableModel()
                self.vD_Table.setModel(self.model)
            self.model.reload()
            self.vS_ProgressBar.setValue(0)
            self.vD_DatabaseTitle.setText("Connected to Database. Standing By.")
        except Exception as e:
            print("ReloadData - " + e.__str__())


    """
    This writes all changes to the database, and uses the UI's progressbar too.
    """
    def pushChangesToDB(self):
        print("Committing Changes...")
        conn = application.getSelConnection()
        changes = application.floatingChanges
        changecount = len(changes)

        self.vS_ProgressBar.setValue(0)
        self.vD_DatabaseTitle.setText("Writing Changes...")
        self.addActiontoHistory("Writing All Changes...")

        conn.openConnection()
        for change in changes:
            self.vS_ProgressBar.valueChanged(self.vS_ProgressBar.value() + 100/changecount)
            str = change.getSQLString()
            print(f"Executing Change: {change.__str__()}")
            try:
                resp = conn.unsafe(str)
            except Exception as e:
                print(e)
                logic_misc.infoDialog("Error committing change: " + change.__str__())\

        self.vS_ProgressBar.setValue(100)
        self.vD_DatabaseTitle.setText("Database up to date.")

