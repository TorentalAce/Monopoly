# Controller Information
This file is to describe current controller decision making behavior, and what factors into the results

## Basic Player Controller
As the most bare-bones AI, the decision making here is relatively straight forward, since the decisions are all static

### Jail
Always pay to leave (unless you would need to mortgage)

### Property Buying
Always purchase a property if able

### House Buying
Always tries to buy on the most expensive it can

### Unmortgaging
Always tries to unmortgage the most expensive option

### Mortgage
Sell the least valuable property first, always try to sell properties before selling houses

### Optional Sell
Never voluntarily sell

### Selling Houses
Sell the least valuable houses if possible

### Auction
Bet the max bet up to the property's original price, then leave

### Trading
Will never trade
