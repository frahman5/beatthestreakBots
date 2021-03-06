from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import BTSUSERNAME, BTSPASSWORD, ignorePlayers
from bot import Bot
from exception import NoPlayerFoundException

cbsFormattingDict = {
        'mia': 'miami',         'cws': 'chi. white sox', 
        'nyy': 'n.y. yankees',  'lad': 'l.a. dodgers', 
        'tor': 'toronto',       'phi': 'philadelphia', 
        'cle': 'cleveland',     'stl': 'st. louis', 
        'oak': 'oakland',       'hou': 'houston', 
        'nym': 'n.y. mets',     'cin': 'cincinnati', 
        'sd':  'san diego',     'tex': 'texas', 
        'det': 'detroit',       'sea': 'seattle', 
        'sf':  'san francisco', 'col': 'colorado',
        'pit': 'pittsburgh',    'laa': 'l.a. angels', 
        'wsh': 'washington',    'chc': 'chi. cubs',  
        'bos': 'boston',        'tb':  'tampa bay', 
        'ari': 'arizona',       'atl': 'atlanta',  
        'mil': 'milwaukee',     'min': 'minnesota', 
        'kc':  'kansas city',   'bal': 'baltimore'
    }

def getRecommendedPicks(d):
    """
    datetime.date int -> listOfTuples
        today: datetime.date | today's date

    Produces a TupleOfTuples where each tuple is of format:
        (firstName, lastName, teamAbbrevations)
        for a player that is on given date's "recommended picks" dropdwown
        on the MLB beat the streak player selection page
    """
    bot = Bot(BTSUSERNAME, BTSPASSWORD, activeDate=d)
    return bot.get_recommended_players()

def topPBatters(**kwargs):
    """
    kwargs -> listOfTuples
        p: int | the number of players to return 
        activeDate: datetime.date | today's date 
        filt: Dict | possible entries...
                    -> "minERA": float | exclude all players who are facing a 
                       starting pitcher with an ERA below this number


    Produces a TupleOfTuples where each tuple is of format:
        (firstName, lastName, teamAbbreviations)
        for a player that is among the top P players by batting average
        this season and is starting today. If "minERA" is in kwargs[filter], 
        then only includes players who are facing a starting pitcher with
        ERA >= minERA
    """
    print "topPBatters. P, minERA: {}, {}".format(kwargs['p'], kwargs['filt']['minERA'])
    import logging 

    from pyvirtualdisplay import Display
    from datetime import datetime
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    from config import ROOT

    ## type check
    assert type(kwargs['p'] == int)
    if 'filt' in kwargs.keys():
        assert (type(kwargs['filt']) == dict)
        if 'minERA' in kwargs['filt'].keys():
            assert type(kwargs['filt']['minERA'] == float)

    ## Sanity check
    if kwargs['activeDate'] != datetime.today().date():
        today = datetime.today().date()
        print "\nWARNING: As you are selecting on a future date," + \
           " the top batters w.r.t batting average will be from TODAY" + \
           " {} and we will filter out the players who".format(today) + \
           " aren't starting or are facing a pitcher with too high an ERA" + \
           " using the given date {}".format(kwargs['activeDate'])

    ## start a display if necessary, and start the browser
    if ROOT == '/home/faiyamrahman/programming/Python/beatthestreakBots':
        print "--> Starting display to get batters"
        display = Display(visible=0, size=(1024, 768))
        display.start()
    else:
        display = None
    browser = webdriver.Chrome()

    # Create a logger so that we don't get blasted with unnecessary info
    # on every error in a test suite. Instead, we only get high priority shit
    seleniumLogger = logging.getLogger('selenium.webdriver.remote.remote_connection')
    seleniumLogger.setLevel(logging.WARNING) 

    players = []
    # if anything happens and we exit prematurely, quit the browser, then reraise
    try:
        ## Get top P players from espn website
            # get the batting page from espn
        browser.get('http://espn.go.com/mlb/stats/batting')
        for passThrough in ('firstTime', 'secondTime'):

            ## If it's greater than 40 players, click the next page
            if passThrough == 'firstTime':
                indexOffset = 0
            elif passThrough == 'secondTime':
                if kwargs['p'] <= 40: # we don't need a second passthrough!
                    break
                indexOffset = 40
                browser.find_element_by_partial_link_text('NEXT').click()

            # Table of players
            table = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'table')))
            tablebody = table.find_element_by_tag_name('tbody')
            oddRows = tablebody.find_elements_by_class_name('oddrow')
            evenRows = tablebody.find_elements_by_class_name('evenrow')
            allRows = []

            for rowPair in zip( oddRows, evenRows ):
                allRows.extend( rowPair )
                # extract player information from each row
            for index, row in enumerate( allRows ):
                    # row cells 
                cells = row.find_elements_by_tag_name('td')
                    # cell[1].text is player's first and last name
                nextPlayer = [ str(name) for name in cells[1].text.split() ]
                    # cell[2].text is player's 3DigitTeamAbbrev
                team = str( cells[2].text.lower() )
                if team == 'chw': # convert for chicago white sox, to comply with boy.pt
                    team = 'cws'
                if "/" in team:   # if a player was traded, team is oldTeam/newTeam
                    team = team.split('/')[-1]
                    print "CHANGED {} {}'s TEAM!".format(nextPlayer[0], nextPlayer[1])
                nextPlayer.append( team )
                players.append( tuple(nextPlayer) )

                    # if we're done, get outta there
                if (index + indexOffset + 1) == kwargs['p']:
                    break

        print "today's top {} players before weeding:".format(kwargs['p'])
        for index, player in enumerate(players):
            print "    -->{}: {}".format(index + 1, player)
        # filter out the players who aren't starting and apply any other used
        # requested filters
        players = _whoIsEligible( players=players, 
                                  activeDate=kwargs['activeDate'], 
                                  filt=kwargs['filt'], 
                                  browser=browser)
    except:
        _quit_browser(browser, display, 'get_batters')
        raise

    ## Close the browser, stop the display if necessary
    _quit_browser(browser, display, 'get_batters')

    return tuple(players)

