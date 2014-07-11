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

def get_num_accounts(sN=None, vMN=None, getRemaining=True):
    """
    int int bool -> int 
       sN: Strategy Number
       vMN: virtual Machine Number
       remaining: Indicates whether or not to count a player iff he hasn't
           already been assigned to today.

    Returns the number of accounts correspodning to strategy number sN
    abd virtual machine vMN. If required==True, then only returns the number
    of accounts that have yet to be assigned to
    """
    import os

    ## Type check
    assert type(sN) == int
    assert type(vMN) == int
    assert type(getRemaining) == bool

    today = str(datetime.today().month) + '-' + str(datetime.today().day)
    minionPath = Filepath.get_minion_account_file(sN=sN, vMN=vMN)

    if os.path.isfile(minionPath):
        minionDF = pd.read_excel( minionPath, sheetname="Production")
        # get the accounts that haven't been assigned to yet if appropriate
        if getRemaining and (today in minionDF.columns): 
            minionDF = minionDF[pd.isnull(minionDF[today])] #pd.isnull checks for nans
    else:    
        ## Get the corresponding accounts
        fullDF = pd.read_excel( Filepath.get_accounts_file(), 
                                sheetname='Production',
                                parse_cols= 'A:F' )
        minionDF = fullDF[fullDF.Strategy == sN][fullDF.VM == vMN]

    ## return the length of the dataframe
    return len(minionDF)

def log_updated_accounts(updatedAccounts, sN=None, vMN=None):
    """
    ListOfTuples -> None
       updatedAccounts: ListOfTuples | A list of the accounts that were
            updated in the choosePlayers function. Format: 
                (username, p1, p2) 
            where p2 and p2 are TuplesOfStrings of format 
                (firstName, lastName, teamAbbreviation)
        sN: int | "strategy number" (see strategyNumber.txt)
        vMN: int | virtual Machine Number.
    """
    import os

    ## Let the user know wazzap
    minionAF = Filepath.get_minion_account_file(sN=sN, vMN=vMN)
    print "--> Updating accounts file: {}".format(minionAF)
    
    ## type check
    assert type(updatedAccounts) == list
    assert type(sN) == int
    assert type(vMN) == int

    ## If the minion spreadsheet hasn't been initalized yet, do so
    if not os.path.isfile(minionAF): # initalize it
        fullDF = pd.read_excel( Filepath.get_accounts_file(), 
                                sheetname='Production',
                                parse_cols= 'A:F' )
        minionDF = fullDF[fullDF.Strategy == sN][fullDF.VM == vMN]
        minionDF.to_excel( minionAF, 
                           sheet_name='Production', 
                           index=False # no extra column of row indices  
                         ) 

    ## Get the minion spreadsheet corresponding to this sN and vMN
    today = str(datetime.today().month) + '-' + str(datetime.today().day)
    minionDF = pd.read_excel( minionAF, sheetname='Production' )

    ## Create the series corresponding to today's player selections
    if today in minionDF.columns: 
        accountInfoL = list(minionDF[today])
        del minionDF[today]
    else:
        accountInfoL = ['' for i in range(len(minionDF))]
    for updatedAccount in updatedAccounts:
        accountIndex = minionDF.Email[ minionDF.Email == \
                                       updatedAccount[0]].index[0]
            # make sure shit is lined up correctly
        accountInfoL[accountIndex] = 'Done. 1: {}, 2: {}'.format(
                                         updatedAccount[1], updatedAccount[2])

    ## Put the dataframe together and print it to file
    newDF = pd.concat([minionDF, pd.Series(accountInfoL, name=today)], axis=1)
    newDF.to_excel( minionAF, 
                    sheet_name='Production', 
                    index=False # we don't want an extra column of row indices
                  )

