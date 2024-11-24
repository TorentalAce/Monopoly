import random
from Controllers import Basic_Player_Controller

"""
Current simplifications:
	- No chance/cc cards
	- Mortgaging just sells the property rather than actual mortgage
		- (Cant buy back either)
	- Bankruptcy just gives everything back to the bank
	- Unlimited houses/hotels (no bank limit)
	- Cant sell houses (and no check on houses before selling property)

Current Player-Controlled Decisions:
	- Stay in jail or pay to leave
	- Buying a property
	- Mortgaging (both forced and voluntary)
	- Auctions
	- Trading

Known Errors:
	- Auction sometimes gives an error where the player who triggered the auction
	is not in the players list
	- Bankruptcy sometimes tries to remove a player not in the player list
"""

#--Player Functions (defined here to change controllers easily)--
def jail_decision(player):
	#True if leaving, false if rolling
	return Basic_Player_Controller.jail_decision(player)

def buy_decision(player, property=None, group=None):
	#Returns nothing
	Basic_Player_Controller.buy_decision(player, property, group)

def mortgage_decision(player, deficit, forced=False):
	#Returns True if player is bankrupt
	if Basic_Player_Controller.mortgage_decision(player, deficit, forced):
		player_bankruptcy(player)

def auction_decision(player, property, bid):
	#Returns the bid the player is making, just returns the inputed bid if no bid is made
	return Basic_Player_Controller.auction_decision(i, property, bid)

#This one will end up having two decisions within it on the controller-side,
#one for who to trade with and the other for what to trade
def trading_decision(player):
	Basic_Player_Controller.trading_decision(player)

#-----------CLASS DEFINITIONS------------

class grouping:
	def __init__(self, name="", properties=[], house_cost=0):
		self.name = name
		self.properties = []
		self.all_owned = False 
		self.house_cost = house_cost
		#This will need to be updated (or checked) whenever a property is bought/sold/traded
		#Bought is handled in buying_handler, sold is handled in player.sell, trading not yet implemented

	def owned_check(self, player):
		for prop in self.properties:
			if prop.owned_by != player:
				self.all_owned = False
				return
		self.all_owned = True

