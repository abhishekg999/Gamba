from datetime import datetime


class Player:
    def __init__(self, identifier, bal=0):
        self.id = identifier
        self.balance = bal

        ## passive_income = [(value, rate), (value, rate)]
        self.passive_income = [(1, 1)]
        self.modifiers = [(1, 1)]

        self.time = datetime.now()

    def getBalance(self):
        return self.balance

    def setBalance(self, n):
        self.balance = n

    def deposit(self, n):
        if n >= 0:
            self.balance += n
            return self.balance

        assert ValueError("Can only deposit positive value")

    def withdraw(self, n):
        if n <= self.balance:
            self.balance -= n
            return self.balance

        assert ValueError("Not enough money")
        # return None

    def passive(self, time):
        self.delta_time = time - self.time
        for income_source in self.passive_income:
            self.deposit(
                income_source[0]
                * income_source[1]
                * self.delta_time.microseconds
                / 100000
            )

        self.time = time
