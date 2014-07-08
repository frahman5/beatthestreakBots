import os            # for error handling
import sys           # for error handling
import random        # random player selections
import logging       # error logging
import pandas as pd  # excel spreadsheet manipulation

from datetime import datetime # to get today's date

from filepath import Filepath 
from bot import Bot
from config import ROOT
from exception import NoPlayerFoundException, FailedAccountException, \
                      FailedUpdateException

def getLogger():
    ## Create logger that handles file logging
    logger = logging.getLogger()
         # handler to write to logs
    fileHandler = logging.FileHandler(Filepath.get_log_file())
    formatter = logging.Formatter('%(asctime)s %(message)s\n')
    fileHandler.setFormatter(formatter)
         # add handlers to logger
    logger.addHandler(fileHandler)

    return logger

def logError(username, password, p1, p2, exception, logger):
    """
    string string TupleOfStrings TupleOfStrings Exception logger -> None
        username: str | username of account being updated at the time of exception
        password: str | password of account being updated at the time of exception
        p1: TupleOfStrings | (firstName, lastName, team) of first player
            being added to account at time of exception
        p2: TupleOfStrings | (firstName, lastName, team) of second player 
            being added to account at time of exception (possible empty)
        exception: Exception | the exception raised 
        logger: logger | logger to use to log errors

    Logs the error to file
    """
       # we don't check the type of exception because i don't know how to do that
    assert type(username) == str
    assert type(password) == str
    assert type(p1) == tuple
    assert type(p2) == tuple
    assert type(logger) == logging.RootLogger

    logger.error("Unit account update failure: {}, {}".format(username, password))
    logger.error("    p1, p2: {}, {}".format(p1, p2))
    logger.error(exception, exc_info=True)

def logFailedAccounts(failedAccounts, numTotalAccounts, logger):
    """
    list int logger -> None
       failedAccounts: ListOfTuples | Each Tuple is a (username, password)
           if a failed Account
       numTotalAccounts: int | the total number of accounts that we attempted
           to update
       logger: logger | logger to use to log errors

    Logs the failedAccounts to today's error log in the event that the main 
    while loop failed to update all players
    """
    # check that we got an appropriate input
    assert len(failedAccounts) != 0
    assert type(failedAccounts) == list
    for elem in failedAccounts:
        assert type(elem) == tuple
        for thing in elem:
            assert type(thing) == str

    # log those errors baby
    logger.error("{} of {} accounts failed".format(
                    len(failedAccounts), numTotalAccounts))
    for failedAccount in failedAccounts:
        logger.error("    U, P: {}, {}".format(failedAccount[0], failedAccount[1]))

def main():
    ## get an error logger for this run
    print "\n-->Creating Error Logger"
    logger = getLogger()

    ## get list of accounts you need
    print "-->Getting accounts file {}".format(Filepath.get_accounts_file())
    df = pd.read_excel( Filepath.get_accounts_file(), sheetname='Production',
                        parse_cols= 'B,' + # Email (i.e username)
                                    'D'    # MLBPassword)
                  )

    ## update each of the accounts
        # list of tuples: (username, firstPlayerChoice, secondPlayerChoice)
    updatedAccounts=[]
    somePlayers = [ 
                    ('Robinson', 'Cano', 'Seattle Mariners'), 
                    ('Paul', 'Goldschmidt', 'Arizona Diamondbacks'),
                    ('Giancarlo', 'Stanton', 'Miami Marlins'), 
                    ('Adam', 'Lind', 'Toronto Blue Jays')
                  ]

    lenDF = len(df)
    numIters = 0
    failedAccounts = [] # in case we fail to update some accounts
    while len(updatedAccounts) != lenDF:

        ## If we've run the loop "too many" times, exit out
        if numIters > (2 * lenDF):
            for index, username, password in df.itertuples():
                if username not in updatedUsernames:
                    failedAccounts.append((str(username), str(password)))
            logFailedAccounts(failedAccounts, lenDF, logger)
            break

            # used for making sure we don't repeat succesffuly updated accounts
        updatedUsernames = [account[0] for account in updatedAccounts]

        ## Update those accounts baby!
        for index, username, password in df.itertuples():

            # don't update the same account twice
            if username in updatedUsernames: 
                continue

            numIters += 1
            # try to update the account 
            try: 
                print "\n-->Iteration {} of {}".format(numIters, 2 * lenDF)
                print "-->Choosing players for account {} of {}. U: {}".format(
                             index+1, lenDF, username)
                print "------> Accounts Done: {0}({1:.2f}%)".format(
                            len(updatedAccounts), 
                            float(len(updatedAccounts))/float(lenDF))
                bot = None # in case we throw an exception while constructing Bot
                bot = Bot(str(username), str(password))
                p1 = random.choice(somePlayers)
                p2 = p1
                while p1 == p2:
                    p2 = random.choice(somePlayers)
                bot.choose_players(p1=p1, p2=p2)

            # this should never happen
            except NoPlayerFoundException as e:
                if bot:
                    bot.browser.quit()
                raise e

            # sometimes unstable browsers raise exceptions. Just try again
            except Exception as e:
                exc_type = sys.exc_info()[0]
                print "------> Failure: {}".format(exc_type)
                print "------> Logging to file"
                logError( str(username), str(password), 
                          p1, p2, e, logger)
                if bot:
                    bot.browser.quit()
                continue

            # If it worked, record as much and keep going!
            else:
                print "-----> Success!"
                updatedAccounts.append((username, p1, p2))            

    ## Update the accounts file to reflect the updates
    print "--> Updating accounts file: {}".format(Filepath.get_accounts_file())

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
    newDF.to_excel( Filepath.get_accounts_file(), 
                    sheet_name='Production', 
                    index=False # we don't want an extra column of row indices
                  )


if __name__ == '__main__':
    main()
