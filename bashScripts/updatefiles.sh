#!/bin/bash
## A script to pull the minion account files and logs from instances 

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


# instanceStuff=(\
#       # "sn5vmn1 sN=5,vMN=1.xlsx sN5vMN1/" "sn5vmn2 sN=5,vMN=2.xlsx sN5vMN2/"\
#       # "sn6vmn1 sN=6,vMN=1.xlsx sN6vMN1/" "sn6vmn2 sN=6,vMN=2.xlsx sN6vMN2/" \
#       # "sn7vmn1 sN=7,vMN=1.xlsx sN7vMN1/" "sn7vmn2 sN=7,vMN=2.xlsx sN7vMN2/" \
#       ("sn8vmn1 sN=8,vMN=1.xlsx sN8vMN1/") ("sn8vmn2 sN=8,vMN=2.xlsx sN8vMN2/") \
#       "sn9vmn1 sN=9,vMN=1.xlsx sN9vMN1/" "sn9vmn2 sN=9,vMN=2.xlsx sN9vMN2/" \
#       "sn10vmn1 sN=10,vMN=1.xlsx sN10vMN1/" "sn10vmn2 sN=10,vMN=2.xlsx sN10vMN2/" \
#       "sn11vmn1 sN=11,vMN=1.xlsx sN11vMN1/" "sn11vmn2 sN=11,vMN=2.xlsx sN11vMN2/" \
#       "sn12vmn1 sN=12,vMN=1.xlsx sN12vMN1/" "sn12vmn2 sN=12,vMN=2.xlsx sN12vMN2/" \
#       "sn13vmn1 sN=13,vMN=1.xlsx sN13vMN1/" "sn13vmn2 sN=13,vMN=2.xlsx sN13vMN2/" \
#       "sn14vmn1 sN=14,vMN=1.xlsx sN14vMN1/" "sn14vmn2 sN=14,vMN=2.xlsx sN14vMN2/" \
#       "sn15vmn1 sN=15,vMN=1.xlsx sN15vMN1/" "sn15vmn2 sN=15,vMN=2.xlsx sN15vMN2/" \
#       "sn16vmn1 sN=16,vMN=1.xlsx sN16vMN1/" "sn16vmn2 sN=16,vMN=2.xlsx sN16vMN2/" \
#       "sn17vmn1 sN=17,vMN=1.xlsx sN17vMN1/" "sn17vmn2 sN=17,vMN=2.xlsx sN17vMN2/" \
#     )
### account Files
for triplet in  "sn8vmn1 sN=8,vMN=1.xlsx sN8vMN1/" "sn8vmn2 sN=8,vMN=2.xlsx sN8vMN2/" \
                "sn9vmn1 sN=9,vMN=1.xlsx sN9vMN1/" "sn9vmn2 sN=9,vMN=2.xlsx sN9vMN2/" \
                "sn10vmn1 sN=10,vMN=1.xlsx sN10vMN1/" "sn10vmn2 sN=10,vMN=2.xlsx sN10vMN2/" \
                "sn11vmn1 sN=11,vMN=1.xlsx sN11vMN1/" "sn11vmn2 sN=11,vMN=2.xlsx sN11vMN2/" \
                "sn12vmn1 sN=12,vMN=1.xlsx sN12vMN1/" "sn12vmn2 sN=12,vMN=2.xlsx sN12vMN2/" \
                "sn13vmn1 sN=13,vMN=1.xlsx sN13vMN1/" "sn13vmn2 sN=13,vMN=2.xlsx sN13vMN2/" \
                "sn14vmn1 sN=14,vMN=1.xlsx sN14vMN1/" "sn14vmn2 sN=14,vMN=2.xlsx sN14vMN2/" \
                "sn15vmn1 sN=15,vMN=1.xlsx sN15vMN1/" "sn15vmn2 sN=15,vMN=2.xlsx sN15vMN2/" \
                "sn16vmn1 sN=16,vMN=1.xlsx sN16vMN1/" "sn16vmn2 sN=16,vMN=2.xlsx sN16vMN2/" \
                "sn17vmn1 sN=17,vMN=1.xlsx sN17vMN1/" "sn17vmn2 sN=17,vMN=2.xlsx sN17vMN2/" 
do
    set -- $triplet
    gcutil pull $projectFlag $1 $googleMinionDir$2 $homeMinionDir # account file
    gcutil pull $projectFlag $1 $googleLogDir$3'*.txt' $homeLogDir$3 # log file
done

# ### log files
# for pair in "sn5vmn1 sN5vMN1/" "sn5vmn2 sN5vMN2/" "sn6vmn1 sN6vMN1/" \
#             "sn6vmn2 sN6vMN2/" "sn7vmn1 sN7vMN1/" "sn7vmn2 sN7vMN2/"
# do
#     set -- $pair
#     gcutil pull $projectFlag $1 $googleLogDir$2'*.txt' $homeLogDir$2
# done


# open the account files for inspection
for file in $homeMinionDir'*'
do 
    echo 
    echo "--> opening file"
    open $file
done 
