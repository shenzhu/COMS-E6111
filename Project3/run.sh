#!/bin/sh

if [ "$#" != "3" ]; then
	echo "Illegal number of arguments"
	echo "Usage: ./run.sh INTEGRATED-DATASET.csv min_sup min_conf"
else
	python main.py $1 $2 $3
fi