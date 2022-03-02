import random
import math
import os
import sys
import random  
from datetime import datetime

import PySimpleGUI as sg
from player import Player

class Game():
    def __init__ (self):
        self.player = Player(1)
        sg.theme('Dark Blue 3')

        self.layout = [[sg.Text('Balance: '), sg.Text(size=(6,1), key='-bal-')],
          [sg.Input(key='-bet-')],
          [sg.Button('CoinFlip')]]


    def run(self):
        window = sg.Window('Gamba', self.layout)
        while True:

            event, values = window.read(timeout=100)
            #print(event, values)

            if event == sg.WIN_CLOSED:
                break

            if event == 'CoinFlip':
                if self.validBet(values['-bet-']):
                    bet = self.parseBet(values['-bet-'])
                    delta = self.gamble(self.coinflip("heads"), bet)

            window['-bal-'].update(int(self.player.getBalance()))
            self.player.passive(datetime.now())

            #print(self.player.getBalance())



    def validBet(self, n):
        if n.isdigit() and self.parseBet(n) <= self.player.getBalance():
            return True 
        return False

    def parseBet(self, bet):
        return int(bet)


    def coinflip(self, value):
        flip = random.choice(["heads", "tails"])
        if value == flip:
            return 2
        return 0

    def gamble(self, payout, bet):
        self.player.withdraw(bet)
        pay = bet * payout 
        self.player.deposit(pay)

        return pay - bet


if __name__ == '__main__':
    g = Game()
    g.run()