#General class for each property
class property:
	def __init__(self, name="", buy_cost=0, rent_cost=0, group=None, housing=[]):
		self.name = name
		self.buy_cost = buy_cost
		self.rent_cost = rent_cost
		self.owned_by = None
		self.mortgaged = False
		self.group = group
		self.houses = 0
		self.housing = housing
		if group:
			group.properties.append(self)

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
		property.group.all_owned = False

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
	brown = grouping(name="Brown", house_cost=50)
	light_blue = grouping(name="Light Blue", house_cost=50)
	pink = grouping(name="Pink", house_cost=100)
	orange = grouping(name="Orange", house_cost=100)
	red = grouping(name="Red", house_cost=150)
	yellow = grouping(name="Yellow", house_cost=150)
	green = grouping(name="Green", house_cost=200)
	blue = grouping(name="Blue", house_cost=200)
	railroad = grouping(name="Railroad")
	utility = grouping(name="Utility")
	match position:
		case 0:
			return property(name="Go")
		case 1:
			return property(name="Mediteranean Avenue", buy_cost=60, rent_cost=2, group=brown, housing=[10, 30, 90, 160, 250])
		case 3:
			return property(name="Baltic Avenue", buy_cost=60, rent_cost=4, group=brown, housing=[20, 60, 180, 320, 450])
		case 4:
			return property(name="Income Tax")
		case 5:
			return property(name="Reading Railroad", buy_cost=200, rent_cost=25, group=railroad)
		case 6:
			return property(name="Oriental Avenue", buy_cost=100, rent_cost=6, group=light_blue, housing=[30, 90, 270, 400, 550])
		case 8:
			return property(name="Vermont Avenue", buy_cost=100, rent_cost=6, group=light_blue, housing=[30, 90, 270, 400, 550])
		case 9:
			return property(name="Conneticut Avenue", buy_cost=120, rent_cost=8, group=light_blue, housing=[40, 100, 300, 450, 600])
		case 10:
			return property(name="Jail")
		case 11:
			return property(name="St. Charles Place", buy_cost=140, rent_cost=10, group=pink, housing=[50, 150, 450, 625, 750])
		case 12:
			return property(name="Electric Company", buy_cost=150, group=utility)
		case 13:
			return property(name="States Avenue", buy_cost=200, rent_cost=10, group=pink, housing=[50, 150, 450, 625, 750])
		case 14:
			return property(name="Virginia Avenue", buy_cost=160, rent_cost=12, group=pink, housing=[60, 180, 500, 700, 900])
		case 15:
			return property(name="Pennsylvania Railroad", buy_cost=200, rent_cost=25, group=railroad)
		case 16:
			return property(name="St. James Place", buy_cost=180, rent_cost=14, group=orange, housing=[70, 200, 550, 700, 950])
		case 18:
			return property(name="Tennessee Avenue", buy_cost=180, rent_cost=14, group=orange, housing=[70, 200, 550, 700, 950])
		case 19:
			return property(name="New York Avenue", buy_cost=180, rent_cost=16, group=orange, housing=[80, 220, 600, 800, 1000])
		case 21:
			return property(name="Kentucky Avenue", buy_cost=220, rent_cost=18, group=red, housing=[90, 250, 700, 875, 1050])
		case 23:
			return property(name="Indiana Avenue", buy_cost=220, rent_cost=18, group=red, housing=[90, 250, 700, 875, 1050])
		case 24:
			return property(name="Illinois Avenue", buy_cost=240, rent_cost=20, group=red, housing=[100, 300, 750, 925, 1100])
		case 25:
			return property(name="B. & O. Railroad", buy_cost=200, rent_cost=25, group=railroad)
		case 26:
			return property(name="Atlantic Avenue", buy_cost=260, rent_cost=22, group=yellow, housing=[110, 330, 800, 975, 1150])
		case 27:
			return property(name="Ventnor Avenue", buy_cost=260, rent_cost=22, group=yellow, housing=[110, 330, 800, 975, 1150])
		case 28:
			return property(name="Water Works", buy_cost=150, group=utility)
		case 29:
			return property(name="Marvin Gardens", buy_cost=280, rent_cost=24, group=yellow, housing=[120, 360, 850, 1025, 1200])
		case 30:
			return property(name="Go To Jail")
		case 31:
			return property(name="Pacific Avenue", buy_cost=300, rent_cost=26, group=green, housing=[130, 390, 900, 1100, 1275])
		case 32:
			return property(name="North Carolina Avenue", buy_cost=300, rent_cost=26, group=green, housing=[130, 390, 900, 1100, 1275])
		case 34:
			return property(name="Pennsylvania Avenue", buy_cost=320, rent_cost=28, group=green, housing=[150, 450, 1000, 1200, 1400])
		case 35:
			return property(name="Short Line", buy_cost=200, rent_cost=25, group=railroad)
		case 37:
			return property(name="Park Place", buy_cost=350, rent_cost=35, group=blue, housing=[175, 500, 1100, 1300, 1500])
		case 38:
			return property(name="Luxary Tax")
		case 39:
			return property(name="Boardwalk", buy_cost=400, rent_cost=50, group=blue, housing=[200, 600, 1400, 1700, 2000])
		#Default case used as placeholder for free parking, chance, & cc
		case _:
			return property(name="Empty Square")

