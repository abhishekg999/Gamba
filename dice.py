import random

class Dice():
	def __init__(self, sides=6, top=1):
		self.sides = sides	
		self.faces = [x for x in range(1, self.sides + 1)]

		if top not in faces:
			assert ValueError("{} sided dice".format(self.sides))

		self.top = top
		self.bottom	= self.getBottom()



	def __add__(self, other):
		return self.top + other.top

	def __mul__(self, other):
		return self.top * other.top



	def __lt__(self, other):
		return self.top < other.top

	def __le__(self, other):
		return self.top <= other.top

	def __eq__(self, other):
		return self.top == other.top

	def __ne__(self, other):
		return self.top != other.top

	def __gt__(self, other):
		return self.top > other.top

	def __ge__(self, other):
		return self.top >= other.top



	def __str__(self):
		return str(self.__repr__())

	def __repr__(self):
		return "Dice({},{})".format(self.sides, self.top)		

	def roll(self):
		self.top = random.choice(self.faces)
		self.bottom = self.getBottom()

	def getBottom(self):
		return 7 - self.top




