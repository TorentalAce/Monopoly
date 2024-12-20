import random, signal
import pandas as pd
from Controllers import Basic_Player_Controller as Basic

#-----------PLAYER FUNCTIONS-----------
def jail_decision(player):
	#True if leaving, false if rolling
	return Basic.jail_decision(player, player.gooj_card)

def buy_decision(player, property=None):
	if Basic.buy_decision(player, property):
		buying_handler(player, property, property.buy_cost, lazyCheck = True)
	else:
		auction_trigger(player, property)

def house_buy_decision(player):
	props = []
	for property in player.properties:
		if property.group.all_owned and property.group.house_cost < player.money and property.houses < 5:
			if (property.houses == 4 and house_bank["hotels"] != 0) or (property.houses < 4 and house_bank["houses"] != 0):
				if property.group not in props: props.append(property.group)
	
	final_props = []

	for group in props:
		if group.name not in ("Utility", "Railroad"):
			final_props += even_buy_check(group) #After this, should have every property the person can buy on

	if len(final_props) == 0: return

	while True:
		#Gives the buy decision, breaks if none is returned
		prop_to_buy = Basic.house_buy_decision(player, final_props)
		if not prop_to_buy: break
		buying_handler(player, prop_to_buy, prop_to_buy.group.house_cost, True)

		#Removes the property and checks if the group is fully gone, if it is reinsert 
		#if the props still meet conditions (covers if the last property 
		#buys the set of houses it needed)
		final_props.remove(prop_to_buy)
		check = True
		for i in final_props:
			if i.group == prop_to_buy.group: check = False
		if check: final_props += even_buy_check(prop_to_buy.group)

		temp = final_props.copy()
		#Now removes anything from the remaining array that the player can no longer afford
		for i in final_props:
			if i.group.house_cost >= player.money or (i.houses == 4 and house_bank["hotels"] == 0) or (i.houses < 4 and house_bank["houses"] == 0):
				temp.remove(i)

		final_props = temp.copy()
		#If the array is empty here, break
		if len(final_props) == 0: break

def unmortgage_decision(player, properties=[], transfer=False):
	#This will be the case for the optional, properties will be filled if this is
	#called from trading or bankruptcy
	prop_check = player.properties if len(properties) == 0 else properties
	cost = 5/10 if transfer else 6/10
	unmortgaged_props = []
	for prop in prop_check:
		if prop.mortgaged and prop.buy_cost*cost < player.money: unmortgaged_props.append(prop)
	if len(unmortgaged_props) == 0: return

	to_unmortgage = Basic.unmortgage_decision(unmortgaged_props)
	if to_unmortgage: player.unmortgage(to_unmortgage)
	else: return
	unmortgaged_props.remove(to_unmortgage)
	unmortgage_decision(player, unmortgaged_props, transfer)

#This logic basically lets the player mortgage properties that dont have houses on them, 
#and then asks for properties with houses, if all the houses in a group are sold, it
#adds that group to the mortgage list
def mortgage_decision(player, cost):
	available_list = []
	houses_list = []
	for property in player.properties:
		if property.houses == 0 and not property.mortgaged:
			yes = True
			for prop in property.group.properties:
				if prop.houses != 0:
					yes = False
					break
			if yes: available_list.append(property)

	while player.money <= cost:
		to_mortgage = Basic.mortgage_decision(player, cost, available_list)
		if to_mortgage:
			player.sell(to_mortgage)
			available_list.remove(to_mortgage)
		else:
			#This will return a group back if an entire property set sold off its houses
			group_add = house_sell_decision(player, cost)
			if group_add: available_list += group_add.properties

def optional_sell_decision(player):
	while True:
		to_mortgage = Basic.optional_sell_decision(player)
		if to_mortgage: player.sell(to_mortgage)
		else: break

def house_sell_decision(player, cost):
	group_list = []
	for property in player.properties:
		if property.houses > 0 and property.group not in group_list: group_list.append(property.group)

	available_list = []
	for group in group_list:
		high_houses = 0
		temp = []
		for property in group.properties:
			if property.houses > high_houses:
				high_houses = property.houses
				temp = [property]
			elif property.houses == high_houses:
				temp.append(property)
		available_list += temp

	while cost >= player.money and len(available_list) > 0:
		prop_to_sell = Basic.house_sell_decision(player, available_list)
		player.house_sell(prop_to_sell, 1)
		available_list.remove(prop_to_sell)
		group_check = False
		for i in available_list:
			if i.group == prop_to_sell.group:
				group_check = True
				break
		if group_check: continue
		elif prop_to_sell.houses > 0:
			available_list += prop_to_sell.group.properties
		else:
			return prop_to_sell.group

	return None

