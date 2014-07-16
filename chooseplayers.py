import pandas as pd  # excel spreadsheet manipulation

from types import FunctionType # to type check function inputs that we expect to be functions
from datetime import datetime, timedelta, date # to get today's date

from filepath import Filepath 
from bot import Bot
from config import ROOT
from exception import NoPlayerFoundException, FailedAccountException, \
                      FailedUpdateException
from errorlogging import getLogger, logError, logFailedAccounts

def __get_date_formatted_for_excel(d):
    """
    datetime.date -> string
       d: datetime.date | date of interest

    Produces the date of interest in month-day format. e.g july 7th -> 7-7
    """
    return str(d.month) +  '-' + str(d.day)

def __get_dataframes_for_choose_players(**kwargs):
    """
    kwargs -> pd.DataFrame
        sN: int | Strategy Number 
        vMN: int | Virtual Machine Number
        num: int | number of unhandled accounts to return
        activeDate: datetime.date | date for which we should parse the dataframe

    Returns two pandas dataframes. One holds num of the unhandled accounts
    corresponding to strategy sN and virtual machine vMN. The second holds
    all unhandled accounts corresponding to strategy sN and virtual machine vMN
    """
    import os 

    ### Type check
    assert type(kwargs['sN']) == int
    assert type(kwargs['vMN']) == int
    assert type(kwargs['num']) == int
    assert type(kwargs['activeDate']) == date

    ### Let the user know what's up
    print "--> Getting accounts file {}".format(Filepath.get_accounts_file())

    ### Read in the minion accounts file if available
    minionPath = Filepath.get_minion_account_file(
                     sN=kwargs['sN'], vMN=kwargs['vMN'])
    if os.path.isfile(minionPath):
        dfPath = minionPath
    ### Otherwise get the master file
    else:
        dfPath = Filepath.get_accounts_file()
    df = pd.read_excel( dfPath, sheetname='Production' )

    ### Parse it down to include only what we want
        # If it's the master accounts file, only include 
        # those accounts with this strategy number and virtual machine number
    if dfPath != minionPath:
        df = df[df.Strategy == kwargs['sN']][df.VM == kwargs['vMN']]

        # Only include those accounts that haven't yet been updated
    dateFormatted = __get_date_formatted_for_excel(activeDate)
    if dateFormatted in df.columns:
        df = df[pd.isnull(df[dateFormatted])] # pd.isnull checks for NaNs (unhandled accounts)

        # Only include the columns we want
    df = df[['ID', 'Email', 'MLBPassword', 'Strategy', 'VM']]

    return df[0:kwargs['num']], df

def __get_eligible_players(**kwargs):
    """
    kwargs -> tupleOfTuples
        activeDate: datetime.date | date of interest
        funcDict: dict | dictionary with key, value pairs:
             key: int
             value: {'select_func': function, 
                     'dist_func': function }
        sN: int | strategy number

    Returns the players eligible for distribution to accounts on date d, using
    the selection function stored in funcDict[sN]['select_func']
    """
    ### Type check
    assert type(kwargs['sN']) == int
    assert type(kwargs['activeDate']) == date
    assert type(kwargs['funcDict']) == dict

    ### Variable assignments
    pVal = 20 # Number of top players to return for strats 6 and 7
    minERAVal = 4.0 # Minimum ERA op pitcher must have for strats 6 and 7

    ### Get the tuple of players
    print "--> Getting {}'s eligible players".format(kwargs['activeDate'])
    selectionFunction = kwargs['funcDict'][kwargs['sN']]['select_func']
    if sN == 5:
        eligiblePlayers = selectionFunction(kwargs['activeDate'])
    elif sN in (6, 7):
        eligiblePlayers = selectionFunction(p=pVal, 
                                            activeDate=kwargs['activeDate'],
                                            filt={'minERA': minERAVal})

    ### Let the user know what's up
    print "--> Today's eligible Players: "
    for player in eligiblePlayers:
        print "          " + str(player)

    ### Return it
    return eligiblePlayers

