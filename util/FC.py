"""
These classes are implemented to streamline the different ways that the database can be updated from changes.
Rather than write SQL statements on the fly I prepare them here, to which each change is added to a queue.
Each SQL Statement is insecure but it works best with limited time.

Each class has three methods with as many kwargs as needed:
- __init__
- getSQLString
- __str__

HEAVILY UNFINISHED

Class Structure:
TODO: Clear so just NewAccount and UpdateAccount work for final. Scope too big!


FloatingChange
    |- FC_NewAccount
    |- FC_UpdateAccount
    |- FC_DropAccount
    |- FC_NewTransaction
    |- FC_DropTransaction
"""
from datetime import datetime
from util.Accounts import SavingAccount, Account
from util.Transaction import Transaction


class FloatingChange:
    def __init__(self, **kwargs):
        pass
    def getSQLString(self, tb1:str,tb2:str) -> str:
        pass
    def __str__(self):
        return "Generic Floating Change"
class FC_NewAccount(FloatingChange):
    def __init__(self, acctname:str, acctype:int, balance:float):
        super().__init__()
        self.accountName = acctname
        self.accttype = acctype
        self.bal = balance
    def getSQLString(self, tb1:str,tb2:str) -> str:
        return f"INSERT INTO \"{tb1}\" (AccountName, AccountType, Balance) VALUES (\"{self.accountName}\", {self.accttype}, {self.bal});"
    def __str__(self):
        return f"Create Account: {self.accountName}"
class FC_UpdateAccount(FloatingChange):
    def __init__(self, acctname:str, acctype:int, balance:float, baseName:str):
        super().__init__()
        self.accountName = acctname
        self.accttype = acctype
        self.bal = balance
        self.baseN:str = baseName
    def getSQLString(self, tb1:str,tb2:str) -> str:
        return f"UPDATE \"{tb1}\" SET AccountName = \"{self.accountName}\", AccountType = \"{self.accttype}\", Balance = \"{self.bal}\" WHERE AccountName = \"{self.baseN}\";"
    def __str__(self):
        return f"Update Account: {self.baseN}"
class FC_DropAccount(FloatingChange):
    def __init__(self, acctName:str):
        super().__init__()
        self.accountName = acctName
    def getSQLString(self, tb1:str,tb2:str) -> str:
        return f"DELETE FROM \"{tb1}\" WHERE AccountName = \"{self.accountName}\";"
    def __str__(self):
        return f"Drop Account: {self.accountName}"
class FC_NewTransaction(FloatingChange):
    def __init__(self, dt:datetime, acctName:str, type:int, delta:float):
        super().__init__()
        self.date = dt
        self.acctName = acctName
        self.type = type
        self.delta = delta
    def getSQLString(self, tb1:str,tb2:str) -> str:
        return f"INSERT INTO \"{tb2}\" (Date, AccountName,TransactionType,Delta) VALUES (\"{self.date}\", \"{self.acctName}\", {self.type}, {self.delta}); "
    def __str__(self):
        if (self.type == 1):
            return f"Deposit of {self.delta} for account {self.acctName}"
        elif (self.type == 0):
            return f"Set Balance to {self.delta} for account {self.acctName}"
        elif (self.type == -1):
            return f"Withdraw of {self.delta} for account {self.acctName}"

