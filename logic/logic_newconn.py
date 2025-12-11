from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QLineEdit

from gui.gui_newconn import Ui_NewConn
from util.db.Connection import Connection

import util.db.Connection as connmgr
import logic.logic_main as MainWin

class NewConn(QtWidgets.QDialog, Ui_NewConn):
    def __init__(self, existingConn:Connection=None):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.conn_b_showpassword.clicked.connect(self.togglePasswordVisibility)
        self.b_testConn.clicked.connect(self.testConnection)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self.accept)
        try:
            if (existingConn != None):
                self.conn_addr.setText(existingConn.host)
                self.conn_port.setValue(str(existingConn.port))
                self.conn_uname.setText(existingConn.user)
                self.conn_pass.setText(existingConn.password)
                self.conn_schema.setText(existingConn.database)
                self.conn_t_accts.setText(existingConn.accttable)
                self.conn_t_trans.setText(existingConn.transtable)
        except Exception as e:
            print(e)







    def accept(self):
        host = self.conn_addr.text()
        port = int(self.conn_port.text())
        db = self.conn_schema.text()
        tb1 = self.conn_t_accts.text()
        tb2 = self.conn_t_trans.text()
        uname = self.conn_uname.text()
        passwd = self.conn_pass.text()
        MainWin.MainWindow.setConnection(1, [host, port, uname, passwd, db, tb1, tb2])
        super().accept()

    def reject(self):
        super().reject()

    def togglePasswordVisibility(self):
        if self.conn_pass.echoMode() == QLineEdit.EchoMode.Normal:
            self.conn_pass.setEchoMode(QLineEdit.EchoMode.Password)
        elif self.conn_pass.echoMode() == QLineEdit.EchoMode.Password:
            self.conn_pass.setEchoMode(QLineEdit.EchoMode.Normal)

    def testConnection(self):


        self.testlabel.update()
        host = self.conn_addr.text()
        port = int(self.conn_port.text())
        db = self.conn_schema.text()
        tb1 = self.conn_t_accts.text()
        tb2 = self.conn_t_trans.text()
        uname = self.conn_uname.text()
        passwd = self.conn_pass.text()
        connection = connmgr.MySQLConnection(host, port, uname, passwd, db, tb1, tb2)
        try:
            self.testlabel.setText("Connecting...")
            res = connection.openConnection()
            if (res == 1):
                self.testlabel.setText("Connection resulted in unknown server error.")
                return
            elif (res == 2):
                self.testlabel.setText("Access Denied. Check username or password.")
                return
            elif (res == 3):
                self.testlabel.setText("Connection Failed, Unable to connect to server.")
                return
            elif (res == 4):
                self.testlabel.setText("Connection Failed, Unable to connect to server.")
                return
        except:
            print("Connection failed")


        testres = connection.test()
        if (testres == 1):
            self.testlabel.setText("Connection successful.")
        if (testres == 2):
            self.testlabel.setText("Unable to read from schema.")
        if (testres == 3):
            self.testlabel.setText("Unable to read from accounts table.")
        if (testres == 4):
            self.testlabel.setText("Unable to read from transactions table.")
        connection.closeConnection()
