import random 

class Card():
	d_suits = {
		0 : "Spades",
		1 : "Hearts",
		2 : "Diamonds",
		3 : "Clovers"
	}

	d_values = {
		0 : "Ace",
		1 : "2",
		2 : "3",
		3 : "4",
		4 : "5",
		5 : "6",
		6 : "7",
		7 : "8",
		8 : "9",
		9 : "10",
		10 : "Jack",
		11 : "Queen",
		12 : "King",
	}

	def __init__(self, cv):
		if cv < 0 and cv >= 52:
			raise ValueError()

		self.cv = cv
		self.value = self.d_values[self.cv % 13]
		self.suit = self.d_suits[self.cv // 13]


	def __str__(self):
		return "{} of {}".format(self.value, self.suit)

	def __repr__(self):
		return "Card({})".format(self.cv)

class Deck():
	def __init__(self):
		self.deck = [Card(x) for x in range(52)]
		self.table = []


	def __len__(self):
		return self.deck_length()

	def __str__(self):
		s = ""
		for c in self.deck:
			s += str(c)
			s += "\n"

		return s

	def deck_length(self):
		return len(self.deck)

	def table_length(self):
		return len(self.table)

	def shuffle(self):
		random.shuffle(self.deck)

	def deal(self):
		if len(self) == 0:
			raise IndexError("Deck is empty")

		card = self.deck[0]
		self.table.append(card)
		self.deck.remove(card)

		return card

	def deal_n(self, n):
		if n < len(self):
			raise ValueError()

		ret = [self.deal _ in range(n)]
		\
		return ret

	def collect(self, card=None, c_all=False):
		if c_all:
			self.deck += self.table
			self.table = []
			return True
		else:
			if card is not None:
				
				if card in self.table:
					self.table.remove(card)
					self.deck.append(card)
					return True
				else:
					return False
			else:
				return True



if __name__ == '__main__':
	d = Deck()
	d.shuffle()

	for x in range(51):
		m = d.deal()

	print(d)
	d.collect(m)
	print(d)