#Returns the filled board state as an array
def initialize_game():
	player_names = ["Bob", "Tom", "Jerry", "Alice", "Tony", "Sam"]

	for i in range(0, 40):
		board.append(initialize_square(i))

	init_rolls = []
	for name in player_names:
		init_rolls.append((roll()[0], name))

	#Sort the player order by initial rolls
	final_order = sorted(init_rolls, key=lambda x: x[0], reverse=True)

	for name in final_order:
		players.append(player(name=name[1]))

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
				mortgage_decision(player, 200 - player.money, True)
		case "Go To Jail":
			player.goToJail()
			doubles = False
		case "Luxary Tax":
			if player.money > 100:
				player.money -= 100
			else:
				mortgage_decision(player, 100 - player.money, True)
		case x if x in ("Empty Square", "Jail"):
			pass
		case _: #This one is all the properties basically
			if not square.owned_by:
				if player.money > square.buy_cost:
					buy_decision(player=player, property=square)
				else:
					auction_trigger(player, square)
			elif square.owned_by != player:
				if square.group.name == "Utility":
					if square.group.all_owned:
						rent_cost = (roll()[0]) * 10
					else:
						rent_cost = (roll()[0]) * 4
				elif square.group.name == "Railroad":
					rr_owned = 0
					for i in square.group.properties:
						if i.owned_by == square.owned_by:
							rr_owned += 1
					rent_cost = 25 * (2**(rr_owned-1))
				else:
					if square.group.all_owned:
						if square.houses == 0:
							rent_cost = square.rent_cost*2
						else:
							rent_cost = square.housing[square.houses-1]
					else:
						rent_cost = square.rent_cost

				if player.money > rent_cost:
					player.money -= rent_cost
					square.owned_by.money += rent_cost
				else:
					mortgage_decision(player, rent_cost - player.money, True)

	#At this point decisions can be made about buying houses, selling properties/bldgs, and trading
	mortgage_decision(player, -1)

	trading_decision(player)

	for i in player.properties:
		if i.group.all_owned:
			buy_decision(player=player, group=i.group)

	if doubles:
		turn(player, board, doubles_num+1)

#If a player goes bankrupt (probably will handle going bankrupt to another person here)
def player_bankruptcy(player):
	player.bankrupted()
	try :
		players.remove(player)
	except: #Sometimes this excepts when it triggers remove twice, can just ignore it
		pass

#Trigger for an auction
def auction_trigger(player, property):
	players_in = players.copy()
	start = players_in.index(player)
	players_in = players_in[start:] + players_in[:start]
	bid = 10
	while True:
		for i in players_in:
			prev_bid = bid
			bid = auction_decision(i, property, bid)
			if bid == prev_bid:
				players_in.remove(i)
		if len(players_in) == 1:
			#The last player in buys here
			buying_handler(player, property, bid)
			break

#Handles buying a property (for both normal buying and auctions)
#Also checks to see if the player now owns the entire group
def buying_handler(player, property, cost, house_buy=False):
	if house_buy:
		player.money -= cost
		property.houses += 1
	else:
		player.money -= cost
		player.properties.append(property)
		property.owned_by = player
		property.group.owned_check(player)

#Helper function since have to buy houses evenly
def even_buy_check(group):
	lowest_houses = 5
	properties_available = []
	
	for property in group.properties:
		if property.houses < 5:
			if property.houses < lowest_houses:
				lowest_houses = property.houses
				properties_available = [property]
			elif property.houses == lowest_houses:
				properties_available.append(property)

	return properties_available

def jail_handler(player):
	if jail_decision(player):
		player.money -= 50
		player.leaveJail()
	else:
		if roll()[1]:
			player.leaveJail()
		elif player.turns_in_jail == 2:
			mortgage_decision(player, 50 - player.money)
			player.leaveJail()
		else: 
			player.turns_in_jail += 1

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
	board = []
	players = []
	initialize_game()
	turns = 0
	rounds = 0

	#Runs until the end of the game gets triggered
	while True:
		rounds += 1
		#Goes through the player order for turns
		for i in players:
			turns += 1
			turn(i, board)
		if len(players) <= 1:
			print(f"The winner is: {players[0].name}")
			print(f"This game took: {turns} turns over {rounds} rounds")
			break