def auction_decision(player, property, bid):
	#Returns the bid the player is making, just returns the inputed bid if no bid is made
	auction_bid = Basic.auction_decision(player, property, bid)
	return bid if auction_bid <= bid else auction_bid

#This one will end up having two decisions within it on the controller-side,
#one for who to trade with and the other for what to trade
#When implementing this, need to have a check to make sure theres no houses on the property being traded
def trading_decision(player):
	Basic.trading_decision(player)

#-----------CLASS DEFINITIONS------------

class grouping:
	def __init__(self, name="", house_cost=0):
		self.name = name
		self.properties = []
		self.house_cost = house_cost
		self.all_owned = False 
		#Only way this becomes false after being true is if properties are traded seperately

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
		self.total_rent_collected = 0
		self.auction_price = 0
		if group:
			group.properties.append(self)

	def __str__(self):
		return f"Name: {self.name}, Cost: {self.buy_cost}, Rent: {self.rent_cost}, Owned by: {self.owned_by}, Houses: {self.houses}"

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
		self.net_worth = 0
		self.gooj_card = []
		self.total_rent_collected = 0
		self.auction_wins = 0

	def __str__(self):
		property_print = list(map(lambda x: x.name, self.properties))
		return f"Name: {self.name}, Owned properties: {property_print}, Money: {self.money}, In jail?: {self.in_jail}"

	def goToJail(self):
		self.position = 10
		self.in_jail = True
		self.turns_in_jail = 0

	def leaveJail(self, pay=False):
		self.in_jail = False
		self.turns_in_jail = 0
		event_dict(self, board[10], "jail", "leave", 50 if pay else 0, 1, 0)

	def unmortgage(self, property):
		self.money -= property.buy_cost/2 + property.buy_cost * 0.1
		self.net_worth += property.buy_cost/2
		property.mortgaged = False
		event_dict(self, property, "purchase", "unmortgage", property.buy_cost/2 + property.buy_cost * 0.1, 1, property.buy_cost/2)

	def sell(self, property):
		self.money += property.buy_cost/2
		self.net_worth -= property.buy_cost/2
		property.mortgaged = True
		event_dict(self, property, "sale", "mortgage", property.buy_cost/2, 1, -property.buy_cost/2)

	def house_sell(self, property, amount):
		self.net_worth -= amount * property.group.house_cost/2
		self.money += amount * property.group.house_cost/2

		if property.houses == 5: #Hotel check
			house_bank["hotels"] += 1
			property.houses -= 1
			amount -= 1

		house_bank["houses"] += amount
		property.houses -= amount
		event_dict(self, property, "sale", "house" if property.houses != 4 else "hotel", amount * property.group.house_cost/2, amount, -amount * property.group.house_cost/2)

	def bankrupted(self, other=None):
		if other:
			other.money += self.money
			mortgaged_props = []
			for i in self.properties:
				other.properties.append(i)
				i.owned_by = other
				other.net_worth += i.buy_cost / 2
				if i.mortgaged: mortgaged_props.append(i)
			mortgage_transfer_payment(other, mortgaged_props)
			other.gooj_card.append(self.gooj_card)
			unmortgage_decision(other, mortgaged_props, True)
		else:
			for i in self.properties:
				i.owned_by = None
				i.houses = 0
				i.group.all_owned = False
		self.money = 0
		self.net_worth = 0
		self.gooj_card = []
		self.bankrupt = True
		self.properties = []
		players.remove(self)

#------------GAME FUNCTIONS---------------