def choosePlayers(**kwargs):
    """
    kwargs -> str|None
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
        num(REQUIRED): int | Indicates how many accounts to assign to

    Reads in the accounts from Filepath.get_accounts_file() that correspond
    to sN, vMN, and then updates num of those accounts accordingly

    Returns 'done' if done, else None
    """
    import os

    ###### Get our arguments: #####
    funcDict = kwargs['funcDict']
    sN = kwargs['sN']
    vMN = kwargs['vMN']
    num = kwargs['num']

    ###### get an error logger #####
    print "\n--> Creating Error Logger"
    logger = getLogger()

    ##### get list of accounts you need #####
    print "--> Getting accounts file {}".format(Filepath.get_accounts_file())
        # read in the minion accounts file if available, else the master accounts file
    minionPath = Filepath.get_minion_account_file(sN=sN, vMN=vMN)
    if os.path.isfile(minionPath):
        dfPath = minionPath
    else:
        dfPath = Filepath.get_accounts_file()
    df = pd.read_excel( dfPath, sheetname='Production' )
        # If it's the master accounts file, parse it down to only include 
        # those accounts with this strategy number and virtual machine number
    if dfPath != minionPath:
        df = df[df.Strategy == sN][df.VM == vMN]
        # Parse it down to only include those accounts that haven't yet been updated
    today = str(datetime.today().month) + '-' + str(datetime.today().day)
    if today in df.columns:
        df = df[pd.isnull(df[today])] # pd.isnull checks for nans, which in our case indicate today's virgin accounts
        # Parse it down to only include the columns we want
    df = df[['ID', 'Email', 'MLBPassword', 'Strategy', 'VM']]
    fulldf = df # in case there are no more eligible players left
        # Lastly, Parse it down to only include num of those accounts
    df = df[0:num] # if num = 7, this gives us rows 0 (the header) through 7
    

    # Get today's eligible players    
    print "--> Getting today's eligible players"
    if sN == 5:
        eligiblePlayers = funcDict[sN]['select_func'](datetime.today().date())
    elif sN in (6, 7):
        eligiblePlayers = funcDict[sN]['select_func']( p=20, 
                                                       today=datetime.today().date(),
                                                       filt={ 'minERA': 4.0 } )
    print "--> Today's eligible Players: "
    for player in eligiblePlayers:
        print "          " + str(player)
    if len(eligiblePlayers) == 0: # report that there's no more selections today
        updatedAccounts = \
            [ (username, ('NOELIGIBLE'), ('NOELIGIBLE')) for 
                 dummyIndex, index, username, password, sN, vMN in 
                 fulldf.itertuples() ]
        print "--> NO PLAYERS LEFT TODAY. LOGGING AND EXITING"
        log_updated_accounts(updatedAccounts, sN=kwargs['sN'], vMN=kwargs['vMN'])
        return 'done'

    ###### update each of the accounts #####
    failedAccounts = [] # in case we fail to update some accounts
    updatedAccounts = [] # to keep track of which accounts we need to log to file!
    lenDF = len(df)
    numIters = 0
    while len(updatedAccounts) != lenDF:
        #### Pro Bono Note: ALWAYS IGNORE DUMMYINDEX. Fuckin pandas always
        #### loads it in to your dataframe if you don't specify columns 
        #### when you read in from csv
        ## If we've run the loop "too many" times, exit out
        if numIters > (2 * lenDF):
            for dummyIndex, index, username, password, sN, vMN in df.itertuples():
                if username not in updatedUsernames:
                    failedAccounts.append((str(username), str(password)))
            logFailedAccounts(failedAccounts, lenDF, logger)
            break

            # used for making sure we don't repeat succesffuly updated accounts
        updatedUsernames = [account[0] for account in updatedAccounts]

        ## Update those accounts baby!
        for dummyIndex, index, username, password, sN, vMN in df.itertuples():

            # don't update the same account twice
            if username in updatedUsernames: 
                continue

            # try to update the account 
            numIters += 1
            try: 
                # print update information
                print "\n--> Iteration {} of {}".format(numIters, 2 * lenDF)
                print "--> Choosing players for account {} of {}. U: {}".format(
                             len(updatedAccounts)+1, lenDF, username)
                print "------> Accounts Done: {0}({1:.2f}%)".format(
                            len(updatedAccounts), 
                            float(len(updatedAccounts))/float(lenDF) * 100)

                # make the appropriate bot and update him
                bot, p1, p2 = (None, None, None) # in case we throw an exception before they get assigned
                bot = Bot(str(username), str(password))
                if sN in (5, 6):
                    p1, p2 = funcDict[sN]['dist_func'](bot, eligiblePlayers)
                elif sN == 7:
                    p1, p2 = funcDict[sN]['dist_func']( bot=bot, 
                                                        eligiblePlayers=eligiblePlayers, 
                                                        doubleDown=True )
            # this should never happen
            except NoPlayerFoundException as e:
                if bot:
                    bot.quit_browser() # closes display as well, if necessary
                raise e

            # sometimes unstable browsers raise exceptions. Just try again
            except Exception as e:
                exc_type = sys.exc_info()[0]
                print "------> Failure: {}".format(exc_type)
                print "------> Logging to file"
                logError( str(username), str(password), p1, p2, e, logger )
                if bot:
                    bot.quit_browser() # closes display as well, if necessary
                continue

            # If it worked, record as much and keep going!
            else:
                print "-----> Success!"
                updatedAccounts.append((username, p1, p2))            

    ## Update the accounts file to reflect the updates
        # we use the dictionary variables instead of the one's we retrieved
        # at the top of the function because sN and vMN take on new values
        # in the while loop
    log_updated_accounts(updatedAccounts, sN=kwargs['sN'], vMN=kwargs['vMN'])

    return 'done'


