# Welcome to Monopoly!

## Running the Program

To run, navigate to the Monopoly folder and run the following commands:

```
chmod +x testfile.sh  
./testfile.sh games -f filename
```

 - Games is an integer representing how many games you want to run
 - -f filename is an optional flag to provide a name for the file, will default to a 'data' folder as an xlsx file
 - -h flag can also be used to provide the same info on command line level

## Project Overview

This project aims to look at monopoly games simulated by different AI and conditions (specialized game modes) to take a more unique look at the game.
- Currently, only 1 controller is available as a very basic AI, however more will be added in the future to simulate both most-effecient and human-like gameplay.
- Additionally, as more controllers are added and game options, command-line parameters will be added to account for them.

Currently the game functions akin to a normal game of Monopoly, with the following simplifications:
- Trading/Voluntary selling has no functionality (as the base AI wouldn't use it anyway as per the specifications)

### Current Player-Controlled Decisions
- Stay in jail or pay to leave
- Buying a property
- Buying houses
- Unmortgaging
- Mortgaging (forced selling)
- Optional Selling (will handle properties & houses)
- Selling houses
- Auctions
- Trading

### Decision Handling
Each decision prompts the player for a response, the following is how each response is handled:

- **Jail**
  - Expects back a boolean response
  - If True, pays to leave, if False (or doesn't have the money), roll to leave
- **Buying a property**
  - Expects back a boolean response
  - If True, buys the property, if False, goes to auction
- **Buying houses**
  - Expects back a property response
  - Buys a house for the property returned, keeps asking until no more elligible properties, or none is returned
- **Unmortgaging**
  - Expects back a property response
  - Gives the controller a list of all properties the player can unmortgage
    - Theres two types for this, either optional unmortgage which has all properties unmortgaged that the player owns at the moment
    - The other is unmortgaging off of bankruptcy or trading (when trading is implemented), where after a mortgaged property moves owners the new owner has the option to unmortgage
- **Mortgaging**
  - Expects back a property response
  - Prompts to sell both properties, and houses (with properties prompted first), continues until costs are covered
- **Optional Selling**
  - Expects back a property response
  - NYI (Not yet implemented), will work similar to mortgaging, but break when None is returned
- **Auctions**
  - Expects back an integer response, greater than or equal to the original big provided
  - Prompts for a bid, if the same value is returned as the original bid the player is considered to be 'out' of the auction (or if bid >= player's money)
- **Trading**
  - NYI (Not yet implemented)
  - This one will be tricky, will likely iterate over every player and deciding what to trade (if at all), with another decision on the incoming end on whether to accept, reject, or counteroffer

### Export Information
Current single game exports, with each table its own sheet in the file:

**Round-by-Round Player Information Table**
- Players
- Money
- Net worth (doesn't include money)
- Net earnings
- Net losses
- Net total
- Round counter

**Payments Table**
- Players paying
- To whom
- What property
- Cost
- Bankrupted?
- Round & Turn counters

**Buying Table**
- Player
- Property
- Cost
- Net over/under buy cost (will be 0 unless auction)
  - 0 for house buy & unmortgage as well
- Classification (purchase/auction/house/unmortgage)
- Round & Turn counters

**Selling Table**
- Player
- Property
- Sold for
- Classification (mortgage/house - forced&optional \[4 in total])
  - Right now, just mortgage/house, since only forced is implemented
- Round & Turn counters

**Jail Information Table**
- Player
- Rounds elapsed
- Classification (Get out of jail free card/Optional&Forced pay/doubles/stay)
  - Labeled as: card/optional/forced/doubles/stay
- Round & Turn counters

Note, trading and optional selling yet to be implemented as per simplifications