def __report_no_more_selections(**kwargs):
    """
    kwargs -> None
        fulldf: pd.DataFrame | dataframe containing all the as-of-yet unhandled
           accounts for sN and vMN
        sN: int | strategy Number
        vMN: int | virtual machine number  

    Assuming there are no more available selections today, puts the value
    "DONE: NOELIGIBLE, NOELIGIBLE" in todays column of the minion account file
    for strategy sN and virtualMachineNumber vMN
    """
    ### Type check
    assert type(kwargs['fulldf']) == pd.DataFrame
    assert type(kwargs['sN']) == int
    assert type(kwargs['vMN']) == int

    ### Let the user know what's up
    print "--> NO PLAYERS LEFT TODAY. LOGGING AND EXITING"

    ### Log the finished accounts
    updatedAccounts = [ (username, ('NOELIGIBLE'), ('NOELIGIBLE')) for 
                          dummyIndex, index, username, password, sN, vMN in 
                          fulldf.itertuples() ]
    log_updated_accounts(updatedAccounts, sN=kwargs['sN'], vMN=kwargs['vMN'])

def __distribute_eligible_players(**kwargs):
    """
    kwargs -> TuplesOfStrings TuplesOfStrings
        funcDict: dict | dictionary with key, value pairs:
             key: int
             value: {'select_func': function, 
                     'dist_func': function }
        bot: Bot | bot to which we are distributing players
        sN: int | strategy number
        eligiblePlayers: tupleOfTupleOfStrings | players to be distributed
        activeDate: datetime.date | date for which we are to select players
    """
    ### Type check
    assert type(kwargs['funcDict']) == dict
    assert type(kwargs['bot']) == Bot
    assert type(kwargs['sN']) == int
    assert type(kwargs['eligiblePlayers']) == tuple

    ## Distribute the players
    distributionFunction = funcDict[kwargs['sN']]['dist_func']
    if kwargs['sN'] in (5, 6):
        p1, p2 = distributionFunction( bot=kwargs['bot'], 
                                       eligiblePlayers=kwargs['eligiblePlayers'])
    elif sN == 7:
        p1, p2 = distributionFunction( bot=kwargs['bot'], 
                                       eligiblePlayers=kwargs['eligiblePlayers'],
                                       doubleDown=True )

    return p1, p2

def get_num_accounts(sN=None, vMN=None, getRemaining=True):
    """
    int int bool -> int 
       sN: Strategy Number
       vMN: virtual Machine Number
       remaining: Indicates whether or not to count a player iff he hasn't
           already been assigned to today.

    Returns the number of accounts correspodning to strategy number sN
    and virtual machine vMN. If required==True, then only returns the number
    of accounts that have yet to be assigned to
    """
    import os

    ## Type check
    assert type(sN) == int
    assert type(vMN) == int
    assert type(getRemaining) == bool

    ## Assign initial variables
    today = __get_date_formatted_for_excel(datetime.today())
    minionPath = Filepath.get_minion_account_file(sN=sN, vMN=vMN)

    ## If the minion account File exists, get it
    if os.path.isfile(minionPath):
        minionDF = pd.read_excel( minionPath, 
                                  sheetname="Production")
        # If appropriate, parse out all accounts that have already been handled
        if getRemaining and (today in minionDF.columns): 
            # pd.isnull checks for NaNs
            minionDF = minionDF[pd.isnull(minionDF[today])]

    ## Otherwise get the accounts from the master accounts file
    else:    
        fullDF = pd.read_excel( Filepath.get_accounts_file(), 
                                sheetname='Production',
                                parse_cols= 'A:F' )
        minionDF = fullDF[fullDF.Strategy == sN][fullDF.VM == vMN]

    ## return the length of the dataframe
    return len(minionDF)

