import random
import pandas as pd

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from datetime import datetime


from filepath import Filepath
from bot import Bot
from config import ROOT
from exception import NoPlayerFoundException

## get list of accounts you need
print "\n-->Getting accounts file {}".format(Filepath.get_accounts_file())
    # B: Email (i.e username)
    # D: MLBPassword
df = pd.read_excel( Filepath.get_accounts_file(), sheetname='Production',
                   parse_cols='B,D')

## update each of the accounts
    # list of tuples: (username, firstPlayerChoice, secondPlayerChoice)
updatedAccounts=[]
somePlayers = [ 
    ('Robinson', 'Cano', 'Seattle Mariners'), ('Mike', 'Trout', 'Los Angeles Dodgers')]
    # ('Giancarlo', 'Stanton', 'Miami Marlins'), ('Adam', 'Lind', 'Toronto Blue Jays')
    #           ]
print df
while len(updatedAccounts) != len(df):
    updatedUsernames = [account[0] for account in updatedAccounts]
    for index, username, password in df.itertuples():
        if username in updatedUsernames:
            continue
        try: 
            print "\n-->Choosing players for account {} of {}. U: {}".format(
                         index+1, len(df), username)
            print "------> Done: {}({}%)".format(len(updatedUsernames), 
                                                 float(len(updatedUsernames))/len(df))
            bot = Bot(str(username), str(password))
            p1 = random.choice(somePlayers)
            p2 = random.choice(somePlayers)
            bot.choose_players(p1=p1, p2=p2)
        except NoPlayerFoundException as e:
            bot.browser.quit()
            raise e
        except Exception as e:
            bot.browser.quit()
            print "-->Failure."
            print "-->Error Message: {}".format(e.message)
            continue
        else:
            print "----->Success!"
            updatedAccounts.append((username, p1, p2))            

## Update the accounts file to reflect the updates
print "-->Updating accounts file: {}".format(Filepath.get_accounts_file())
today = str(datetime.today().month) + '-' + str(datetime.today().day)
fullDF = pd.read_excel(Filepath.get_accounts_file(), sheetname='Production')
accountInfoL = []
for index, updatedAccount in enumerate(updatedAccounts):
        # make sure shit is lined up correctly
    assert updatedAccount[0] == fullDF.Email[index]
    accountInfoL.append( 'Done. 1: {}, 2: {}'.format(
                         updatedAccount[1], updatedAccount[2]))
newDF = pd.concat([fullDF, pd.Series(accountInfoL, name=today)], axis=1)
newDF.to_excel(Filepath.get_accounts_file(), sheet_name='Production', index=False)

