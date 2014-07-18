#!/bin/bash
## A script to full the minion account files from instances 

## Google compute engine parameters
   # project specifier
projectFlag=--project='faiyam-bts-1'
   # directory of minion account files
googleAccountFilesDir=/home/faiyamrahman/programming/Python/beatthestreakBots/accountFiles/
minionAccountFilesSuffix=minionAccountFiles/
googleMinionDir=$googleAccountFilesDir$minionAccountFilesSuffix
   # directory of minion logs
googleLogDir=/home/faiyamrahman/programming/Python/beatthestreakBots/logs/
   # instance names
strat5Instance1='sn5vmn1'
strat5Instance2="sn5vmn2"

## Home computer parameters
homeMinionDir=/Users/faiyamrahman/Desktop/final/minions/
homeLogDir=/Users/faiyamrahman/Desktop/final/logs/

### account Files
for pair in "sn5vmn1 sN=5,vMN=1.xlsx" "sn5vmn2 sN=5,vMN=2.xlsx" \
            "sn6vmn1 sN=6,vMN=1.xlsx" "sn6vmn2 sN=6,vMN=2.xlsx"
do
    set -- $pair
    gcutil pull $projectFlag $1 $googleMinionDir$2 $homeMinionDir
done

### log files
for pair in "sn5vmn1 sN5vMN1/" "sn5vmn2 sN5vMN2/" "sn6vmn1 sN6vMN1/" \
            "sn6vmn2 sN6vMN2/"
do
    set -- $pair
    gcutil pull $projectFlag $1 $googleLogDir$2'*.txt' $homeLogDir$2
done
#     # Strategy 5
# suffix1="sN=5,vMN=1.xlsx"
# suffix2="sN=5,vMN=2.xlsx"
# gcutil pull $projectFlag $strat5Instance1 $googleMinionDir$suffix1 $homeMinionDir
# gcutil pull $projectFlag $strat5Instance2 $googleMinionDir$suffix2 $homeMinionDir

### log files
    # Strategy 5
# suffix1="sN5vMN1/"
# suffix2="sN5vMN2/"
# gcutil pull $projectFlag $strat5Instance1 $googleLogDir$suffix1'*.txt' $homeLogDir$suffix1
# gcutil pull $projectFlag $strat5Instance2 $googleLogDir$suffix2'*.txt' $homeLogDir$suffix2


# open the account files for inspection
for file in $homeMinionDir'*'
do 
    echo 
    echo "--> opening file"
    open $file
done 