def log_updated_accounts(updatedAccounts, sN=None, vMN=None, activeDate=None):
    """
    ListOfTuples -> None
       updatedAccounts: ListOfTuples | A list of the accounts that were
            updated in the choosePlayers function. Format: 
                (username, p1, p2) 
            where p2 and p2 are TuplesOfStrings of format 
                (firstName, lastName, teamAbbreviation)
        sN: int | "strategy number" (see strategyNumber.txt)
        vMN: int | virtual Machine Number.

    Writes info about updated accounts to minion account files
    """
    import os

    ## type check
    assert type(updatedAccounts) == list
    assert type(sN) == int
    assert type(vMN) == int
    assert type(activeDate) == date

    ## Let the user know which account file we are updating
    minionAF = Filepath.get_minion_account_file(sN=sN, vMN=vMN)
    print "--> Updating accounts file: {}".format(minionAF)

    ## If the minion spreadsheet hasn't been initalized yet, do so
    if not os.path.isfile(minionAF): 
        fullDF = pd.read_excel( Filepath.get_accounts_file(), 
                                sheetname='Production',
                                parse_cols= 'A:F' )
        minionDF = fullDF[fullDF.Strategy == sN][fullDF.VM == vMN]
        minionDF.to_excel( minionAF, 
                           sheet_name='Production', 
                           index=False # no extra column of row indices  
                         ) 

    ## Get the minion spreadsheet corresponding to this sN and vMN
    dateFormatted = __get_date_formatted_for_excel(activeDate)
    minionDF = pd.read_excel( minionAF, 
                              sheetname='Production' )

    ## Create the series corresponding to today's player selections
    if dateFormatted in minionDF.columns: 
        accountInfoL = list(minionDF[dateFormatted])
        del minionDF[dateFormatted]
    else:
        accountInfoL = ['' for i in range(len(minionDF))]
    for account in updatedAccounts:
        accountIndex = minionDF.Email[ minionDF.Email == \
                                       account[0]].index[0]
        accountInfoL[accountIndex] = 'Done. 1: {}, 2: {}'.format(
                                         account[1], account[2])

    ## Put the dataframe together and print it to file
    newDF = pd.concat( [minionDF, 
                        pd.Series(accountInfoL, name=dateFormatted)], 
                        axis=1)
    newDF.to_excel( minionAF, 
                    sheet_name='Production', 
                    index=False # no extra column for row indices
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
        activeDate(REQUIRED): datetime.date  Indicates for which day we are 
           assigning players

    Reads in the accounts from Filepath.get_accounts_file() that correspond
    to sN, vMN, and then updates num of those accounts accordingly

    Returns 'noneLeft' if no players are eligible anymore
    """
    import os

    ###### Get our arguments: #####
    funcDict = kwargs['funcDict']
    sN = kwargs['sN']
    vMN = kwargs['vMN']
    num = kwargs['num']
    activeDate = kwargs['activeDate']

    ###### get an error logger #####
    print "\n--> Creating Error Logger"
    logger = getLogger()

    ##### get list of accounts you need #####
    df, fulldf = __get_dataframes_for_choose_players( 
                     sN=sN, vMN=vMN, num=num, activeDate=activeDate)
    
    ##### Get today's eligible players #### 
    eligiblePlayers = __get_eligible_players( activeDate=activeDate, 
                                              funcDict = funcDict, 
                                              sN=sN )
    if len(eligiblePlayers) == 0: # report as much and exit gracefully
        __report_no_more_selections( fulldf=fulldf, 
                                     sN=kwargs['sN'], 
                                     vMN=kwargs['vMN'] )
        return 'noneLeft'

    ###### update each of the accounts #####
    numIters = 0          # if we iterate too many times, exit gracefully
    lenDF = len(df)       # for keeping track of how much we have left
    failedAccounts = []   # in case we fail to update some accounts
    updatedAccounts = []  # to keep track accounts to log to file
    while len(updatedAccounts) != lenDF:

        ## If we've run the loop "too many" times, exit out
        if numIters > (2 * lenDF):
            logFailedAccounts( df=df, updatedUsernames=updatedUsernames, 
                               logger=logger )
            break

        ## Update those accounts baby!
        updatedUsernames = [ account[0] for account in updatedAccounts] 
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
                bot = Bot(str(username), str(password), activeDate)
                p1, p2 = __distribute_eligible_players( 
                    funcDict=funcDict, bot=bot, sN=kwargs['sN'],
                    eligiblePlayers=eligiblePlayers)

            # this should never happen
            except NoPlayerFoundException as e:
                logError( str(username), str(password), p1, p2, e, logger)
                if bot:
                    bot.quit_browser() # closes display as well, if necessary
                raise

            # if the user interferes, exit
            except KeyboardInterrupt:
                if bot:
                    bot.quit_browser() # closes display as well, if necessary
                raise

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
    log_updated_accounts( updatedAccounts, sN=kwargs['sN'], 
                          vMN=kwargs['vMN'], activeDate=kwargs['activeDate'] )

if __name__ == '__main__':
    """
    Usage:
        1) python chooseplayers.py -sN={strategyNumber} -vMN={virtualMachineNumber}
    """
    import re
    import sys

    from selectfunctions import getRecommendedPicks, topPBatters
    from distributionfunctions import randDownRandPlayers, staticDownRandPlayers

    ## What strategyNumber virtualMachineNumber, and date are we using?
    options = [arg for arg in sys.argv if '-' in arg]

        # Get the strategy number
    sNPattern = re.compile(r"""
        -sN=            # strategy number
        [1-7]           # method number must be in (1, 2, 3, 4, 5)
        """, re.VERBOSE)
    matches = [ sNPattern.match(option) for option in options if 
                    sNPattern.match(option) ]
    assert len(matches) == 1
    sN = int(matches[0].string[4:])
    options.remove(matches[0].string)

        # Get the virtualMachine Number
    vMNPattern = re.compile(r"""
        -vMN=            # virtual machine number
        [1-9]            # first digit must be nonzero
        [0-9]*           # arbitrary number of digits
        """, re.VERBOSE)
    matches = [ vMNPattern.match(option) for option in options if 
                    vMNPattern.match(option)]
    assert len(matches) == 1
    vMN = int(matches[0].string[5:])
    options.remove(matches[0].string)

         # Get the date
    datePattern = re.compile(r"""
        -d=             # date "number"
        [0-5]           # digit must be 0-5)
        """, re.VERBOSE)
    matches = [ datePattern.match(option) for option in options if 
                   datePattern.match(option) ]
    assert len(matches) == 1
    dateNUM = int(matches[0].string[3:])
    options.remove(matches[0].string)
       # e.g if dateNum == 4, activeDate is four days from now
    activeDate = datetime.today().date() + timedelta(days=dateNUM)

    ## Check that we didn't get any bogus options:
    if len(options) != 0:
        raise KeyError("Invalid options: " + str(options))

    ## Assign players to accounts in chunks of 50 so that in case something
    ## bad happens, we finish as many players as possible
    doneYet = ''
    blockSize = 20
    origCount = get_num_accounts( 
                  sN=sN, vMN=vMN, getRemaining=True )
    numLeft = origCount
    funcDict = {
        5: { 'select_func': getRecommendedPicks, 
             'dist_func'  : randDownRandPlayers }, 
        6: {'select_func': topPBatters, 
            'dist_func': randDownRandPlayers }, 
        7: {'select_func': topPBatters, 
            'dist_func': staticDownRandPlayers }
                }    
    while numLeft > 0:
        if doneYet == 'noneLeft': # if there are no eligible players left
            numLeft = 0
            break
        if numLeft < blockSize:
            print "\n****** Assigning to final {} accounts".format(numLeft) + \
                  " for Strategy, VM: {}, {}******".format(sN, vMN)
            doneYet = choosePlayers( funcDict=funcDict, sN=sN, vMN=vMN, 
                                     num=numLeft, activeDate=activeDate)
            break
        else: 
            assert type(sN) == int
            print "\n********** Assigning IN CHUNKS OF {}".format(blockSize) + \
                  ":.Completed {} of {}".format(origCount-numLeft, origCount) + \
                  " Strategy, VM: {}, {} ***********".format(sN, vMN) 
            doneYet = choosePlayers( funcDict=funcDict, sN=sN, vMN=vMN, 
                                     num=blockSize, activeDate=activeDate)
            numLeft -= blockSize

