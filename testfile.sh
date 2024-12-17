#This file is just to bulk run to look for less common errors
#!/bin/bash

set -e

fileName=""
choice=0
games=1

while getopts 'hn:f:c:' flag; do
 case $flag in
 	n) games=$OPTARG ;;
 	h)
		echo "
		\nRun the script in the format ./testfile.sh 'Games' -f filename -c 0/1/2
		\n - -n flag is optional to provide an integer >= 1 that represents the amount of games to run, will default to 1 if none is provided
		\n - -f flag is optional to provide a filename for the single game export functionality, 
	- if no filename is provided will default to 'data/single_game_export.xlsx' 
	- filename automatically is appended data/{filename}.xlsx, so only name needs to be provided.
		\n - -c flag is optional, will default to 0 
	- 0 is no export
	- 1 is single game export (will export last game)
	- 2 is full multi-game export
	- 3 is multi-game export of only winning games (excludes tie results)
		\n"
		exit 1;
	;;
	f) fileName=$OPTARG ;;
	c) choice=$OPTARG ;;
 esac
done

if ! [[ $games =~ ^[0-9]+$ ]] || (( $games == 0 )); then
	echo "'Games' argument must be an integer greater than or equal to 1"
	exit 1;
fi

python3 monopoly.py "$fileName" $choice $games