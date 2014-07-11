#!/bin/bash
## A script to full the minion account files from instances 

## Google compute engine parameters
   # project specifier
projectFlag=--project='faiyam-bts-1'
   # directory of minion account files
googleMinionDir=/home/faiyamrahman/programming/Python/beatthestreakBots/minionAccountFiles/
   # instance names
strat5Instance1='production-instance-a'
strat5Instance2="production-instance-b"

## Home computer parameters
homeMinionDir=/Users/faiyamrahman/programming/Python/beatthestreakBots/minionAccountFiles/

# Strategy 5
suffix1="sN=5,vMN=1.xlsx"
suffix2="sN=5,vMN=2.xlsx"
gcutil pull $projectFlag $strat5Instance1 $googleMinionDir$suffix1 $homeMinionDir
gcutil pull $projectFlag $strat5Instance2 $googleMinionDir$suffix2 $homeMinionDir

