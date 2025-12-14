import csv
import datetime

from util.Accounts import Account, SavingAccount
from util.Transaction import Transaction

"""
This Fetches all account data from a CSV and imports it under the right Account class.
Looks for AccountName, AccountType, and Balance as the header text.
See Test Datasets / Demo_AccountList.csv for a demo.
"""
def parseAccountsFromCSV(file:str) -> list[Account]:
    accounts:list[Account] = []

    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile) # Dictionaries are cool
        for row in reader:
            print(row)
            if row['AccountType'] == "SAVINGS":
                svga = SavingAccount(row['AccountName'])
                svga.set_balance(float(row['Balance']))
                accounts.append(svga)
            elif row['AccountType'] == "DEFAULT":
                acct = Account(row['AccountName'])
                acct.set_balance(float(row['Balance']))
                accounts.append(acct)
            else:
                raise Exception("Unknown account type")

    return accounts

"""
Does the same as its twin function, but for a .csv of Transactions.
See Test Datasets / Demo_TransactionList for a demo.
"""
def parseTransactionsFromCSV(file:str) -> list[Transaction]:
    tr:list[Transaction] = []

    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                dt = datetime.datetime.strptime(row['Date'], '%Y-%m-%d %H:%M:%S')
                tt = 0
                if (row['TransactionType'] == "Deposit"):
                    tt = 1
                elif (row['TransactionType'] == "Withdraw"):
                    tt = -1
                Transaction(row['AccountName'], dt, tt, float(row['Amount']))
            except:
                raise Exception("Invalid Date")

    return tr