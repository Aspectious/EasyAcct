from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QLineEdit, QDialogButtonBox, QFileDialog

from gui.gui_newconn import Ui_NewConn
import logic.logic_misc as logic_misc
from main import application
from util.Connection import Connection, SqLiteConnection, MySQLConnection

import util.Connection as connmgr


class NewConn(QtWidgets.QDialog, Ui_NewConn):
    def __init__(self, existingConn:Connection=None):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.fileselButton.hide()


        # Connections
        self.conn_b_showpassword.clicked.connect(self.togglePasswordVisibility)
        self.b_testConn.clicked.connect(self.testConnection)
        self.buttonBox.clicked.connect(self.closebox)
        self.rb_ConnLocal.clicked.connect(self.updateOptionsFromRadio)
        self.rb_ConnRemote.clicked.connect(self.updateOptionsFromRadio)
        self.fileselButton.clicked.connect(self.selFile)


        # Edit menu setup
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

        # MySQL disabled in this version.
        logic_misc.infoDialog("Notice: MySQL Implementation is incomplete. This version uses SQLite Only.")

        self.updateOptionsFromRadio()
        self.rb_ConnRemote.setEnabled(False)


    def selFile(self):
        path = QFileDialog.getOpenFileName(self, 'Open File', "./", '*.db')
        if (path != None):
            self.conn_addr.setText(path[0])
    """
    Updates the options on the form depending on which mode the connection to be established is selected.
    """
    def updateOptionsFromRadio(self):
        if (self.rb_ConnLocal.isChecked()):
            self.conn_uname.setEnabled(False)
            self.conn_pass.setEnabled(False)
            self.conn_schema.setEnabled(False)
            self.conn_b_showpassword.setEnabled(False)

            self.fileselButton.setEnabled(True)
            self.fileselButton.show()
            self.conn_port.hide()
            self.conn_portLabel.setText("File...")
            self.label_connaddr.setText("File Path")
            self.conn_addr.setText("")

        elif (self.rb_ConnRemote.isChecked()):
            self.conn_uname.setEnabled(True)
            self.conn_pass.setEnabled(True)
            self.conn_schema.setEnabled(True)
            self.conn_b_showpassword.setEnabled(True)
            self.fileselButton.setEnabled(False)
            self.fileselButton.hide()
            self.conn_port.show()
            self.label_connaddr.setText("Address")
            self.conn_portLabel.setText("Port")
            self.conn_addr.setText("localhost")


    def closebox(self, button:QDialogButtonBox.StandardButton):
        if (button == QDialogButtonBox.StandardButton.Save):
            self.accept()
        else:
            self.reject()


    def accept(self):
        host = self.conn_addr.text()
        port = int(self.conn_port.text())
        db = self.conn_schema.text()
        tb1 = self.conn_t_accts.text()
        tb2 = self.conn_t_trans.text()
        uname = self.conn_uname.text()
        passwd = self.conn_pass.text()

        conn:Connection = None
        if (self.rb_ConnLocal.isChecked()):
            conn = SqLiteConnection(host, tb1, tb2)
            application.createConnection(conn)
        else:
            conn = MySQLConnection(host, port, uname, passwd, db, tb1, tb2)
            application.createConnection(conn)

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
