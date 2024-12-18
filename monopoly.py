import monopoly_sim as ms
import pandas as pd
import argparse

"""
Current (known) errors/need to change:
	- There may be an infinite loop error with mortgage/house sell, doesnt happen often

Todo: Fix the error (added a lazy fix of a timeout after 5 seconds to handle this for now)
"""

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Parse arguments")
	parser.add_argument('filename', type=str)
	parser.add_argument('choiceExport', type=int)
	parser.add_argument('gameNumber', type=int)
	args = parser.parse_args()

	jailDF = pd.DataFrame()
	playerDF = pd.DataFrame()
	propertyDF = pd.DataFrame()
	auctionDF = pd.DataFrame()
	eventDF = pd.DataFrame()

	if args.choiceExport == 2:
		for i in range(0, args.gameNumber):
			new = ms.main(2, i)
			playerDF = pd.concat([playerDF, new[0]], ignore_index=True)
			propertyDF = pd.concat([propertyDF, new[1]], ignore_index=True)
			eventDF = pd.concat([eventDF, new[2]], ignore_index=True)
			auctionDF = pd.concat([auctionDF, new[3]], ignore_index=True)
			jailDF = pd.concat([jailDF, new[4]], ignore_index=True)
	elif args.choiceExport == 3:
		count = 0
		while True:
			try:
				new = ms.main(3, count)
			except SystemExit: continue

			if not new[5]: continue
			count += 1
			playerDF = pd.concat([playerDF, new[0]], ignore_index=True)
			propertyDF = pd.concat([propertyDF, new[1]], ignore_index=True)
			eventDF = pd.concat([eventDF, new[2]], ignore_index=True)
			auctionDF = pd.concat([auctionDF, new[3]], ignore_index=True)
			jailDF = pd.concat([jailDF, new[4]], ignore_index=True)
			if count == args.gameNumber: break
	else:
		for i in range(0, args.gameNumber-1):
			ms.main(0, i)
		playerDF, propertyDF, eventDF, auctionDF, jailDF = ms.main(args.choiceExport, args.gameNumber-1)

	if args.choiceExport != 0:
		fileName = args.filename
		if fileName.find(".") != -1:
			fileName = fileName[:fileName.find(".")]

		if args.choiceExport == 1:
			fileName = f"data/{fileName}.xlsx" if fileName != "" else "data/single_game_export.xlsx"
		else:
			fileName = f"data/{fileName}.xlsx" if fileName != "" else "data/multi_game_export.xlsx"

		with pd.ExcelWriter(fileName) as writer:
			playerDF.to_excel(writer, sheet_name='Player Information', index=False)
			propertyDF.to_excel(writer, sheet_name='Property Information', index=False)
			eventDF.to_excel(writer, sheet_name='Event Tracking Information', index=False)
			auctionDF.to_excel(writer, sheet_name='Auction Tracking Information', index=False)
			jailDF.to_excel(writer, sheet_name='Jail Information', index=False)