import random
from Controllers import Basic_Player_Controller

"""
Current simplifications:
	- No chance/cc cards
	- No house/hotel building
	- Mortgage is only calculated by getting/purchasing for 1/2 of cost
	- No auctions
	- No boosted rent cost for sets (including railroads & utilities)
	- Mortgaging just sells the property rather than actual mortgage
	- Bankruptcy just gives everything back to the bank

Current Player-Controlled Decisions:
	- Stay in jail or pay to leave
	- Buying a property
	- What to do to avoid bankruptcy (mortgaging)
"""

#--Player Functions(will import from player controller)--
def jail_decision(player):
	if Basic_Player_Controller.jail_decision(player):
		player_bankruptcy(player)

def buy_decision(player, property):
	Basic_Player_Controller.buy_decision(player, property)

def mortgage_decision(player, deficit):
	if Basic_Player_Controller.mortgage_decision(player, deficit):
		player_bankruptcy(player)

#-----------CLASS DEFINITIONS------------

#General class for each property
class property:
	def __init__(self, name="", buy_cost=0, rent_cost=0):
		self.name = name
		self.buy_cost = buy_cost
		self.rent_cost = rent_cost
		self.owned_by = None
		self.mortgaged = False

	def __str__(self):
		return f"Name: {self.name}, Cost: {self.buy_cost}, Rent: {self.rent_cost}, Owned by: {self.owned_by}"

#General player class, position is defined 0 - 39 (0 being go, 39 being boardwalk)
class player:
	def __init__(self, name=""):
		self.name = name
		self.position = 0
		self.properties = []
		self.money = 1500
		self.in_jail = False
		self.turns_in_jail = 0
		self.bankrupt = False

	def __str__(self):
		property_print = list(map(lambda x: x.name, self.properties))
		return f"Name: {self.name}, Owned properties: {property_print}, Money: {self.money}, In jail?: {self.in_jail}"

	def goToJail(self):
		self.position = 10
		self.in_jail = True
		self.turns_in_jail = 0

	def leaveJail(self):
		self.in_jail = False
		self.turns_in_jail = 0

	def sell(self, property):
		self.properties.remove(property)
		self.money += property.buy_cost/2
		property.owned_by = None

	def bankrupted(self):
		#There shouldnt be properties left over on basic controller,
		#But just in case
		for i in self.properties:
			self.sell(i)
		self.money = 0
		self.bankrupt = True

#------------GAME FUNCTIONS---------------

#Returns the proper property info for each board position
def initialize_square(position):
	match position:
		case 0:
			return property(name="Go")
		case 1:
			return property(name="Mediteranean Avenue", buy_cost=60, rent_cost=2)
		case 3:
			return property(name="Baltic Avenue", buy_cost=60, rent_cost=4)
		case 4:
			return property(name="Income Tax")
		case 5:
			return property(name="Reading Railroad", buy_cost=200, rent_cost=25)
		case 6:
			return property(name="Oriental Avenue", buy_cost=100, rent_cost=6)
		case 8:
			return property(name="Vermont Avenue", buy_cost=100, rent_cost=6)
		case 9:
			return property(name="Conneticut Avenue", buy_cost=120, rent_cost=8)
		case 10:
			return property(name="Jail")
		case 11:
			return property(name="St. Charles Place", buy_cost=140, rent_cost=10)
		case 12:
			return property(name="Electric Company", buy_cost=150)
		case 13:
			return property(name="States Avenue", buy_cost=200, rent_cost=10)
		case 14:
			return property(name="Virginia Avenue", buy_cost=160, rent_cost=12)
		case 15:
			return property(name="Pennsylvania Railroad", buy_cost=200, rent_cost=25)
		case 16:
			return property(name="St. James Place", buy_cost=180, rent_cost=14)
		case 18:
			return property(name="Tennessee Avenue", buy_cost=180, rent_cost=14)
		case 19:
			return property(name="New York Avenue", buy_cost=180, rent_cost=16)
		case 21:
			return property(name="Kentucky Avenue", buy_cost=220, rent_cost=18)
		case 23:
			return property(name="Indiana Avenue", buy_cost=220, rent_cost=18)
		case 24:
			return property(name="Illinois Avenue", buy_cost=240, rent_cost=20)
		case 25:
			return property(name="B. & O. Railroad", buy_cost=200, rent_cost=25)
		case 26:
			return property(name="Atlantic Avenue", buy_cost=260, rent_cost=22)
		case 27:
			return property(name="Ventnor Avenue", buy_cost=260, rent_cost=22)
		case 28:
			return property(name="Water Works", buy_cost=150)
		case 29:
			return property(name="Marvin Gardens", buy_cost=280, rent_cost=24)
		case 30:
			return property(name="Go To Jail")
		case 31:
			return property(name="Pacific Avenue", buy_cost=300, rent_cost=26)
		case 32:
			return property(name="North Carolina Avenue", buy_cost=300, rent_cost=26)
		case 34:
			return property(name="Pennsylvania Avenue", buy_cost=320, rent_cost=28)
		case 35:
			return property(name="Short Line", buy_cost=200, rent_cost=25)
		case 37:
			return property(name="Park Place", buy_cost=350, rent_cost=35)
		case 38:
			return property(name="Luxary Tax")
		case 39:
			return property(name="Boardwalk", buy_cost=400, rent_cost=50)
		#Default case used as placeholder for free parking, chance, & cc
		case _:
			return property(name="Empty Square")

