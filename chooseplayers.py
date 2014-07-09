import random        # random player selections
import pandas as pd  # excel spreadsheet manipulation

from types import FunctionType # to type check function inputs that we expect to be functions
from datetime import datetime # to get today's date

from filepath import Filepath 
from bot import Bot
from config import ROOT
from exception import NoPlayerFoundException, FailedAccountException, \
                      FailedUpdateException
from errorlogging import getLogger, logError, logFailedAccounts

def choosePlayers(**kwargs):
    """
    kwargs -> None
        kwargs;
        funcDict(REQUIRED): dict | a dictionary with key, value pairs of:
            strategyNumber: (selection_func, distribution_func). See below
            for descriptions of selection_func and distribution_func
                selection_func: Function | Takes today's date, 
                   returns a tuple of players eligible for distribution 
                   to the various accounts.
                distribution_func: Function | Takes a bot, and a list of 
                   distribution-eligible players, and assigns the appropriate 
                   players to that bot. Returns a tuple (p1, p2) of the 
                   players that were assigned to the bot
        sN(REQUIRED): int | "strategy number" (see strategyNumber.txt)
        vMN(REQUIRED): int | Indicates which of n virtual machines responsible
           for executing sN is currently calling choosePlayers. For example,
           we might have 2 VMs responsible for executing strategy 3 for 1000
           accounts. The first VM will be responsible for the first 500 accounts, 
           and the second Vm will be responsible for the last 500 accounts.

    Reads in the accounts from Filepath.get_accounts_file() that correspond
    to sN, vMN, and then updates those accounts accordingly
    """
    ###### Get our arguments: #####
    funcDict = kwargs['funcDict']
    sN = kwargs['sN']
    vMN = kwargs['vMN']

    ###### get an error logger #####
    print "\n-->Creating Error Logger"
    logger = getLogger()

    ##### get list of accounts you need #####
    print "-->Getting accounts file {}".format(Filepath.get_accounts_file())
        # read in the master accounts file
    df = pd.read_excel( Filepath.get_accounts_file(), sheetname='Production',
                        parse_cols= 'B,' + # Email (i.e username)
                                    'D,'  + # MLBPassword)
                                    'E,'  + # Strategy
                                    'F'    # VM
                       )
        # parse it down to only include those accounts with this strategy
        # number and virtual machine number
    df = df[df.Strategy == sN][df.VM == vMN]

    ###### update each of the accounts #####
    print "-->Getting today's eligible players"
    eligiblePlayers = funcDict[sN]['select_func'](datetime.today().date())
    failedAccounts = [] # in case we fail to update some accounts
    updatedAccounts = [] # to keep track of which accounts we need to log to file!
    lenDF = len(df)
    numIters = 0
    while len(updatedAccounts) != lenDF:

        ## If we've run the loop "too many" times, exit out
        if numIters > (2 * lenDF):
            for index, username, password, sN, vMN in df.itertuples():
                if username not in updatedUsernames:
                    failedAccounts.append((str(username), str(password)))
            logFailedAccounts(failedAccounts, lenDF, logger)
            break

            # used for making sure we don't repeat succesffuly updated accounts
        updatedUsernames = [account[0] for account in updatedAccounts]

        ## Update those accounts baby!
        for index, username, password, sN, vMN in df.itertuples():

            # don't update the same account twice
            if username in updatedUsernames: 
                continue

            # try to update the account 
            numIters += 1
            try: 
                # print update information
                print "\n-->Iteration {} of {}".format(numIters, 2 * lenDF)
                print "-->Choosing players for account {} of {}. U: {}".format(
                             index+1, lenDF, username)
                print "------> Accounts Done: {0}({1:.2f}%)".format(
                            len(updatedAccounts), 
                            float(len(updatedAccounts))/float(lenDF))

                # make the appropriate bot and update him
                bot, p1, p2 = (None, None, None) # in case we throw an exception before they get assigned
                bot = Bot(str(username), str(password))
                p1, p2 = funcDict[sN]['dist_func'](bot, eligiblePlayers)

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

        # Create the series corresponding to today's player selections
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
    """
    Usage:
        1) python chooseplayers.py -sN={strategyNumber} -vMN={virtualMachineNumber}
    """
    import re
    import sys

    from selectfunctions import todaysRecommendedPicks
    from distributionfunctions import randDownRandPlayers

    ## What strategyNumber and virtualMachine Number are we using?
    options = [arg for arg in sys.argv if '-' in arg]

        # Get the strategy number
    sNPattern = re.compile(r"""
        -sN=            # strategy number
        [1-5]           # method number must be in (1, 2, 3, 4, 5)
        """, re.VERBOSE)
    matches = [ sNPattern.match(option) for option in 
                options if sNPattern.match(option)]
    print [match.string for match in matches]
    assert len(matches) == 1
    sN = int(matches[0].string[4:])
    options.remove(matches[0].string)

        # Get the virtualMachine Number
    vMNPattern = re.compile(r"""
        -vMN=            # virtual machine number
        [1-9]            # first digit must be nonzero
        [0-9]*           # arbitrary number of digits
        """, re.VERBOSE)
    matches = [ vMNPattern.match(option) for option in 
                options if vMNPattern.match(option)]
    assert len(matches) == 1
    vMN = int(matches[0].string[5:])
    options.remove(matches[0].string)

    ## Check that we didn't get any bogus options:
    if len(options) != 0:
        raise KeyError("Invalid options: " + str(options))

    funcDict = {
        5: { 'select_func': todaysRecommendedPicks, 
             'dist_func'  : randDownRandPlayers }
                }
    print "\n******Choosing players for strategy, VM: {}, {}******".format(sN, vMN)
    choosePlayers( funcDict=funcDict, sN=sN, vMN=vMN )
