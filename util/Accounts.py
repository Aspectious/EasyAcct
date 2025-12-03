class Account:
    def __init__(self, name, balance=0):
        self.account_name = name;
        self.account_balance = balance;
        if (balance < 0):
            self.set_balance(0);


    def deposit(self, amount):
        if (amount > 0):
            self.account_balance += amount;
            return True;
        else:
            return False;

    def set_balance(self, value):
        if (value < 0):
            self.account_balance = 0;
        else:
            self.account_balance = value;


    def withdraw(self, amount):
        if (amount <= 0):
            return False;
        elif (amount > self.account_balance):
            return False;
        else:
            self.account_balance -= amount;
            return True;


    def get_balance(self):
        return self.account_balance;

    def get_name(self):
        return self.account_name;

    def __str__(self):
        text = f"Account name = {self.get_name()}, Account balance = {self.get_balance():.2f}";
        return text;


class SavingAccount(Account):
    MINIMUM = 100;
    RATE = 0.02;

    def __init__(self, name):
        super().__init__(name, SavingAccount.MINIMUM)
        self.deposit_count = 0;


    def apply_interest(self):
        if (self.deposit_count > 0):
            if (self.deposit_count % 5 == 0):
                self.set_balance(self.account_balance * (1 + SavingAccount.RATE));


    def deposit(self, amount):
        result = super().deposit(amount);
        if (result == True):
            self.deposit_count += 1;
            self.apply_interest();
        return result;

    def withdraw(self, amount):
        if (self.get_balance() - amount < SavingAccount.MINIMUM):
            return False;
        else:
            return super().withdraw(amount);

    def set_balance(self, value):
        if (value < SavingAccount.MINIMUM):
            self.set_balance(SavingAccount.MINIMUM);
        else:
            super().set_balance(value);

    def __str__(self):
        return f"SAVING ACCOUNT: {super().__str__()}"