def _whoIsEligible(**kwargs):
    """
    kwargs -> ListOfTuples:
        players: ListOfTuples | Each tuple is of format
           (firstName, lastName, 3DigitTeamAbbrev)
        activeDate: datetime.date | date for which we are retrieving eligibility
        filt: dict | key, value pairs are
           typeOfFilter (str), relevantParameter
           e.g: {'minERA': 4.0} filters out players who are playing against
           a starting pitcher with ERA less than 4
        browser: Webdriver | A selenium webdriver to use for finding the
           necessary info

    Filters out all players who aren't starting on activeDate, as well as filters
    by any conditions provided in Filt. Can only handle activeDates that are <= 
    2 days from now. E.g if today is the 8th, can hanlde the 8th, 9th, and 10th

    Assumes a display is open if necessary
    """
    import time as timetime
    from datetime import datetime, time, timedelta
    from pytz import timezone

    ## type check
    assert type(kwargs['players']) == list
    for thing1, thing2, thing3 in kwargs['players']:
        assert type(thing1) == str
        assert type(thing2) == str
        assert type(thing3) == str
    assert type(kwargs['filt']) == dict
 

    ## Are we going to filter by minERA?
    if 'minERA' in kwargs['filt'].keys():
        filterERA = True
    else:
        filterERA = False

    ## Get scheduling info for today
    browser = kwargs['browser']
        ## Get the html document with schedule tables
    browser.get('http://www.cbssports.com/mlb/schedules')
    iFrames = browser.find_elements_by_tag_name('iframe')
    for frame in iFrames:
        if 'schedule' in frame.get_attribute('src'):
            browser.switch_to_frame(frame)
            break

        ## Get the schedule table for activeDate
    waitForTable = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'table')))
    timetime.sleep(3) # to let tables load
    tables = browser.find_elements_by_tag_name('table')
    activeTable = None
    for table in tables:
        tableDate = _datify(
                       str(table.find_element_by_class_name('title').text) )
        if tableDate == kwargs['activeDate']:
            activeTable = table
            break
    assert activeTable is not None

        ## See if player's team is playing. Get opposing ERA
            # dict structures: 'teamName': opposing pitcher's ERA
    awayTeams = {}
    homeTeams = {}
    for row in activeTable.find_elements_by_tag_name('tr'):
        if "row" in row.get_attribute('class'): # game row
            ## Get relevant variables
            firstCell = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'td')))
            cells = row.find_elements_by_tag_name('td')
            awayTeam = str(cells[0].text).lower()
            homeTeam = str(cells[1].text).lower()
            time = _timify(str(cells[2].text))
            if 'ERA' not in str(cells[3].text):
                print "WARNING: {} pitcher unannounced".format(awayTeam)
                awayERA = 0.0
            else:
                awayERA = float(cells[3].text.split()[-2])
            if 'ERA' not in str(cells[4].text):
                print "WARNING: {} pitcher unannounced".format(homeTeam)
                homeERA = 0.0
            else:
                homeERA = float(cells[4].text.split()[-2])
            awayTeams[awayTeam] = (time, homeERA)
            homeTeams[homeTeam] = (time, awayERA) 

    ## Sanity/coding check
    allTeams = []
    allTeams.extend(awayTeams.keys())
    allTeams.extend(homeTeams.keys())
    for team in allTeams:
        if team not in cbsFormattingDict.values():
            raise ValueError("{} not in cvsFormattingDict".format(team))
            

    ## remove ineligible players
       # we make two copies because if you alter a list as you iterate through it,
       # things get messed up!
    global ignorePlayers                        # global list of players to remove
    activePlayersIter = [ player for player in kwargs['players'] ]
    activePlayersReturn = [ player for player in kwargs['players'] ]
    filt = kwargs['filt']
    for player in activePlayersIter:
        firstName, lastName, team = player
        teamFormatted = _formatTeam(team)
        now = datetime.now(timezone('US/Eastern'))
        today = now.date()
        twentyMinFromNow = (now + timedelta(minutes=20)).time()
        # today = datetime.today().date()
        # twentyMinFromNow = (datetime.now(timezone('US/Eastern')) + timedelta(minutes=20)).time()
        print "Today: {}".format(today)
        print "Twenty Min From Now: {}".format(twentyMinFromNow)

        # is the player's team playing
        if teamFormatted in awayTeams.keys():
            relevantTeams = awayTeams
        elif teamFormatted in homeTeams.keys():
            relevantTeams = homeTeams
        else:
            activePlayersReturn.remove(player)
            continue

        # Player's team is playing... is the game locked?
        if today == kwargs['activeDate'] and \
              relevantTeams[teamFormatted][0] < twentyMinFromNow:
             activePlayersReturn.remove(player)
             continue

        # Player's team is playing... is the opposing pitcher ERA high enough?
        elif filterERA and (relevantTeams[teamFormatted][1] <= filt['minERA']):
            activePlayersReturn.remove(player)
            continue

        # Player's team is playing, opposing pitcher ERA high enough, 
        # but they've caused too many NoPlayerFOundExceptions
        if player in ignorePlayers:
            activePlayersReturn.remove(player)

    return activePlayersReturn

