"""
Application.py

This module handles all internal logic of the application, including managing
the "floating" Bank, Database Connections, and File Utilities, all outside any
GUI logic script. This is to divide out the work, and to clean up the GUI Logic to
handle actions only to the GUI.

The program's instance of the Application class is retreivable as a static variable
in the main.py script.
"""
import os.path
import os
from datetime import datetime as datetime

from util.Accounts import Account, SavingAccount
from util.Bank import Bank as Bank
from util.Transaction import Transaction
from util.Connection import Connection as Connection, SqLiteConnection, ConnectionState

import logic.logic_misc as logic_misc

from util.FC import *






class Application:
    def __init__(self):
        self.bank:Bank = Bank(self)
        self.ConnectionList:list[Connection] = []
        self.ActiveConnectionIndex = None






    """
    Connection Logic
    """

    """
    Adds a new Connection to the list. Allows for switching the source
    of the data.
    :param connection:Connection
    """
    def createConnection(self, connection:Connection) -> None:
        self.ConnectionList.append(connection)


    """
    Attempts to remove a connection from the list of connections.
    :param index:Int
    :returns True | False
    """
    def deleteConnection(self, index) -> bool:
        if index > 0:
            if index <= len(self.ConnectionList)-1:
                self.ConnectionList.pop(index)
                return True
        return False

    """
    Retrieves the index of a connection in the connection list.
    :returns None | index:int
    :argument connection:Connection
    """
    def findConnection(self, connection:Connection) -> int | None:
        for i in range(self.ConnectionList.__len__()):
            if self.ConnectionList[i] == connection:
                return i
        return None


    """
        Returns the Connection object at a specific index.
    """
    def getConnection(self, index:int) -> None | Connection:
        if index >= 0:
            if index <= len(self.ConnectionList)-1:
                return self.ConnectionList[index]
        return None

    """
    Returns a list of all registered connections.
    
    """
    def listConnections(self) -> list[Connection]:
        return self.ConnectionList


    """
    Sets the connection at a specific index to be the connection used for a database.
    """
    def selectConnection(self, index:int) -> bool:
        if index >= 0:
            if index <= len(self.ConnectionList)-1:
                self.ActiveConnectionIndex = index
                return True
        return False

    """
    Combines the implementation of getConnection and self.ActiveConnectionIndex.
    Raises an exception if there is no connection selected.
    """
    def getSelConnection(self) -> None | Connection:
        if self.ActiveConnectionIndex is None:
            raise Exception('No active connection')
        else:
            return self.getConnection(self.ActiveConnectionIndex)



    """
    Data Handling Section
    """


    """
    Checks if there is a file at the path and if not, creates a new sqlite file.
    According to python documentation it implicitly creates the file if it does not exist.
    """
    def createConnectEmptyDB(self, path):
        if (os.path.exists(path)):
            confirm = logic_misc.confirmDialog("Overwrite existing file with blank database?")
            if (confirm == False):
                return False
            else:
                os.remove(path)

        newconn:SqLiteConnection = SqLiteConnection(path, "PrimaryAccounts", "PrimaryAccounts.Transactions")
        try:

            newconn.test()
            newconn.openConnection()
            newconn.createTablesFromBlank()
            newconn.closeConnection()
        except Exception as e:
            print("Failed to open connection")
            print(e)

        if (os.path.exists(path)):
            return newconn

        return False

    """
    This operation is performed on a connection when the main program performs a fetchall of the current connection.
    Designed to not catch the exception possible in getSelConnection, so that it may be checked in GUI logic.
    
    Returns a tuple containing two lists, one of accounts and one of transactions.
    """
    def ConnectionFetchAll(self) -> tuple[list[Account], list[Transaction]]:
        conn = self.getSelConnection()

        try:
            if conn.state == ConnectionState.DISCONNECTED:
                conn.openConnection()

            if conn.state == ConnectionState.CONNECTED:
                try:
                    acctlist = conn.fetchAllAccounts()
                    translist = conn.fetchAllTransactions()
                except Exception as e:
                    print("Error fetching data from database.")
                    print(e)
                    return ([],[])

                data: tuple[list[Account], list[Transaction]] = ([],[])
                for acct in acctlist:
                    name = acct[1]
                    type = acct[2]
                    startingbal = acct[3]

                    if (type == 1):
                        pacct = SavingAccount(name)
                        pacct.set_balance(startingbal)
                        data[0].append(pacct)
                    else:
                        pacct = Account(name, startingbal)
                        data[0].append(pacct)

                for transaction in translist:
                    rawdate = transaction[1]
                    acctname = transaction[2]
                    type = transaction[3]
                    amount = transaction[4]

                    try:
                        parsedate = datetime.strptime(rawdate, "%Y-%m-%d %H:%M:%S.%f")
                    except:
                        parsedate = datetime.strptime(rawdate, "%Y-%m-%d %H:%M:%S")

                    tr = Transaction(acctname, parsedate, type, amount)
                    data[1].append(tr)
                    # According to documentation and how SQL handles timestamps, I need the %f for milliseconds.
                    # I try to parse both though, so if one fails the other continues.


                return data

            return [],[]

        except Exception as e:
            print("e")
            raise e


    """
    Super inefficient last-minute change. I had difficulty syncing changes across the database so
    I decided to write changes immediately.
    """
    def writeChange(self, fc:FloatingChange):
        conn = self.getSelConnection()
        names = conn.getTableNames()
        if (conn.state != ConnectionState.CONNECTED):
            conn.openConnection()
        str = fc.getSQLString(names[0],names[1])
        conn.unsafe(str)


    def flagFloatingChange(self, fc:FloatingChange):
        self.floatingChanges.append(fc)
        print("Floating Change flagged.")

    def fetchChanges(self):
        return self.floatingChanges