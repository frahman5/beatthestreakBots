# beatthestreakBots
I built some robots. 

MLB offers a fantasy baseball game called "Beat the Streak." During the MLB season, participants can daily choose up to two players that they believe will get a hit in their game that day. 
If you guess 57 players in a row correctly, you win $5.7 million dollars. 

In this repo, I built 13 Narrow Artificial Intelligence enabled bots to play Beat the Streak for me. Each bot plays the game on 1,000 unique accounts. 

In a related [repo] (https://github.com/frahman5/beatthestreak), I wrote code to simulate hundreds of thousands of different strategies using historical baseball data. I chose what I believed to be the top 13 strategies to implement here. 

This repo includes not only the code for those bots (in Python), but also bash scripts to automate the process of launching the bots on the Google Compute Engine. 

The main python file is chooseplayers.py. 
