"""
Application.py

This module handles all internal logic of the application, including managing
the "floating" Bank, Database Connections, and File Utilities, all outside any
GUI logic script. This is to divide out the work, and to clean up the GUI Logic to
handle actions only to the GUI.

The program's instance of the Application class is retreivable as a static variable
in the main.py script.
"""

from util.Bank import Bank as Bank
from util.db.Connection import Connection as Connection


class Application:
    def __init__(self):
        self.Bank:Bank = Bank()
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
        if index > 0:
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
        if index > 0:
            if index <= len(self.ConnectionList)-1:
                self.ActiveConnectionIndex = index
                return True
        return False







    """
    Data Handling Section
    """

