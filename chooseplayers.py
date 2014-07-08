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
    ('Robinson', 'Cano', 'Seattle Mariners'), ('Yasiel', 'Puig', 'Los Angeles Dodgers'),
    ('Giancarlo', 'Stanton', 'Miami Marlins'), ('Adam', 'Lind', 'Toronto Blue Jays')
              ]

while len(updatedAccounts) != len(df):
       # used for making sure we don't repeat succesffuly updated accounts
    updatedUsernames = [account[0] for account in updatedAccounts]
    for index, username, password in df.itertuples():
        if username in updatedUsernames: 
            continue
        try: 
            print "\n-->Choosing players for account {} of {}. U: {}".format(
                         index+1, len(df), username)
            print "------> Accounts Done: {}({}%)".format(
                    len(updatedAccounts), float(len(updatedAccounts))/len(df))
            bot = Bot(str(username), str(password))
            p1 = random.choice(somePlayers)
            p2 = p1
            while p1 == p2:
                p2 = random.choice(somePlayers)
            bot.choose_players(p1=p1, p2=p2)
        except NoPlayerFoundException as e:
            bot.browser.quit()
            raise e
        except Exception as e:
            # import pdb
            # pdb.set_trace()
            print "-->Failure."
            print "-->Error Message: {}".format(e)
            bot.browser.quit()
            continue
        else:
            print "----->Success!"
            updatedAccounts.append((username, p1, p2))            

## Update the accounts file to reflect the updates
print "-->Updating accounts file: {}".format(Filepath.get_accounts_file())

    # Get the full production spreadsheet
today = str(datetime.today().month) + '-' + str(datetime.today().day)
fullDF = pd.read_excel(Filepath.get_accounts_file(), sheetname='Production')
if today in fullDF.columns: # if we had to redo the day, clear the column from the DF
    del fullDF[today]

    # Create the series correspodning to today's player selections
accountInfoL = [ 'NOT DONE' for i in range(len(fullDF)) ]
for updatedAccount in updatedAccounts:
    accountIndex = fullDF.Email[fullDF.Email == updatedAccount[0]].index[0]
        # make sure shit is lined up correctly
    accountInfoL[accountIndex] = 'Done. 1: {}, 2: {}'.format(
                                     updatedAccount[1], updatedAccount[2])

    # Put the dataframe together and print it to file
newDF = pd.concat([fullDF, pd.Series(accountInfoL, name=today)], axis=1)
newDF.to_excel(Filepath.get_accounts_file(), sheet_name='Production', index=False)

