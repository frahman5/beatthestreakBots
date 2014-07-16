#!/bin/bash

## A script to run on the virtual machines, AFTER OPENING A SCREEN, 
## to choose players
## Usage: ./chooseplayers.sh sN vMN

## Get strategy and virtual machine numbers
sN=$1
vMN=$2
d=$3

## Home of python script
pyscript=/home/faiyamrahman/programming/Python/beatthestreakBots/chooseplayers.py

## Run the program
python $pyscript -sN=$1 -vMN=$2 -d=$3
