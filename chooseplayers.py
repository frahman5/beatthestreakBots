import random
import pandas as pd

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from datetime import datetime


from filepath import Fielpath
from bot import Bot
from config import ROOT

## get list of accounts you need
    # B: Email (i.e username)
    # D: MLBPassword
df = pd.read_excel( Filepath.get_accounts_file(), sheetname='Production',
                   parse_cols='B,D')

## update each of the accounts
    # list of tuples: (username, firstPlayerChoice, secondPlayerChoice)
updatedAccounts=[]
somePlayers = [ 
    ('Robinson', 'Cano', 'Seattle Mariners'), ('Mike', 'Trout', 'Los Angeles Dodgers'),
    ('Giancarlo', 'Stanton', 'Miami Marlins'), ('Adam', 'Lind', 'Toronto Blue Jays')
              ]
while len(updatedAccounts) != len(df):
    for username, password in df.itertuples():
        if username in updatedAccounts:
            continue
        try: 
            bot = Bot(username, password)
            p1 = random.choice(somePlayers)
            p2 = random.choice(somePlayers)
            bot.choose_players(p1=p1, p2=p2)
        except:
            continue
        else:
            updatedAccounts.append((username, p1, p2))            

## Update the accounts file to reflect the updates
today = str(datetime.today.month()) + '-' + str(datetime.today.day())
fullDF = pd.read_excel(Filepath.get_accounts_file(), sheetname='Production')
accountInfoL = []
for index, updatedAccount in enumerate(updatedAccounts):
        # make sure shit is lined up correctly
    assert updatedAccount[0] == fullDF.Email[index]
    accountInfoL.append( 'Done. 1: {}, 2: {}'.format(
                         updatedAccount[1], updatedAccount[2]))
newDF = pd.concat([fullDF, pd.Series(accountInfoL, name=today)])
newDF.to_excel(Filepath.get_accounts_file(), sheet_name='Production', index=False)