#Returns the proper property info for each board position
def initialize_square(position, groups):
	match position:
		case 0:
			return property(name="Go")
		case 1:
			return property(name="Mediteranean Avenue", buy_cost=60, rent_cost=2, group=groups["brown"], housing=[10, 30, 90, 160, 250])
		case 2:
			return property(name="Community Chest")
		case 3:
			return property(name="Baltic Avenue", buy_cost=60, rent_cost=4, group=groups["brown"], housing=[20, 60, 180, 320, 450])
		case 4:
			return property(name="Income Tax")
		case 5:
			return property(name="Reading Railroad", buy_cost=200, rent_cost=25, group=groups["railroad"])
		case 6:
			return property(name="Oriental Avenue", buy_cost=100, rent_cost=6, group=groups["light_blue"], housing=[30, 90, 270, 400, 550])
		case 7:
			return property(name="Chance")
		case 8:
			return property(name="Vermont Avenue", buy_cost=100, rent_cost=6, group=groups["light_blue"], housing=[30, 90, 270, 400, 550])
		case 9:
			return property(name="Conneticut Avenue", buy_cost=120, rent_cost=8, group=groups["light_blue"], housing=[40, 100, 300, 450, 600])
		case 10:
			return property(name="Jail")
		case 11:
			return property(name="St. Charles Place", buy_cost=140, rent_cost=10, group=groups["pink"], housing=[50, 150, 450, 625, 750])
		case 12:
			return property(name="Electric Company", buy_cost=150, group=groups["utility"])
		case 13:
			return property(name="States Avenue", buy_cost=140, rent_cost=10, group=groups["pink"], housing=[50, 150, 450, 625, 750])
		case 14:
			return property(name="Virginia Avenue", buy_cost=160, rent_cost=12, group=groups["pink"], housing=[60, 180, 500, 700, 900])
		case 15:
			return property(name="Pennsylvania Railroad", buy_cost=200, rent_cost=25, group=groups["railroad"])
		case 16:
			return property(name="St. James Place", buy_cost=180, rent_cost=14, group=groups["orange"], housing=[70, 200, 550, 700, 950])
		case 17:
			return property(name="Community Chest")
		case 18:
			return property(name="Tennessee Avenue", buy_cost=180, rent_cost=14, group=groups["orange"], housing=[70, 200, 550, 700, 950])
		case 19:
			return property(name="New York Avenue", buy_cost=200, rent_cost=16, group=groups["orange"], housing=[80, 220, 600, 800, 1000])
		case 20:
			return property(name="Free Parking")
		case 21:
			return property(name="Kentucky Avenue", buy_cost=220, rent_cost=18, group=groups["red"], housing=[90, 250, 700, 875, 1050])
		case 22:
			return property(name="Chance")
		case 23:
			return property(name="Indiana Avenue", buy_cost=220, rent_cost=18, group=groups["red"], housing=[90, 250, 700, 875, 1050])
		case 24:
			return property(name="Illinois Avenue", buy_cost=240, rent_cost=20, group=groups["red"], housing=[100, 300, 750, 925, 1100])
		case 25:
			return property(name="B. & O. Railroad", buy_cost=200, rent_cost=25, group=groups["railroad"])
		case 26:
			return property(name="Atlantic Avenue", buy_cost=260, rent_cost=22, group=groups["yellow"], housing=[110, 330, 800, 975, 1150])
		case 27:
			return property(name="Ventnor Avenue", buy_cost=260, rent_cost=22, group=groups["yellow"], housing=[110, 330, 800, 975, 1150])
		case 28:
			return property(name="Water Works", buy_cost=150, group=groups["utility"])
		case 29:
			return property(name="Marvin Gardens", buy_cost=280, rent_cost=24, group=groups["yellow"], housing=[120, 360, 850, 1025, 1200])
		case 30:
			return property(name="Go To Jail")
		case 31:
			return property(name="Pacific Avenue", buy_cost=300, rent_cost=26, group=groups["green"], housing=[130, 390, 900, 1100, 1275])
		case 32:
			return property(name="North Carolina Avenue", buy_cost=300, rent_cost=26, group=groups["green"], housing=[130, 390, 900, 1100, 1275])
		case 33:
			return property(name="Community Chest")
		case 34:
			return property(name="Pennsylvania Avenue", buy_cost=320, rent_cost=28, group=groups["green"], housing=[150, 450, 1000, 1200, 1400])
		case 35:
			return property(name="Short Line", buy_cost=200, rent_cost=25, group=groups["railroad"])
		case 36:
			return property(name="Chance")
		case 37:
			return property(name="Park Place", buy_cost=350, rent_cost=35, group=groups["blue"], housing=[175, 500, 1100, 1300, 1500])
		case 38:
			return property(name="Luxary Tax")
		case 39:
			return property(name="Boardwalk", buy_cost=400, rent_cost=50, group=groups["blue"], housing=[200, 600, 1400, 1700, 2000])

#Returns the filled board state as an array
def initialize_game():
	groups = {
		"brown" : grouping(name="Brown", house_cost=50),
		"light_blue" : grouping(name="Light Blue", house_cost=50),
		"pink" : grouping(name="Pink", house_cost=100),
		"orange" : grouping(name="Orange", house_cost=100),
		"red" : grouping(name="Red", house_cost=150),
		"yellow" : grouping(name="Yellow", house_cost=150),
		"green" : grouping(name="Green", house_cost=200),
		"blue" : grouping(name="Blue", house_cost=200),
		"railroad" : grouping(name="Railroad"),
		"utility" : grouping(name="Utility")
	}

	player_names = ["Bob", "Tom", "Jerry", "Alice", "Tony", "Sam"]

	for i in range(0, 40):
		board.append(initialize_square(i, groups))

	init_rolls = []
	for name in player_names:
		init_rolls.append((roll()[0], name))

	#Sort the player order by initial rolls
	final_order = sorted(init_rolls, key=lambda x: x[0], reverse=True)

	for name in final_order:
		players.append(player(name=name[1]))

	initialize_cards()

