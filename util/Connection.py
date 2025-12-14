import sys
import time
from contextlib import nullcontext
from enum import Enum
from errno import errorcode

import mysql.connector
import sqlite3

from util.Accounts import Account


# I made an Enum because it was so damn hard to keep track of how I
# formatted strings to determine the state of a database connection
class ConnectionState(Enum):
    UNKNOWN = 0         # Defines a connection that has yet to be tested or connected
    CONNECTING = 1      # Defines a connection partway between Connected and Disconnected
    CONNECTED = 2       # Defines a connected, ready connection.
    DISCONNECTED = 3    # Defines a disconnected, unavailable yet previously used connection.
    ERROR = 4           # Defines a connection that has errored out and should be reconnected with caution.



"""
This is how I've handled connections to database sources.
The base class defines a skeleton, similar to header files in c and cpp,
where the children implement the database calls in different ways.

Sadly, at the time of submission, the MySQL connection is broken, and so only
the SQLite connection is running well.

I have attempted to add effective placeholders, but because each connector implements placeholders differently
it has been a headache to run consistently. As a result most queries are insecure and possibly subject to
SQL Injection attacks. This is simply to function for the final.
"""
class Connection():
    def __init__(self, type, accttable, transtable):
        self.type = type
        self.accttable = accttable
        self.transtable = transtable
        self.state = ConnectionState.UNKNOWN

    def __str__(self) -> str:
        return "Unknown Connection"

    """
    Defines an extra set of information specifically for remote queries to MySQL or Mariadb.
    While implemented in MySQLConnector, it needs to be here for the abstract "Connector" class.
    """
    def setMySqlData(self,host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    """
    Private Implementation to run a SQL Query. Was insecure.
    Legacy Code, still in use.
    """
    def __executeSingle(self, statement) -> list[any]:
        pass
    """
    Private implementation to run a multiple SQL Queries. 
    Legacy Code.
    """
    def __executeMany(self, statement, data)  -> list[any]:
        pass
    """
    Attempts to open the connection and mark the state as ConnectionState.CONNECTED.
    """
    def openConnection(self) -> int:
        pass
    """
    Closes the connection and marks the "state" as ConnectionState.Disconnected.
    """
    def closeConnection(self) -> int:
        pass
    """
    performs a select * from Accounts.
    """
    def fetchAllAccounts(self) -> list[any]:
        pass
    """
    Fetches a Select * from Transactions.
    """
    def fetchAllTransactions(self) -> list[any]:
        pass
    """
    Performs a Select * From Transaction Where AccountName
    """
    def fetchTransactionsFromAccount(self, account:Account) -> list[any]:
        pass
    """
    Tests the connection, usually with a simple SELECT 1;
    """
    def test(self) -> list[any]:
        pass
    """
    Runs an unsafe SQL command.
    """
    def unsafe(self, query) -> list[any]:
        pass
    """
    Gets names of the two Database Tables.
    Helpful most with writing changes to the database.
    """
    def getTableNames(self) -> tuple[str,str]:
        return (self.accttable, self.transtable)


"""
Defines a SqLite3 Connection.
Works the best so far.
Implements methods in Connection.
"""
class SqLiteConnection(Connection):
    def __init__(self, filelocation, accttable, transtable):
        Connection.__init__(self, 0, accttable, transtable)
        self.__connection = None
        self.database = filelocation

    def __str__(self) -> str:
        return f"Local: {self.database}"

    def openConnection(self) -> int:
        self.state = ConnectionState.CONNECTING
        try:
            self.__connection = sqlite3.connect(self.database)
            self.state = ConnectionState.CONNECTED
            return 0
        except:
            self.state = ConnectionState.ERROR
            return 1

    def closeConnection(self) -> int:
        self.state = ConnectionState.CONNECTING
        try:
            self.__connection.close()
            self.state = ConnectionState.DISCONNECTED
        except Exception as err:
            self.state = ConnectionState.ERROR
            print(err)

    def __executeSingleUnsafe(self, statement) -> list[any]:
        self.__cur = self.__connection.cursor()
        result = self.__cur.execute(statement)
        self.__connection.commit()
        result = result.fetchall()
        self.__cur.close()
        return result;

    def __executeSinglePlaceholder(self, statement:str, data) -> list[any]:
        print(self.state)
        self.__cur = self.__connection.cursor()
        result = self.__cur.execute(statement, data)
        self.__connection.commit()
        result = result.fetchall()
        self.__cur.close()
        return result


    def createTablesFromBlank(self):
        # Need to create tables and relations. Default table names are "PrimaryAccounts" and "PrimaryAccounts.Transactions".
        self.__executeSingleUnsafe("CREATE TABLE PrimaryAccounts ('Index' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, AccountName TEXT UNIQUE, AccountType INTEGER, Balance FLOAT);")
        self.__executeSingleUnsafe("CREATE TABLE 'PrimaryAccounts.Transactions' ('Index' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, Date DATETIME, AccountName TEXT, TransactionType INTEGER, Delta FLOAT);")


    def test(self) -> list[any]:
        self.openConnection()
        test1 = self.__executeSingleUnsafe("SELECT 1;")
        self.closeConnection()
        return test1

    def fetchAllAccounts(self) -> list[any]:
        query = self.__executeSingleUnsafe(f"SELECT * FROM \"{self.accttable}\"")
        return query

    def fetchAllTransactions(self) -> list[any]:
        query = self.__executeSingleUnsafe(f"SELECT * FROM \"{self.transtable}\"")
        return query

    def fetchTransactionsFromAccount(self, account:Account) -> list[any]:
        query = self.__executeSinglePlaceholder("SELECT * FROM " + self.transtable + " WHERE AccountName=?;", account.account_name)
        return query

    """
    The easiest way without spending several days devising a better solution.
    """
    def unsafe(self, query:str):
        query = self.__executeSingleUnsafe(query)
        return query


"""
Defines a MySQL Connection.
Currently broken legacy code, however should be able to work with enough extra time.
Implements methods in Connection.
"""
class MySQLConnection(Connection):
    def __init__(self, host:str, port:int, user:str, password:str, database:str, accttable:str, transtable:str):
        super().__init__(1, accttable, transtable)
        super().setMySqlData(host, port, user, password, database)

    def __str__(self):
        return f"Remote: {self.user} @ mysql://{self.host}:{self.port}/{self.database}"
    def openConnection(self):
        if (self.state == ConnectionState.CONNECTED):
            return
        attempt = 1
        while attempt < 4:
            self.state = ConnectionState.CONNECTING
            try:
                self.__connection = mysql.connector.connect(user=self.user, password=self.password,
                                                            database=self.database, host=self.host, connection_timeout=5)
                self.state = ConnectionState.CONNECTED
                return 0
            except mysql.connector.Error as err:
                self.state = ConnectionState.ERROR
                if err == mysql.connector.DatabaseError:
                    return 1
                elif err.errno == 1045: # Access Denied error
                    return 2
                elif err.errno == 2003: # Invalid or Unknown Host / Can't Connect
                    return 3
            except Exception as err:
                self.state = ConnectionState.ERROR
                return -1
            time.sleep(500 ** attempt)
            attempt += 1
        self.state = ConnectionState.ERROR
        return 4

    def closeConnection(self):
        self.state = ConnectionState.CONNECTING
        try:
            self.__connection.close()
            self.state = ConnectionState.DISCONNECTED
        except Exception as err:
            self.state = ConnectionState.ERROR
            print(err)


    def __executeSelectSingle(self, statement):
        self.__cur = self.__connection.cursor()
        self.__cur.execute(statement)
        rows = self.__cur.fetchall()
        self.__cur.close()
        return rows
    def __executeSelectMany(self, statement, data):
        self.__cur = self.__connection.cursor()
        self.__cur.execute(statement, data)
        result = self.__cur.fetchall()
        self.__cur.close()
        return result

    def __executeInsertSingle(self, statement):
        self.__cur = self.__connection.cursor()
        self.__cur.execute(statement)
        self.__connection.commit()
        self.__cur.close()

    def __executeInsertMany(self, statement, data):
        statement.replace("?","%s")
        self.__cur = self.__connection.cursor()
        self.__cur.execute(statement, data)
        self.__connection.commit()
        self.__cur.close()

    def test(self):
        self.openConnection()
        try:
            test1 = self.__executeSelectSingle("SELECT 1;")
            if test1 == [(1,)]:
                return 1
            else:
                return 0
        except Exception as err:
            print(err)
            return 0

    def fetchAllAccounts(self):
        query = self.__executeSelectSingle("SELECT * FROM " + self.accttable)
        return query

    def fetchAllTransactions(self):
        query = self.__executeSelectSingle("SELECT * FROM " + self.transtable)
        return query

    def fetchTransactionsFromAccount(self, account:Account):
        query = self.__executeSelectMany("SELECT * FROM %s WHERE AccountName=%s;", (self.transtable, account.account_name))
        return query