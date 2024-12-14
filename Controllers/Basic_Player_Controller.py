import monopoly_sim as ms

#Always tries to leave jail as long as doesnt have to sell
def jail_decision(player, jail_card=[]):
	if len(jail_card) > 0: return jail_card[0]
	return True

#Will always try to buy (assumes can buy at this point)
def buy_decision(player, property=None):
	return True

#Always tries to unmortgage the most expensive property
def unmortgage_decision(properties):
	return max(properties, key=lambda x: x.buy_cost)

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