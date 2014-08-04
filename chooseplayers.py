import pandas as pd  # excel spreadsheet manipulation

from types import FunctionType # to type check function inputs that we expect to be functions
from datetime import datetime, timedelta, date # to get today's date

from filepath import Filepath 
from bot import Bot
from config import ROOT, ignorePlayers, logEligiblePlayers, playerExceptions
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

    ### Read in the minion accounts file if available
    minionPath = Filepath.get_minion_account_file(
                     sN=kwargs['sN'], vMN=kwargs['vMN'])
    if os.path.isfile(minionPath):
        dfPath = minionPath
    ### Otherwise get the master file
    else:
        dfPath = Filepath.get_accounts_file()
    df = pd.read_excel( dfPath, sheetname='Production' )

    ### Let the user know what's up
    print "--> Getting accounts file {}".format(dfPath)

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

    ### Get the tuple of players
    print "--> Getting {}'s eligible players".format(kwargs['activeDate'])
    selectionFunction = kwargs['funcDict'][kwargs['sN']]['select_func']
    if sN == 5:
        eligiblePlayers = selectionFunction(kwargs['activeDate'])
    elif sN in (6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17):
        # Choose a pVal depending on the strategy
        if sN in (6, 7, 8, 9, 10, 11):
            pVal = 40
        elif sN in (12, 13, 14, 15, 16, 17):
            pVal = 80

        # Choose a minERAVal depending on the strategy
        if sN in (6, 7, 8, 12, 13, 14):
            minERAVal = 4.0
        elif sN in (9, 10, 11, 15, 16, 17):
            minERAVal = 5.0

        # Select the players
        eligiblePlayers = selectionFunction( p=pVal, 
                                             activeDate=kwargs['activeDate'],
                                             filt={'minERA': minERAVal})


    ### Let the user know what's up
    if sN !=5:
        print "today's top {} players after weeding:".format(pVal)
        for index, player in enumerate(eligiblePlayers):
            print "    -->{}: {}".format(index + 1, player)
    if sN ==5:
        print "Today's eligible Players: {}".format(eligiblePlayers)

    ### Return it
    return eligiblePlayers

def __report_no_more_selections(**kwargs):
    """
    kwargs -> None
        fulldf: pd.DataFrame | dataframe containing all the as-of-yet unhandled
           accounts for sN and vMN
        sN: int | strategy Number
        vMN: int | virtual machine number  
        activeDate: date | activeDate

    Assuming there are no more available selections today, puts the value
    "DONE: NOELIGIBLE, NOELIGIBLE" in todays column of the minion account file
    for strategy sN and virtualMachineNumber vMN
    """
    ### Type check
    assert type(kwargs['fulldf']) == pd.DataFrame
    assert type(kwargs['sN']) == int
    assert type(kwargs['vMN']) == int
    assert type(kwargs['activeDate']) == date

    ### Let the user know what's up
    print "--> NO PLAYERS LEFT TODAY. LOGGING AND EXITING"

    ### Log the finished accounts
    updatedAccounts = [ (username, ('NOELIGIBLE'), ('NOELIGIBLE')) for 
                          dummyIndex, index, username, password, sN, vMN in 
                          kwargs['fulldf'].itertuples() ]
    log_updated_accounts( updatedAccounts, sN=kwargs['sN'], 
                          vMN=kwargs['vMN'], activeDate=kwargs['activeDate'])

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
    if kwargs['sN'] in (5, 6, 9, 12, 15): # Random Double Down choices
        p1, p2 = distributionFunction( bot=kwargs['bot'], 
                                       eligiblePlayers=kwargs['eligiblePlayers'])
    elif kwargs['sN'] in (7, 10, 13, 16): # Double Down every time
        p1, p2 = distributionFunction( bot=kwargs['bot'], 
                                       eligiblePlayers=kwargs['eligiblePlayers'],
                                       doubleDown=True )
    elif kwargs['sN'] in (8, 11, 14, 17): # Single Down every time
        p1, p2 = distributionFunction( bot=kwargs['bot'], 
                                       eligiblePlayers=kwargs['eligiblePlayers'],
                                       doubleDown=False )

    return p1, p2

