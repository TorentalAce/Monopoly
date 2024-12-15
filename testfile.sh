#This file is just to bulk run to look for less common errors
#!/bin/bash

set -e

fileName=""
cancel=0

while getopts "hf:c" flag; do
 case $flag in
 	h)
		echo "
		\nRun the script in the format ./testfile.sh 'Games' -f filename
		\n - 'Games' paramater is an integer >= 1 that represents the amount of games to run
		\n - -f flag is optional to provide a filename for the single game export functionality, 
	- if no filename is provided will default to 'data/single_game_export.xlsx' 
	- filename automatically is appended data/{filename}.xlsx, so only name needs to be provided.
		\n - -c flag is optional, will prevent data export and will only run the sim
		\n\n"
		exit 1;
	;;
	f)
		fileName=$OPTARG
	;;
	c)
		cancel=1
 esac
done

if ! [[ $1 =~ ^[0-9]+$ ]] || (( $1 == 0 )); then
	echo "'Games' argument must be an integer greater than or equal to 1"
	exit 1;
fi

for i in $(seq 1 $1)
do
	python3 monopoly_sim.py "$fileName" $cancel
done