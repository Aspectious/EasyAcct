# Transaction.py
# Authors a record of a change to an account.
# aspectious.dev

import datetime
from util.Accounts import Account

class Transaction:
    def __init__(self, account:str, date:datetime.datetime, type:int, amount:float):
        self.account = account
        self.date = date
        self.type = type
        self.amount = amount

    def getName(self):
        return self.account

    def getDate(self):
        return self.date

    def getType(self):
        return self.type

    def getAmount(self):
        return self.amount

    def __str__(self):
        if (type == 1):
            return "Transaction for " + self.account + " on (" + self.date.isoformat() + ") --  Deposit  -- "  + str(self.amount)
        if type == -1:
            return "Transaction for " + self.account + " on (" + self.date.isoformat() + ") -- Withdrawl -- "  + str(self.amount)
        return "Transaction for " + self.account + " on (" + self.date.isoformat() + ") --   Other   -- " + str(
                self.amount)

