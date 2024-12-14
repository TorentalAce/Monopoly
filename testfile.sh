#This file is just to bulk run to look for less common errors
#!/bin/bash

set -e

fileName=""

while getopts "hf:" flag; do
 case $flag in
 	h)
		echo "
		\nRun the script in the format ./testfile.sh 'Games' -f filename
		\n - 'Games' paramater is an integer >= 1 that represents the amount of games to run
		\n - Filename flag is optional to provide a filename for the single game export functionality, 
	- if no filename is provided will default to 'data/single_game_export.xlsx' 
	- filename automatically is appended data/{filename}.xlsx, so only name needs to be provided.
		\n\n"
		exit 1;
	;;
	f)
		fileName = $OPTARG
	;;
 esac
done

if ! [[ $1 =~ ^[0-9]+$ ]] || (( $1 == 0 )); then
	echo "'Games' argument must be an integer greater than or equal to 1"
	exit 1;
fi

for i in $(seq 1 $1)
do
	python3 monopoly_sim.py "$fileName"
done