#Rolls for a player, returns a tuple of the roll amount and if a double was rolled
def roll():
	dice1  = random.randint(1, 6)
	dice2  = random.randint(1, 6)

	return (dice1 + dice2, True) if dice1 == dice2 else (dice1 + dice2, False)

#Controls a single turn for the player (calls itself again if doubles are rolled)
def turn(player, board, doubles_num=0):
	#Check if the player is in jail and see what action is taken
	if player.in_jail:
		movement, doubles = jail_handler(player)
		player.position += movement
	else:
		movement, doubles = roll()

		if doubles_num == 2 and doubles: #If 3 doubles were rolled in a row
			event_dict(player, board[player.position], "jail", "doubles", 0, 1, 0)
			player.goToJail()
			doubles = False
		else:
			player.position += movement
			if player.position >= 40:
				player.money += 200
				player.position -= 40
				event_dict(player, board[player.position], "gift", "go", 200, 1, 0)

	#Check what square was landed on and take appropriate action
	square = board[player.position]

	match square.name:
		case "Income Tax":
			payment_handler(player, 200, "tax")
		case "Go To Jail":
			event_dict(player, board[player.position], "jail", "go_to_jail", 0, 1, 0)
			player.goToJail()
			doubles = False
		case "Luxary Tax":
			payment_handler(player, 100, "tax")
		case x if x in ("Free Parking", "Jail", "Go"):
			pass
		case x if x in ("Community Chest", "Chance"):
			if card_handler(player, x):
				doubles = False
		case _: #This one is all the properties basically
			if not square.owned_by:
				if player.money > square.buy_cost:
					buy_decision(player=player, property=square)
				else:
					auction_trigger(player, square)
			elif square.owned_by != player:
				if square.mortgaged:
					pass
				elif square.group.name == "Utility":
					if square.group.all_owned:
						rent_cost = (roll()[0]) * 10
					else:
						rent_cost = (roll()[0]) * 4
				elif square.group.name == "Railroad":
					rr_owned = sum(1 for i in square.group.properties if i.owned_by == square.owned_by)
					rent_cost = 25 * (2**(rr_owned-1))
				else:
					if square.group.all_owned:
						if square.houses == 0:
							rent_cost = square.rent_cost*2
						else:
							rent_cost = square.housing[square.houses-1]
					else:
						rent_cost = square.rent_cost

				if not square.mortgaged:
					payment_handler(player, rent_cost, "rent", square.owned_by)

	if not player.bankrupt: #Make sure the player didnt go bankrupt above
		#At this point decisions can be made about buying houses, selling properties/bldgs, and trading
		optional_sell_decision(player) #Always false for now

		trading_decision(player) #Always false for now

		unmortgage_decision(player)

		house_buy_decision(player)

		if doubles:
			turn(player, board, doubles_num+1)

#Trigger for an auction
def auction_trigger(player, property):
	players_in = players.copy()
	start = players_in.index(player)
	players_in = players_in[start:] + players_in[:start]
	bid = 10
	bidding_round = 0
	while len(players_in) > 1:
		bidding_round += 1
		for i in players_in:
			prev_bid = bid
			bid = auction_decision(i, property, bid)
			if bid >= i.money or bid == prev_bid:
				players_in.remove(i)
				bid = prev_bid
			outcome = "Bid" if bid > prev_bid else "Out"
			auction_table.append({
				"Property": property.name,
				"Bidding_Round": bidding_round,
				"Player": i.name,
				"Bid": bid,
				"Player_Balance_After_Bid": i.money - bid if i.money - bid > 0 else 0,
				"Outcome": outcome
			})
	auction_table.append({
		"Property": property.name,
		"Bidding_Round": bidding_round,
		"Player": players_in[0].name,
		"Bid": bid,
		"Player_Balance_After_Bid": players_in[0].money - bid,
		"Outcome": "Won"
	})
	#The last player in buys here
	buying_handler(players_in[0], property, bid, auction=True)
	players_in[0].auction_wins += 1
	property.auction_price = bid
	event_dict(players_in[0], property, "purchase", "auction", bid, 1, property.buy_cost/2)

