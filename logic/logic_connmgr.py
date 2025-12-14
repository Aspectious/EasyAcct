from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt, QAbstractListModel, QModelIndex
from PyQt6.QtWidgets import QDialog

from gui.gui_connmgr import Ui_ConnMgr
from logic.logic_newconn import NewConn
import logic.logic_misc as logic_misc

from main import application as application

class ConnItemListModel(QAbstractListModel):
    def __init__(self, initialdata=None, parent=None):
        super().__init__(parent)
        if initialdata is None:
            initialdata = []
        self.items:list[str] = initialdata
        self.activeconnIndex = None


    def rowCount(self, parent=None) -> int:
        return len(self.items)

    def resetData(self, newData: list[str], activeIndex=None):
        self.beginResetModel()
        self.activeconnIndex = activeIndex
        self.items = newData
        self.endResetModel()


    def data(self, index, role=None):
        if (role == Qt.ItemDataRole.DisplayRole):
            if self.activeconnIndex == index.row():
                return f"[ACTIVE] {self.items[index.row()]}"
            return self.items[index.row()]
        return None








class ConnMgr(QDialog, Ui_ConnMgr):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.model = None
        self.selecteditem = None

        # Bind Buttons
        self.b_New.clicked.connect(self.newConnection)
        self.connList.clicked.connect(self.selectItem)
        self.b_Select.clicked.connect(self.setConnActive)
        self.b_Edit.clicked.connect(self.editConnection)


        # Execute LAST
        self.updateConnList()




    def updateConnList(self):
        try:
            list = application.listConnections()
            if (len(list) > 0):
                connectionstrs = []
                for connection in list:
                    connectionstrs.append(connection.__str__())
                if (self.model == None):
                    self.model = ConnItemListModel()
                    self.connList.setModel(self.model)

                if application.ActiveConnectionIndex == None:
                    self.model.resetData(connectionstrs)
                else:
                    self.model.resetData(connectionstrs, application.ActiveConnectionIndex)


        except Exception as e:
            print(e)



    def selectItem(self, index: QModelIndex):
            self.selecteditem = index.row()

    def setConnActive(self):
        if (self.selecteditem is not None):
            print(application.selectConnection(self.selecteditem))
            self.updateConnList()
        else:
            logic_misc.infoDialog("No connection selected.")

    def newConnection(self):
        dialog = NewConn()
        dialog.exec()
        self.updateConnList()

    def editConnection(self):
        if (self.selecteditem is not None):
            dialog = NewConn(application.getConnection(self.selecteditem))
            dialog.exec()
            self.updateConnList()
        else:
            logic_misc.infoDialog("No connection selected.")


    def deleteConnection(self):
        if (self.selecteditem is not None):
            conf = logic_misc.confirmDialog("Delete Selected Connection?")
            if conf == True:
                application.deleteConnection(self.selecteditem)
                self.updateConnList()
            else:
                self.updateConnList()
        else:
            logic_misc.infoDialog("No connection selected.")