import monopoly_sim as ms

"""
The basic controller will make very bare-bones decisions.

Jail - Always pay to leave (unless you would need to mortgage)
Buying - Always purchase a property if able, always purchases houses if able to
Mortgage - Sell the least valuable properties first, never voluntarily sell
Auction - Bet the max bet up to the property's original price, then leave
Trading - Will never trade
"""

#Always tries to leave jail as long as doesnt have to sell
def jail_decision(player):
	return True

#Will never have both property and group have values
def buy_decision(player, property=None, group=None):
	if property:
		ms.buying_handler(player, property, property.buy_cost)
	elif group:
		#Housing buying is currently broken
		while True:
			properties_available = ms.even_buy_check(group)
			bought = False

			for property in properties_available:
				if property.group.house_cost < player.money:
					ms.buying_handler(player, property, property.group.house_cost, True)
					bought = True

			if not bought:
				break

#Returns Will never voluntarily sell so if forced is false do nothing
def mortgage_decision(player, cost, forced=False):
	if not forced:
		return

	player.sell(min(player.properties, key=lambda x: x.buy_cost))
	if player.money <= cost:
		mortgage_decision(player, cost, True)
	return

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

#Will never trade
def trading_decision(player):
	pass