def get_num_accounts(sN=None, vMN=None, getRemaining=True, activeDate=None):
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
    day = __get_date_formatted_for_excel(activeDate)
    minionPath = Filepath.get_minion_account_file(sN=sN, vMN=vMN)

    ## If the minion account File exists, get it
    if os.path.isfile(minionPath):
        minionDF = pd.read_excel( minionPath, 
                                  sheetname="Production")
        # If appropriate, parse out all accounts that have already been handled
        if getRemaining and (day in minionDF.columns): 
            # pd.isnull checks for NaNs
            minionDF = minionDF[pd.isnull(minionDF[day])]

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

def reportUnusedPlayers(sN, vMN, activeDate):
    """
    int int -> None
    Comapares the global list "eligiblePlayers" to the listed players
    in the minion Account file for sN and vMN and logs player selection 
    rates to the log file

    For example, if eligiblePlayers = (p1, p2, p3) and 3 accounts chose p1, 
    5 accounts chose p2 and 0 accounts chose p3, then it will write:

    **** Player Selection Rates ****
    p2: 5
    p1: 3
    p3: 0
    """
    global logEligiblePlayers
    global ignorePlayers
    global playerExceptions

    ### Read in the minion accounts file
    minionPath = Filepath.get_minion_account_file(sN=sN, vMN=vMN)
    df = pd.read_excel( minionPath, sheetname='Production' )

        ### Let the user know what's up
    print "--> Reporting Player selection rates for {}".format(minionPath)

    ### Only include column with today's selections
    df = df[__get_date_formatted_for_excel(activeDate)]

    ### Compare to eligible players and construct selection counts
    playerCounts = {}
    for player in logEligiblePlayers:
        playerCounts[player] = 0
    for selection in df:
        for player in logEligiblePlayers:
            if str(player) in selection:
                playerCounts[player] += 1

    ### Organize the player counts
    sortedPlayerCounts = []
    for player, count in playerCounts.iteritems():
        sortedPlayerCounts.append((player, count))
    sortedPlayerCounts.sort(key=lambda x: x[1])

    ### Log counts to file
    logger = getLogger(activeDate=activeDate, sN=sN, vMN=vMN)

    ### Tell us what values the global variables had
    logger.info("\n\n**** logEligiblePlayers ****\n" + str(logEligiblePlayers))
    logger.info("\n\n**** ignorePlayers ****\n" + str(ignorePlayers))
    logger.info("\n\n**** playerExceptions ****\n" + str(playerExceptions))

    info = "\n\n**** Player Selection Rates ****\n"
    for player, count in sortedPlayerCounts:
        info = info + "\n --->{}: {}".format(player, count)
    logger.info(info)

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
    import subprocess   

    global logEligiblePlayers                       # to log player selection rates
    global ignorePlayers
    
    ###### Get our arguments: #####
    funcDict = kwargs['funcDict']
    sN = kwargs['sN']
    vMN = kwargs['vMN']
    num = kwargs['num']
    activeDate = kwargs['activeDate']

    ###### get an error logger #####
    print "\n--> Creating Error Logger"
    logger = getLogger(kwargs['activeDate'], kwargs['sN'], kwargs['vMN'])

    ##### get list of accounts you need #####
    df, fulldf = __get_dataframes_for_choose_players( 
                     sN=sN, vMN=vMN, num=num, activeDate=activeDate)
    
    ##### Get today's eligible players #### 
    eligiblePlayers = None
    while eligiblePlayers is None:
        # wrap it in a try-except because sometimes the websites don't load
        # and we need to try again
        try: 
            eligiblePlayers = __get_eligible_players( activeDate=activeDate, 
                                                      funcDict = funcDict, 
                                                      sN=sN )
        except Exception as e:
            logger.error(e)

    if len(ignorePlayers) == 0:                     # for player selection rate logging
        logEligiblePlayers = [player for player in eligiblePlayers]


    if len(eligiblePlayers) == 0: # report as much and exit gracefully
        __report_no_more_selections( fulldf=fulldf, 
                                     sN=kwargs['sN'], 
                                     vMN=kwargs['vMN'],
                                     activeDate=kwargs['activeDate'] )
        return 'noneLeft'

    ###### update each of the accounts #####
    numIters = 0          # if we iterate too many times, exit gracefully
    lenDF = len(df)       # for keeping track of how much we have left
    failedAccounts = []   # in case we fail to update some accounts
    updatedAccounts = []  # to keep track accounts to log to file
    while len(updatedAccounts) != lenDF:

        ## Who have we already updated?
        updatedUsernames = [ account[0] for account in updatedAccounts]

        ## If we've run the loop "too many" times, exit out
        if numIters > (2 * lenDF):
            logFailedAccounts( df=df, updatedUsernames=updatedUsernames, 
                               logger=logger )
            break

        ## Update those accounts baby! 
        for dummyIndex, index, username, password, sN, vMN in df.itertuples():

            # log ps -A, for debugging purposes
            # with open( Filepath.get_log_file(kwargs['activeDate'], 
            #            kwargs['sN'], kwargs['vMN']), "a") as f:
            #     f.write('\n\n\n')
            #     f.write('ITER: {} with u, p: {}, {}\n'.format(
            #                 numIters, username, password))
            #     f.write('TIME: {}\n'.format(datetime.now().time()))
            #     f.flush()
            #     subprocess.call(['ps', '-A'], stdout=f)

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

            # this should never happen. We now allow it to happen, because
            # of ('Yadier', 'Molina', 'stl') on 07-18-2014. He is a catcher
            #, and catchers get days off man!. We have to trust that our code
            # isn't accidentally overlooking dudes
            # except NoPlayerFoundException as e:
            #     logError( str(username), str(password), p1, p2, e, logger)
            #     if bot:
            #         bot.quit_browser() # closes display as well, if necessary
            #     raise

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
    from pytz import timezone

    ## What strategyNumber virtualMachineNumber, and date are we using?
    options = [arg for arg in sys.argv if '-' in arg]

        # Get the strategy number
    sNPattern = re.compile(r"""
        -sN=            # strategy number
        [1-9]           # 1 digit in 1-9
        [0-7]?          # 0 or 1 digits in (0,1,2,3,4,5,6,7)
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
    activeDate = datetime.now(timezone('US/Eastern')).date() + timedelta(days=dateNUM)

    ## Check that we didn't get any bogus options:
    if len(options) != 0:
        raise KeyError("Invalid options: " + str(options))

    ## Assign players to accounts in chunks of 50 so that in case something
    ## bad happens, we finish as many players as possible
    doneYet = ''
    blockSize = 20
    origCount = get_num_accounts( 
                  sN=sN, vMN=vMN, getRemaining=True, activeDate=activeDate )
    if origCount == 0:
        print "We already done playboy!"
    numLeft = origCount
    funcDict = {
        5:  { 'select_func': getRecommendedPicks, 
              'dist_func'  : randDownRandPlayers }, 
        6:  { 'select_func': topPBatters, 
              'dist_func'  : randDownRandPlayers }, 
        7:  { 'select_func': topPBatters, 
              'dist_func'  : staticDownRandPlayers }, 
        8:  { 'select_func': topPBatters,
              'dist_func'  : staticDownRandPlayers }, 
        9:  { 'select_func': topPBatters, 
              'dist_func'  : randDownRandPlayers },
        10: { 'select_func': topPBatters, 
              'dist_func'  : staticDownRandPlayers},
        11: { 'select_func': topPBatters, 
              'dist_func'  : staticDownRandPlayers},
        12: { 'select_func': topPBatters, 
              'dist_func'  : randDownRandPlayers },
        13: { 'select_func': topPBatters, 
              'dist_func'  : staticDownRandPlayers},
        14: { 'select_func': topPBatters, 
              'dist_func'  : staticDownRandPlayers},
        15: { 'select_func': topPBatters, 
              'dist_func'  : randDownRandPlayers},
        16: { 'select_func': topPBatters, 
              'dist_func'  : staticDownRandPlayers},
        17: { 'select_func': topPBatters, 
              'dist_func'  : staticDownRandPlayers}
                }    
    while numLeft > 0:
        if doneYet == 'noneLeft': # if there are no eligible players left
            numLeft = 0
            break
        else: 
            assert type(sN) == int
            print "\n********** Assigning IN CHUNKS OF {}".format(blockSize) + \
                  ":.Completed {} of {}".format(origCount-numLeft, origCount) + \
                  " Strategy, VM: {}, {} ***********".format(sN, vMN) 
            doneYet = choosePlayers( funcDict=funcDict, sN=sN, vMN=vMN, 
                                     num=blockSize, activeDate=activeDate)
            numLeft = get_num_accounts( 
                             sN=sN, vMN=vMN, 
                             getRemaining=True, activeDate=activeDate )

    reportUnusedPlayers(sN=sN, vMN=vMN, activeDate=activeDate)