#Returns the filled board state as an array
def initialize_game():
	board_state = []
	p = []
	player_names = ["Bob", "Tom", "Jerry", "Alice", "Tony", "Sam"]

	for i in range(0, 40):
		board_state.append(initialize_square(i))

	init_rolls = []
	for name in player_names:
		init_rolls.append((roll()[0], name))

	#Sort the player order by initial rolls
	final_order = sorted(init_rolls, key=lambda x: x[0], reverse=True)

	for name in final_order:
		p.append(player(name=name[1]))

	return board_state, p

#Rolls for a player, returns a tuple of the roll amount and if a double was rolled
def roll():
	dice1  = random.randint(1, 6)
	dice2  = random.randint(1, 6)

	return (dice1 + dice2, True) if dice1 == dice2 else (dice1 + dice2, False)

#Controls a single turn for the player (calls itself again if doubles are rolled)
def turn(player, board, doubles_num=0):
	#Check if the player is in jail and see what action is taken
	if player.in_jail:
		jail_decision(player)

	movement, doubles = roll()
	if doubles_num == 2 and doubles: #If 3 doubles were rolled in a row
		player.goToJail()
		doubles = False
	else:
		player.position += movement
		if player.position >= 40:
			player.position -= 40

	#Check what square was landed on and take appropriate action
	square = board[player.position]

	match square.name:
		case "Go":
			player.money += 200
		case "Income Tax":
			if player.money > 200:
				player.money -= 200
			else:
				mortgage_decision(player, 200 - player.money)
		case "Go To Jail":
			player.goToJail()
			doubles = False
		case "Luxary Tax":
			if player.money > 100:
				player.money -= 100
			else:
				mortgage_decision(player, 100 - player.money)
		case x if x in ("Empty Square", "Jail"):
			pass
		case _: #This one is all the properties basically
			if not square.owned_by:
				if player.money > square.buy_cost:
					buy_decision(player, square)
				else:
					pass #This is where the auction would happen
			else:
				#TODO: Should have a check for a complete set
				if square.name in ("Electric Company", "Water Works"):
					rent_cost = (roll()[0]) * 4
				else:
					rent_cost = square.rent_cost

				if player.money > rent_cost:
					player.money -= rent_cost
					square.owned_by.money += rent_cost
				else:
					mortgage_decision(player, rent_cost - player.money)

	if doubles:
		turn(player, board, doubles_num+1)

#If a player goes bankrupt (probably will handle going bankrupt to another person here)
def player_bankruptcy(player):
	player.bankrupted()
	try :
		players.remove(player)
	except: #Sometimes this excepts when it triggers remove twice, can just ignore it
		pass

#------------DEBUG FUNCTIONS---------------
#Shows current board state
def print_board():
	for i in board:
		print(str(i))

#Shows current player state
def print_players():
	for i in players:
		print(str(i))

#Shows all unowned properties
def print_bank(board):
	bank = []

	for i in board:
		if not i.owned_by:
			bank.append(str(i))

	return bank

#----------Praying things work-------------
if __name__ == "__main__":
	global board, players
	board, players = initialize_game()

	#Runs until end_game gets triggered
	while (True):
		#Goes through the player order for turns
		for i in players:
			turn(i, board)
		if len(players) <= 1:
			print("The winner is: " + str(players[0]))
			break