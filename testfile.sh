#This file is just to bulk run to look for less common errors

set -e

for i in $(seq 1 $1)
do
	python3 monopoly_sim.py
done