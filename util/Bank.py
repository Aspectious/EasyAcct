# bank.py
# A class written to wrap account and transactional data instead of parsing directly from sql
# aspectious.dev
import math
from datetime import datetime

from util.Accounts import Account, SavingAccount
from util.Transaction import Transaction
from util.FC import *

class Bank:
    def __init__(self, parentApplication):
        """
        Creates a bank with no accounts or transactions.
        :param name:
        """
        self.application = parentApplication
        self.__accounts:list[Account] = []
        self.__transactions:list[Transaction] = []


    def openAccount(self, account:Account) -> bool:
        """
        Defines how accounts should be opened, and
        prevents duplicate accounts in the bank.

        :param account:
        :return:
        """
        for (accountName) in self.__accounts:
            if accountName == account.account_name:
                return False
        self.__accounts.append(account)
        atype=0
        if (type(account) == SavingAccount):
            atype = 1
        ch = FC_NewAccount(account.account_name, atype, account.account_balance)
        self.application.writeChange(ch)
        return True

    def closeAccount(self, name:str) -> bool:
        """
        Closes the account with the given name.

        :param name:
        :return:
        """
        for (accountName) in self.__accounts:
            if accountName == name:
                self.__accounts.remove(accountName)
                return True
        return False

    """
    This is called whenver a database is loaded. Does not apply it to accounts on file.
    """
    def loadTransaction(self, ts:Transaction):
        self.__transactions.append(ts)


    """
    This writes a new transaction to the list, runs checks, and applies the delta to an account on file.
    Also adds changes to the floating queue in "Application" to be sent to the database.
    """
    def writeNewTransaction(self, ts:Transaction) -> bool:
        acctname = ts.getName()
        if self.fetchAccount(acctname) == None:
            raise Exception("Account not found.")

        account = self.fetchAccount(acctname)

        self.loadTransaction(ts) # Applies to list
        ch = FC_NewTransaction(ts.getDate(), ts.getName(), ts.getType(), ts.getAmount())
        self.application.writeChange(ch)


        cinterest = self.checkInterest(acctname) # Checks interest

        # Performs operation on account
        if (ts.type == 1):
            # This ensures that the savings account does not accidentally apply interest
            # by not marking it as a "deposit" at all on the account.
            # If interest were
            # to go out of sync then the sum of transactions would not match the
            # account balance.
            if (type(account) == SavingAccount):
                existingbal = account.get_balance()
                account.set_balance(existingbal + ts.getAmount())
            else:
                account.deposit(ts.getAmount())
        elif (ts.type == -1):
            account.withdraw(ts.getAmount())
        elif (ts.type == 0):
            account.set_balance(ts.getAmount())
        else:
            raise Exception("Unknown transaction type.")

        # Applies interest if applicable
        if cinterest == True:
            svacctinterest = SavingAccount.RATE * account.get_balance()
            interestTransaction = Transaction(acctname, datetime.now(), 0, svacctinterest)

            account.set_balance((1+SavingAccount.RATE) * account.get_balance())
            self.__transactions.append(interestTransaction)
            ch = FC_NewTransaction(interestTransaction.getDate(), interestTransaction.getName(), interestTransaction.getType(), interestTransaction.getAmount())
            self.application.writeChange(ch)

        # Flags Changes to application to sync with database.
        return True





    """
    Fetches the Account object from an account name.
    """
    def fetchAccount(self, searchString:str) -> Account | None:
        for acct in self.__accounts:
            if acct.account_name == searchString:
                return acct
        return None

    """
    Fetches all accounts in the bank.
    """
    def fetchAllAccounts(self) -> list[Account]:
        return self.__accounts

    """
    Calculates the final "total" of an account, based on its sum of transactions.
    """
    def fetchSumBalanceFromAccount(self, accountName:str) -> float:
        translist = self.fetchAllTransactionsFromAccount(accountName)
        acct = self.fetchAccount(accountName)
        total = 0.00
        for transaction in translist:
            if (transaction.type == -1):
                total -= transaction.amount
            else:
                total += transaction.amount
        return total


    """
    This function is called whenever a new transaction is added. 
    It only applies interest to accounts that need it, such as the SavingAccount.
    It does so under a second, new transaction that covers the difference in interest.
    This is to maintain that the sum of transactions matches the account balance on file.
    """
    def checkInterest(self, accountName:str) -> bool:
        account = self.fetchAccount(accountName)
        if (type(account) == SavingAccount):
            tsactions = self.fetchAllTransactionsFromAccount(accountName)
            deptsactions = []

            for tsaction in tsactions:
                if (tsaction.type == 1):
                    deptsactions.append(tsaction)
            depcount = len(deptsactions)

            dointerest = False
            if (depcount % 5 == 0):
                dointerest = True
            return dointerest
        else:
            return False

    """
    Account balances are stored in two places - the sum of transactions and the amount stored in the primary table.
    This ensures that the two are equal, verifying that there has been no corruption betwen the two.
    It also accounts for interest and
    """
    def validateBalanceDiff(self, accountName:str) -> bool:
        sumbal = self.fetchSumBalanceFromAccount(accountName)
        account = self.fetchAccount(accountName)
        accountbal = account.get_balance()

        if type(account) == SavingAccount:
            transactioncount = len(self.fetchAllTransactionsFromAccount(accountName))
            interestcount = math.floor()

        else:
            if (accountbal == sumbal):
                return True
            return False




    """
    Fetches all transactions that match a specific account in the bank.
    """
    def fetchAllTransactionsFromAccount(self, accountName:str) -> list[Transaction]:
        transactions = []
        for (transaction) in self.__transactions:
            if transaction.getName() == accountName:

                transactions.append(transaction)
        return transactions
