# Transaction.py
# Authors a record of a change to an account.
# aspectious.dev

import datetime
from util.Accounts import Account

class Transaction:
    def __init__(self, account:Account, date:datetime.datetime, type:int, amount:int):
        self.account = account
        self.date = date
        self.type = type
        self.amount = amount

    def getAccount(self):
        return self.account

    def getDate(self):
        return self.date

    def getType(self):
        return self.type

    def getAmount(self):
        return self.amount

    def __str__(self):
        if (type == 1):
            return "Transaction for " + self.account.account_name + " on (" + self.date.__str__() + ") --  Deposit  -- "  + str(self.amount)
        if type == 0:
            return "Transaction for " + self.account.account_name + " on (" + self.date.__str__() + ") --   Other   -- "  + str(self.amount)
        if type == -1:
            return "Transaction for " + self.account.account_name + " on (" + self.date.__str__() + ") -- Withdrawl -- "  + str(self.amount)

