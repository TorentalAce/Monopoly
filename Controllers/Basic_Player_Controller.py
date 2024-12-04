import monopoly_sim as ms

"""
The basic controller will make very bare-bones decisions. Note, this will make most
games end in a draw (since most times no house groups end up collected, and payments can't
keep up with the gain from cards/go)

Jail - Always pay to leave (unless you would need to mortgage)
Property Buying - Always purchase a property if able
House Buying - Always tries to buy on the most expensive it can
Mortgage - Sell the least valuable property first, always try to sell properties before selling houses
Optional Sell - Never voluntarily sell
Selling Houses - Sell the least valuable houses if possible
Auction - Bet the max bet up to the property's original price, then leave
Trading - Will never trade
"""

#Always tries to leave jail as long as doesnt have to sell
def jail_decision(player, jail_card=[]):
	if len(jail_card) > 0: return jail_card[0]
	return True

#Will always try to buy (assumes can buy at this point)
def buy_decision(player, property=None):
	return True

"""
Takes a list of elligible properties that you can buy houses on
Returns a property to buy houses on (or none)
Elligible properties are properties that fulfill the following:
	a) all properties in the group are owned by the same player
	b) house cost < player money
	c) lowest amount of houses within the group
	d) less than 5 houses (a hotel)
"""

#Always buy the most expensive possible
def house_buy_decision(player, properties):
	return max(properties, key=lambda x: x.buy_cost)

#Returns minimum value property to sell, sells houses if can't sell properties
def mortgage_decision(player, cost, properties):
	if len(properties) == 0: return None
	return min(properties, key=lambda x: x.buy_cost)

#Will never optionally sell, also will be used for optional house selling
def optional_sell_decision(player):
	return None

#Always sell the least expensive
def house_sell_decision(player, properties):
	return min(properties, key=lambda x: x.group.house_cost)

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