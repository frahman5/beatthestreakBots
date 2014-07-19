#!/bin/bash
## A script to pull the minion account files and logs from instances 

## Global variables
homeMinionDir=/Users/faiyamrahman/Desktop/final/minions/

function pullFiles {
  # strategyNumber -> None
  # Given a strategy Number, pulls in the logs and minion account files 

  ## Google compute engine parameters
     # project specifier
  p=--project='faiyam-bts-1'
     # directory of minion account files
  googleMinionDir=/home/faiyamrahman/programming/Python/beatthestreakBots/accountFiles/minionAccountFiles/
     # directory of minion logs
  googleLogDir=/home/faiyamrahman/programming/Python/beatthestreakBots/logs/

  ## Home computer parameters
  homeLogDir=/Users/faiyamrahman/Desktop/final/logs/

  # Assign necessary variables
  instance='sn'$1
  minion1=$googleMinionDir'sN='$1',vMN=1.xlsx'
  minion2=$googleMinionDir'sN='$1',vMN=2.xlsx'
  logFolder1='sN'$1'vMN1/'
  logFolder2='sN'$1'vMN2/'

  # Pull account files
  gcutil pull $p $instance $minion1 $minion2 $homeMinionDir
    
  # Pull log files
  gcutil pull $p $instance $googleLogDir$logFolder1'*.txt' $homeLogDir$logFolder1
  gcutil pull $p $instance $googleLogDir$logFolder2'*.txt' $homeLogDir$logFolder2 

}

## Pull files in parallel
pullFiles 5 & pullFiles 6 & pullFiles 7 & pullFiles 8 & pullFiles 9 & \ 
pullFiles 10 & pullFiles 11 & pullFiles 12 & pullFiles 13 & pullFiles 14 & \
pullFiles 15 & pullFiles 16 & pullFiles 17 & wait
echo "*********** FILES PULLED! ************"

# let me know which strategies ran to completion
source /Users/faiyamrahman/programming/Python/beatthestreakBots/bvenv/bin/activate
python update.py $homeMinionDir $1

