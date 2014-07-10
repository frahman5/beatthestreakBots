#!/bin/bash
## Instructions for a single google cloud VM to select the appropriate players

## CD to the beatTheStreakBots folder
cd /home/faiyamrahman/programming/Python/beatthestreakBots
screen -l -m -d -S conquer1
    #-l | skips the login page, so we don't have to hit enter to get to the terminal functionalit
    #-m -d | Start screen in "detached" mode. creates a new session but doesn't attach to it
    #-S conquer | gives this screen session the nickname "conquer"
echo we succesffully make the screen
screen -r conquer1 | wall
./accounts.py num