#Handles buying a property (for both normal buying and auctions)
#Also checks to see if the player now owns the entire group
def buying_handler(player, property, cost, house_buy=False, auction=False, lazyCheck=False):
	if cost < player.money:
		if house_buy:
			key_check = "hotels" if property.houses == 4 else "houses"
			if house_bank[key_check] == 0:
				return False
			else:
				house_bank[key_check] -= 1
			property.houses += 1
			player.net_worth += cost/2
			event_dict(player, property, "purchase", "house" if property.houses != 5 else "hotel", property.group.house_cost, 1, property.group.house_cost/2)
		else:
			player.properties.append(property)
			property.owned_by = player
			property.group.owned_check(player)
			player.net_worth += property.buy_cost/2 #Can't just use cost in case auction was called
			if lazyCheck:
				event_dict(player, property, "purchase", "property", cost, 1, cost/2)
		player.money -= cost
		return True

#Helper function since have to buy houses evenly
def even_buy_check(group):
	lowest_houses = 4
	properties_available = []
	
	for property in group.properties:
		if property.mortgaged:
			return []
		if property.houses < lowest_houses:
			lowest_houses = property.houses
			properties_available = [property]
		elif property.houses == lowest_houses:
			properties_available.append(property)

	return properties_available

#Handles the jail stuff
def jail_handler(player):
	classification = ""
	rounds_elapsed = 0
	end_result = (0, False)
	choice = jail_decision(player)
	if type(choice) == dict:
		player.gooj_card.remove(choice)
		choice["gooj_owned"] = False
		rounds_elapsed = player.turns_in_jail
		player.leaveJail()
		classification = "card"
		end_result = roll()
	elif choice and player.money > 50:
		player.money -= 50
		rounds_elapsed = player.turns_in_jail
		player.leaveJail(True)
		classification = "optional"
		end_result = roll()
	else:
		if roll()[1]:
			rounds_elapsed = player.turns_in_jail
			player.leaveJail()
			classification = "doubles"
			end_result = (roll()[0], False)
		elif player.turns_in_jail == 2:
			payment_handler(player, 50, "jail")
			rounds_elapsed = player.turns_in_jail
			player.leaveJail()
			classification = "forced"
			if not player.bankrupt:
				end_result = roll()
		else:
			rounds_elapsed = player.turns_in_jail
			player.turns_in_jail += 1
			classification = "stay"

	jail_table.append({
		"Round": rounds,
		"Player": player.name,
		"Rounds_Elapsed": rounds_elapsed,
		"Decision": classification
		})

	return end_result

#Handles payments
def payment_handler(player, payment, type, paying=None):
	if player.money + player.net_worth <= payment:
		event_dict(player, board[player.position], "bankrupt", paying.name if paying else "bank", payment, 1, -player.net_worth)
		player.bankrupted(paying)
	else:
		if player.money <= payment:
			mortgage_decision(player, payment)

		event_dict(player, board[player.position], type, paying.name if paying else "bank", payment, 1, 0)
		player.money -= payment
		if paying:
			paying.total_rent_collected += payment
			paying.money += payment
			board[player.position].total_rent_collected += payment

#Initializes the chance and community chest cards
def initialize_cards():
	#Fills the decks
	#Chance has 15 cards
	for i in range(0, 15):
		chance_cards[i] = True

	#Community chest has 17 cards
	for i in range(0, 17):
		cc_cards[i] = True

#If every card in the chance or cc deck is used, reset deck
def shuffle_deck(deck):
	deck["used"] = 0
	for key in deck:
		if key not in ("used", "gooj_owned"):
			if key == 4 and deck["gooj_owned"]:
				deck["used"] = 1
				continue
			deck[key] = True

