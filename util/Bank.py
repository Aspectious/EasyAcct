# bank.py
# A class written to wrap account and transactional data instead of parsing directly from sql
# aspectious.dev
from operator import truediv

from util.Accounts import Account
from util.Transaction import Transaction

class Bank:
    def __init__(self, name:str="Bank"):
        """
        Creates a bank with no accounts or transactions.
        :param name:
        """
        self.__accounts = []
        self.__transactions = []


    def openAccount(self, account:Account):
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
        return True

    def closeAccount(self, name:str):
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

    def writeTransaction(self, ts:Transaction):
        self.__transactions.append(ts)


    def fetchAccount(self, searchString:str):
        for acct in self.__accounts:
            if acct.account_name == searchString:
                return acct
        return False

    def fetchAllAccounts(self):
        return self.__accounts


    def fetchAllTransactionsFromAccount(self, accountName:str):
        transactions = []
        for (transaction) in self.__transactions:
            if transaction.account_name == accountName:

                transactions.append(transaction)
        return transactions