def _timify(timeString):
    """
    string -> datetime.time
        timeString | time expressed in format e.g '7:05 pm'

    returns a datetime.time object that encodes the given time
    """
    import datetime
 
    time, ampm = timeString.split()
    hour, minute = time.split(':')
    hour = int(hour)
    minute = int(minute)
    if ampm == 'pm':
        if hour != 12:
            hour += 12

    return datetime.time(hour=hour, minute=minute)
    
    
def _formatTeam(teamString):
    """
    string -> string
       teamString: string | 3 digit team abbrevation, compliant with self.teams
       in bot.py

    Returns the team, formatted to comply with the way cbssports writes
    team names on their schedule page
    """
    from bot import Bot
    #print "teamString: {}".format(teamString)
    assert teamString in Bot.teams

    return cbsFormattingDict[teamString]
def _quit_browser(browser, display, funcName):
    """
    webdriver None|Display string -> None

    Closes the browser, stops the display if necessary, and prints to 
    stdout to let the user know
    """
    browser.quit()
    if display:
        print "--> Stopping display for {}".format(funcName)
        display.stop()

def _datify(dateString):
    """
    string -> datetime.date
        dateString: string | a string that writes out a date in format
           Month date, year (e.g JULY 15, 2014)

    Converts the english-formatted date string to a datetime.date object
    and returns it 

    Only works for july through november
    """
    from datetime import date

    ## Extract variables
    month, day, year = dateString.split()
    month = month.lower()
    day = int(day.replace(',', ''))
    year = int(year)

    ## make the date and return it
    monthDict = { 'july': 7, 'august': 8, 'september': 9, 
                  'october': 10, 'november': 11 }
    return date(year, monthDict[month], day)
