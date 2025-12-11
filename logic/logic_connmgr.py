from PyQt5.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QDialog

from gui.gui_connmgr import Ui_ConnMgr
from logic.logic_newconn import NewConn

from main import application as application

class ConnMgr(QDialog, Ui_ConnMgr):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)


        # Bind Buttons
        self.b_New.clicked.connect(self.newConnection)



        # Execute LAST
        self.updateConnList()




    def updateConnList(self):
        list = application.listConnections()
        if (len(list) > 0):
            self.connList.clear()
            for conn in application.listConnections():
                self.connList.addItem(conn.__str__())


    def fetchSelectedItem(self):
        QModelIndex = self.connList.currentIndex()
        return QModelIndex.row()


    def newConnection(self):
        dialog = NewConn()
        dialog.exec()
        self.updateConnList()

    def editConnection(self):
        dialog = NewConn(application.getConnection(self.fetchSelectedItem()))
        dialog.exec()
        self.updateConnList()

    def deleteConnection(self):
        conf = QMessageBox.question(self, 'Confirm', "Delete this Connection?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if (conf == QMessageBox.StandardButton.Yes):
            application.deleteConnection(self.fetchSelectedItem())
            self.updateConnList()
        else:
            self.updateConnList()