#Will handle the chance/cc card pulled
def card_handler(player, deck_name):
	deck = cc_cards if deck_name == "Community Chest" else chance_cards

	if deck == cc_cards:
		while True:
			card = random.randint(0, 16)
			if deck[card]: break
	else:
		while True:
			card = random.randint(0, 14)
			if deck[card]: break

	double_end_check = False #If went to jail gotta set this true

	#Cards described by chance / community chest (with 15/16 as exceptions)
	#Cards copied from monopoly.fandom.com/wiki/{Community_Chest / Chance}
	match (card):
		case 0: #Advance to go for both
			player.position = 0
			player.money += 200
			event_dict(player, board[player.position], "gift", "go", 200, 1, 0)

		case 1: #Advance to Illinois Ave. / Collect $200
			if deck == chance_cards:
				if player.position > 24:
					player.money += 200
					event_dict(player, board[player.position], "gift", "go", 200, 1, 0)
				player.position = 24

				square = board[player.position]
				if square.owned_by and square.owned_by != player:
					if square.mortgaged:
						pass
					elif square.group.all_owned:
						if square.houses == 0:
							rent_cost = square.rent_cost*2
						else:
							rent_cost = square.housing[square.houses-1]
					else:
						rent_cost = square.rent_cost

					if not square.mortgaged:
						payment_handler(player, rent_cost, "rent", square.owned_by)
				elif not square.owned_by: #If not owned
					if player.money > square.buy_cost:
						buy_decision(player=player, property=square)
					else:
						auction_trigger(player, square)
			else:
				player.money += 200
				event_dict(player, board[player.position], "gift", "community_chest", 200, 1, 0)

		case 2: #Advance to St. Charles Place / Pay $50
			if deck == chance_cards:
				if player.position > 11:
					player.money += 200
					event_dict(player, board[player.position], "gift", "go", 200, 1, 0)
				player.position = 11

				square = board[player.position]
				if square.owned_by and square.owned_by != player:
					if square.mortgaged:
						pass
					elif square.group.all_owned:
						if square.houses == 0:
							rent_cost = square.rent_cost*2
						else:
							rent_cost = square.housing[square.houses-1]
					else:
						rent_cost = square.rent_cost
					if not square.mortgaged:
						payment_handler(player, rent_cost, "rent", square.owned_by)
				elif not square.owned_by: #If not owned
					if player.money > square.buy_cost:
						buy_decision(player=player, property=square)
					else:
						auction_trigger(player, square)
			else:
				payment_handler(player, 50, "community_chest")

		case 3: #Advance to nearest utility, pay 10x dice roll if owned / Get $50
			if deck == chance_cards:
				if player.position > 28:
					player.money += 200
					event_dict(player, board[player.position], "gift", "go", 200, 1, 0)
					player.position = 12
				elif player.position > 12:
					player.position = 28
				else:
					player.position = 12

				square = board[player.position]
				if square.owned_by and square.owned_by != player and not square.mortgaged:
					rent_cost = roll()[0] * 10
					payment_handler(player, rent_cost, "rent", square.owned_by)
				elif not square.owned_by: #If not owned
					if player.money > square.buy_cost:
						buy_decision(player=player, property=square)
					else:
						auction_trigger(player, square)
			else:
				player.money += 50
				event_dict(player, board[player.position], "gift", "community_chest", 50, 1, 0)

		case 4: #Get out of jail free card
			player.gooj_card.append(deck)
			deck["gooj_owned"] = True

		case 5: #Go to jail
			card_name = "chance" if deck == chance_cards else "community_chest"
			event_dict(player, board[player.position], "jail", card_name, 0, 1, 0)
			player.goToJail()
			double_end_check = True

		case 6: #Advance to the nearest railroad, 2x rent / collect $100
			if deck == chance_cards:
				if player.position > 35:
					player.money += 200
					event_dict(player, board[player.position], "gift", "go", 200, 1, 0)
					player.position = 5
				elif player.position > 5:
					player.position = 15
				elif player.position > 15:
					player.position = 25
				elif player.position > 25:
					player.position = 35
				else:
					player.position = 5

				square = board[player.position]
				if square.owned_by and square.owned_by != player and not square.mortgaged:
					rr_owned = sum(1 for i in square.group.properties if i.owned_by == square.owned_by)
					rent_cost = 25 * (2**(rr_owned-1)) * 2
					payment_handler(player, rent_cost, "rent", square.owned_by)
				elif not square.owned_by: #If not owned
					if player.money > square.buy_cost:
						buy_decision(player=player, property=square)
					else:
						auction_trigger(player, square)
			else:
				player.money += 100
				event_dict(player, board[player.position], "gift", "community_chest", 100, 1, 0)

		case 7: #Get $50 / Collect $50 from each player
			if deck == chance_cards:
				player.money += 50
				event_dict(player, board[player.position], "gift", "chance", 200, 1, 0)
			else:
				for i in players:
					if i != player: 
						payment_handler(i, 50, "community_chest", player)
						player.total_rent_collected -= 50

		case 8: #Go back 3 spaces / Collect $20
			if deck == chance_cards:
				player.position -= 3
				#Theres only 3 spaces the player can be after this, each handled below
				if player.position == 4: #Income tax
					payment_handler(player, 200, "tax")
				elif player.position == 19: #New york ave.
					square = board[player.position]
					if square.owned_by and square.owned_by != player:
						if square.mortgaged:
							pass
						elif square.group.all_owned:
							if square.houses == 0:
								rent_cost = square.rent_cost*2
							else:
								rent_cost = square.housing[square.houses-1]
						else:
							rent_cost = square.rent_cost

						if not square.mortgaged:
							payment_handler(player, rent_cost, "rent", square.owned_by)
					elif not square.owned_by: #If not owned
						if player.money > square.buy_cost:
							buy_decision(player=player, property=square)
						else:
							auction_trigger(player, square)
				else: #CC
					card_handler(player, "Community Chest")
			else:
				player.money += 20
				event_dict(player, board[player.position], "gift", "community_chest", 20, 1, 0)

		case 9: #Repairs (25/100 / 40/115)
			if deck == chance_cards:
				house = 25
				hotel = 100
				card_name = "chance"
			else:
				house = 40
				hotel = 115
				card_name = "community_chest"
			total_cost = sum(house*prop.houses if prop.houses < 5 else hotel for prop in player.properties)
			payment_handler(player, total_cost, card_name)

		case 10: # Go to Reading Railroad / 10 from each player
			if deck == chance_cards:
				player.money += 200
				event_dict(player, board[player.position], "gift", "go", 200, 1, 0)
				player.position = 5
				square = board[player.position]
				if square.owned_by and square.owned_by != player and not square.mortgaged:
					rr_owned = sum(1 for i in square.group.properties if i.owned_by == square.owned_by)
					rent_cost = 25 * (2**(rr_owned-1))
					payment_handler(player, rent_cost, "rent", square.owned_by)
				elif not square.owned_by: #If not owned
					if player.money > square.buy_cost:
						buy_decision(player=player, property=square)
					else:
						auction_trigger(player, square)
			else:
				for i in players:
					if i != player: 
						payment_handler(i, 10, "community_chest", player)
						player.total_rent_collected -= 10

		case 11: #Pay $15 / Collect $100
			if deck == chance_cards:
				payment_handler(player, 15, "chance")
			else:
				player.money += 100
				event_dict(player, board[player.position], "gift", "community_chest", 100, 1, 0)

		case 12: #Advance to boardwalk / Pay $50
			if deck == chance_cards:
				player.position = 39
				square = board[player.position]
				if square.owned_by and square.owned_by != player:
					if square.mortgaged:
						pass
					elif square.group.all_owned:
						if square.houses == 0:
							rent_cost = square.rent_cost*2
						else:
							rent_cost = square.housing[square.houses-1]
					else:
						rent_cost = square.rent_cost

					if not square.mortgaged:
						payment_handler(player, rent_cost, "rent", square.owned_by)
				elif not square.owned_by: #If not owned
					if player.money > square.buy_cost:
						buy_decision(player=player, property=square)
					else:
						auction_trigger(player, square)
			else:
				payment_handler(player, 50, "community_chest")

		case 13: #Pay each player $50 / Pay $50
			if deck == chance_cards:
				for i in players:
					if i != player: 
						payment_handler(player, 50, "chance", i)
						i.total_rent_collected -= 50
					if player.bankrupt:
						break
			else:
				payment_handler(player, 50, "community_chest")

		case 14: #Collect $150 / collect $25
			if deck == chance_cards:
				player.money += 150
				event_dict(player, board[player.position], "gift", "chance", 150, 1, 0)
			else:
				player.money += 25
				event_dict(player, board[player.position], "gift", "community_chest", 25, 1, 0)

		case 15: #Collect $10
			player.money += 10
			event_dict(player, board[player.position], "gift", "community_chest", 10, 1, 0)

		case 16: #Collect $100
			player.money += 100
			event_dict(player, board[player.position], "gift", "community_chest", 100, 1, 0)

	deck[card] = False
	deck["used"] += 1
	#Shuffles deck at the end if all the cards have been used up
	if (deck_name == "Community Chest" and deck["used"] == 17) or (deck_name == "Chance" and deck["used"] == 15):
		shuffle_deck(deck)

	return double_end_check