if __name__ == '__main__':
    """
    Usage:
        1) python chooseplayers.py -sN={strategyNumber} -vMN={virtualMachineNumber}
    """
    import re
    import sys

    from selectfunctions import todaysRecommendedPicks, todaysTopPBatters
    from distributionfunctions import randDownRandPlayers, staticDownRandPlayers

    ## What strategyNumber and virtualMachine Number are we using?
    options = [arg for arg in sys.argv if '-' in arg]

        # Get the strategy number
    sNPattern = re.compile(r"""
        -sN=            # strategy number
        [1-7]           # method number must be in (1, 2, 3, 4, 5)
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

    ## Assign players to accounts in chunks of 50 so that in case something
    ## bad happens, we remain robust
    origCount = get_num_accounts( sN=sN, vMN=vMN, getRemaining=True )
    blockSize = 50
    numLeft = origCount
    funcDict = {
        5: { 'select_func': todaysRecommendedPicks, 
             'dist_func'  : randDownRandPlayers }, 
        6: {'select_func': todaysTopPBatters, 
            'dist_func': randDownRandPlayers }, 
        7: {'select_func': todaysTopPBatters, 
            'dist_func': staticDownRandPlayers }
                }
    doneYet = ''
    while numLeft > 0:
        if doneYet == 'done': # mostly for when there are no eligible players left
            numLeft = 0
            break
        if numLeft < blockSize:
            print "\n****** Assigning to final {} accounts".format(numLeft) + \
                  " for Strategy, VM: {}, {}******".format(sN, vMN)
            doneYet = choosePlayers( funcDict=funcDict, sN=sN, vMN=vMN, num=numLeft)
            break
        else: 
            print "\n********** Assigning IN CHUNKS OF {}".format(blockSize) + \
                  ":.Completed {} of {}".format(origCount-numLeft, origCount) + \
                  " Strategy, VM: {}, {} ***********".format(sN, vMN) 
            doneYet = choosePlayers( funcDict=funcDict, sN=sN, vMN=vMN, num=blockSize)
            numLeft -= blockSize

