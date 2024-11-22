import monopoly_sim as ms

"""
The basic controller will make very bare-bones decisions.

Jail - Always pay to leave (unless you would need to mortgage)
Buying - Always purchase a property if able
Mortgage - Sell the least valuable properties first
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
		pass #Auction decision would be here

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