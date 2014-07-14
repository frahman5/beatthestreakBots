#!/bin/bash
## A script to full the minion account files from instances 

## Google compute engine parameters
   # project specifier
projectFlag=--project='faiyam-bts-1'
   # directory of minion account files
googleAccountFilesDir=/home/faiyamrahman/programming/Python/beatthestreakBots/
minionAccountFilesSuffix=minionAccountFiles/
googleMinionDir=$googleAccountFilesDir$minionAccountFilesSuffix
   # instance names
strat5Instance1='sn5vmn1'
strat5Instance2="sn5vmn2"
accountMakerInstance="production-instance-c"

## Home computer parameters
homeAccountFilesDir=/users/faiyamrahman/programming/Python/beatthestreakBots/accountFiles/
homeMinionDir=$homeAccountFilesDir$minionAccountFilesSuffix

# Strategy 5
suffix1="sN=5,vMN=1.xlsx"
suffix2="sN=5,vMN=2.xlsx"
gcutil pull $projectFlag $strat5Instance1 $googleMinionDir$suffix1 $homeMinionDir
gcutil pull $projectFlag $strat5Instance2 $googleMinionDir$suffix2 $homeMinionDir

# master account file
suffix3="btsAccounts.xlsx"
gcutil pull $projectFlag $accountMakerInstance $googleAccountFilesDir$suffix3 $homeAccountFilesDir

# open the account files for inspection
for file in $homeMinionDir'*'
do 
    echo 
    echo "--> opening file"
    open $file
done 
