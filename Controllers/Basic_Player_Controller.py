import monopoly_sim as ms

"""
The basic controller will make very bare-bones decisions.

Jail - Always pay to leave (unless you would need to mortgage)
Buying - Always purchase a property if able
Mortgage - Sell the least valuable properties first
Auction - Bet the max bet up to the property's original price, then leave
"""

#Returns True if player is bankrupt
def jail_decision(player):
	if player.money > 50:
		player.money -= 50
		player.leaveJail()
	else:
		if ms.roll()[1]:
			player.leaveJail()
		elif player.turns_in_jail == 2:
			if mortgage_decision(player, 50 - player.money):
				return True
			player.leaveJail()
		else: 
			player.turns_in_jail += 1
	return False


def buy_decision(player, property):
	if player.money > property.buy_cost:
		player.money -= property.buy_cost
		player.properties.append(property)
		property.owned_by = player
	else:
		auction_decision(player, property, 10) #This won't trigger but just in case

#Helper function for mortgage
def find_cheapest(properties):
	cheapest_property = None
	for i in properties:
		if not cheapest_property:
			cheapest_property = i
		else:
			if i.buy_cost < cheapest_property.buy_cost:
				i = cheapest_property
	return cheapest_property

#Returns True if player is bankrupt
def mortgage_decision(player, deficit):
	if len(player.properties) == 0:
		return True
	elif deficit < 0:
		return False
	else:
		player.sell(find_cheapest(player.properties))
		if player.money <= deficit:
			mortgage_decision(player, deficit)
		else:
			return False

#Returns the og if the player is backing out, bets are made in intervals of 1, 10, or 100
def auction_decision(player, property, bid):
	if bid >= property.buy_cost:
		return bid
	elif bid + 10 > property.buy_cost and bid + 1 < player.money:
		bid += 1
	elif bid + 100 > property.buy_cost and bid + 10 < player.money:
		bid += 10
	elif bid + 100 < player.money:
		bid += 100
	return bid