#Called during bankruptcy or trade for mortgaged properties
def mortgage_transfer_payment(player, properties):
	for prop in properties:
		payment_handler(player, prop.buy_cost*1/10, "unmortgage")

def event_dict(player, property, type, t_type, t_a, t_n, net_worth):
	event_table.append({
		"Round": rounds,
		"Player": player.name,
		"Property": property.name,
		"Action_Type": type,
		"Transaction_Type": t_type,
		"Transaction_Amount": t_a,
		"Transaction_Number": t_n,
		"Net_Worth_Change": net_worth
	})

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
def print_bank():
	bank = []

	for i in board:
		if not i.owned_by:
			bank.append(str(i))

	return bank

#Shows how many houses each property holds
def print_houses():
	for prop in board:
		print(f"Name: {prop.name}, Houses: {prop.houses}")

#Shows the properties and houses for the person
def print_property_info(player):
	for prop in player.properties:
		print(f"Person: {player.name}, Name: {prop.name}, Houses: {prop.houses}, Mortgage Status: {prop.mortgaged}")


def alarmHit(signum, frame):
	print("Timed Out")
	signal.alarm(0)
	exit(0)

#----------PRAYING THINGS WORK-------------
def main(choice, n):
	global board, players, house_bank, chance_cards, cc_cards, rounds
	global event_table, jail_table, player_table, property_table, auction_table #For excel export
	board = []
	players = []
	house_bank = {
		"houses": 32,
		"hotels": 12
	}
	chance_cards = {"used": 0, "gooj_owned": False}
	cc_cards = {"used": 0, "gooj_owned": False}
	jail_table = []
	event_table = []
	player_table = []
	property_table = []
	auction_table = []
	initialize_game()
	rounds = 0

	#Lazy Fix for infinite loop
	signal.signal(signal.SIGALRM, alarmHit)
	signal.alarm(2)

	#Runs until the end of the game gets triggered
	while True:
		rounds += 1
		data_players = {}
		for i in players:
			data_players[i] = (i.money, i.net_worth)

		#Goes through the player order
		for i in players:
			turn(i, board)

		for key in data_players:
			player_table.append({
				"Round": rounds,
				"Player": key.name,
				"Starting_Balance": data_players[key][0],
				"Starting_Net_Worth": data_players[key][1],
				"Ending_Balance": key.money,
				"Ending_Net_Worth": key.net_worth,
				"Total_Worth_Change": (key.money + key.net_worth) - (data_players[key][0] + data_players[key][1]),
				"Properties_Owned": len(key.properties),
				"Properties_Mortgaged": sum(1 for i in key.properties if i.mortgaged),
				"Mortgaged Value": sum(i.rent_cost/2 for i in key.properties if i.mortgaged),
				"Houses_Owned": sum(i.houses for i in key.properties),
				"Total_Rent_Collected": key.total_rent_collected,
				"Trade_Count": 0,
				"Auction_Wins": key.auction_wins
			})

		for prop in board:
			if not prop.group: continue
			if prop.mortgaged: status = "mortgaged"
			elif not prop.group.all_owned: status = "normal"
			elif prop.houses == 0: status = "group owned"
			else: status = f"{prop.houses} houses" if prop.houses != 5 else "hotel"
			property_table.append({
				"Round": rounds,
				"Property": prop.name,
				"Owner": prop.owned_by.name if prop.owned_by else "none",
				"Property_Group": prop.group.name,
				"Status": status,
				"Total_Rent_Collected": prop.total_rent_collected,
				"Auction_Price": prop.auction_price,
				"Buy_Price": prop.buy_cost
			})

		if len(players) <= 1:
			print(f"The winner is: {players[0].name} in {rounds} rounds")
			break
		if rounds == 100:
			for player in players:
				player.net_worth += player.money
				for prop in player.properties:
					player.net_worth += prop.buy_cost/2

			best_networth = None
			tie = []
			for player in players:
				if not best_networth: 
					best_networth = player
					tie = [player]
				elif player.net_worth > best_networth.net_worth:
					best_networth = player
					tie = [player]
				elif player.net_worth == best_networth.net_worth:
					tie.append(player)

			if len(tie) == 1:
				print(f"Round limit reached, {best_networth.name} wins with the highest net worth!")
			else:
				string_to_print = ""
				for player in tie:
					string_to_print += player.name + ", "
				print(f"Round limit reached, there was a tie for the highest net worth between: {string_to_print[:-2]}!")
			break

	if len(players) <= 1:
		event_dict(players[0], board[players[0].position], "game_end", "victory", 0, 1, 0)
	else:
		event_dict(best_networth, board[best_networth.position], "game_end", "tie-victory", 0, 1, 0)

	signal.alarm(0)

	jailDF = pd.DataFrame(jail_table)
	playerDF = pd.DataFrame(player_table)
	propertyDF = pd.DataFrame(property_table)
	auctionDF = pd.DataFrame(auction_table)
	eventDF = pd.DataFrame(event_table)
	if choice == 2 or choice == 3:
		jailDF.insert(0, 'Game_ID', n)
		playerDF.insert(0, 'Game_ID', n)
		propertyDF.insert(0, 'Game_ID', n)
		auctionDF.insert(0, 'Game_ID', n)
		eventDF.insert(0, 'Game_ID', n)

	if choice == 3 and len(players) <= 1:
		return (playerDF, propertyDF, eventDF, auctionDF, jailDF, True)
	elif choice == 3:
		return (playerDF, propertyDF, eventDF, auctionDF, jailDF, False)
	elif choice != 0: return (playerDF, propertyDF, eventDF, auctionDF, jailDF)