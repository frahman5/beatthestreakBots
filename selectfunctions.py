from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import BTSUSERNAME, BTSPASSWORD
from bot import Bot
from exception import NoPlayerFoundException


def todaysRecommendedPicks(today):
    """
    datetime.date int -> listOfTuples
        today: datetime.date | today's date

    Produces a TupleOfTuples where each tuple is of format:
        (firstName, lastName, teamAbbrevations)
        for a player that is on today's "recommended picks" dropdwown
        on the MLB beat the streak player selection page
    """
    bot = Bot(BTSUSERNAME, BTSPASSWORD)
    return bot.get_todays_recommended_players()

def todaysTopPBatters(**kwargs):
    """
    kwargs -> listOfTuples
        P: int | the number of players to return 
        today: datetime.date | today's date 
        filt: Dict | possible entries...
                    -> "minERA": float | exclude all players who are facing a 
                       starting pitcher with an ERA below this number


    Produces a TupleOfTuples where each tuple if of format:
        (firstName, lastName, teamAbbreviations)
        for a player that is among the top P players by batting average
        this season and is starting today. If "minERA" is in kwargs[filter], 
        then only includes players who are facing a starting pitcher with
        ERA >= minERA
    """
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
    assert type(kwargs['today'] == datetime.date)
    if 'filt' in kwargs.keys():
        assert (type(kwargs['filt']) == dict)
        if 'minERA' in kwargs['filt'].keys():
            assert type(kwargs['filt']['minERA'] == float)

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
            # Table of players
        table = browser.find_element_by_tag_name('table')
            # Body of that table
        tablebody = table.find_element_by_tag_name('tbody')
            # rows of that table
        oddRows = tablebody.find_elements_by_class_name('oddrow')
        evenRows = tablebody.find_elements_by_class_name('evenrow')
        allRows = []
        for rowPair in zip( oddRows, evenRows ):
            allRows.extend( rowPair )
            # extract player information from each row
        for index, row in enumerate( allRows ):
            # if we're done, get outta there
            if index == kwargs['p']:
                break
                # row cells 
            cells = row.find_elements_by_tag_name('td')
                # cell[1].text is player's first and last name
            nextPlayer = [ str(name) for name in cells[1].text.split() ]
                # cell[2].text is player's 3DigitTeamAbbrev
            nextPlayer.append( str( cells[2].text.lower() ) )
            players.append( tuple(nextPlayer) )
    except:
        _quit_browser(browser, display, 'get_batters')
        raise

    print "today's top {} players: {}".format(kwargs['p'], str(players))
    # filter out the players who aren't starting and apply any other used
    # requested filters
    players = _whoIsEligibleToday(players, filt=kwargs['filt'], browser=browser)

    ## Close the browser, stop the display if necessary
    _quit_browser(browser, display, 'get_batters')

    return tuple(players)

def _whoIsEligibleToday(players, filt=None, browser=None):
    """
    ListOfTuples None|dict WebDriver -> ListOfTuples:
        players: ListOfTuples | Each tuple is of format
           (firstName, lastName, 3DigitTeamAbbrev)
        filt: dict | key, value pairs are
           typeOfFilter (str), relevantParameter
           e.g: {'minERA': 4.0} filters out players who are playing against
           a starting pitcher with ERA less than 4
        browser: Webdriver | A selenium webdriver to use for finding the
           necessary info

    Filters out all players who aren't starting today, as well as filters
    by any conditions provided in Filt

    Assumes a display is open if necessary
    """
    from datetime import datetime, time, timedelta
        ## type check
    assert type(players) == list
    for thing1, thing2, thing3 in players:
        assert type(thing1) == str
        assert type(thing2) == str
        assert type(thing3) == str
    assert type(filt) == dict

    ## Are we going to filter by minERA?
    if 'minERA' in filt.keys():
        filterERA = True
    else:
        filterERA = False

    today = datetime.today()
    activePlayers = [player for player in players]
    # import pdb
    # pdb.set_trace()
    for player in players:
        firstName, lastName, team = player

        # Go the ESPN clubhouse page
        browser.get(_get_espn_clubhouse_url(team))

        # Get info for the game the team is playing
        nextGameBox = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'current')))
        dateTimeOfNextGame = nextGameBox.find_element_by_tag_name('h4')
        dateTime = str(dateTimeOfNextGame.text)

        # If they aren't playing a game today, remove the player and continue
        print "Game info for {}: {}".format(firstName, dateTime.split())
            #['weekday,', 'month', 'day', 'time', 'AM/PM', 'Timezone']
        weekday, month, day, gameTimeS, timePeriod = dateTime.split()[0:5] 
        weekday = weekday.strip(',') # e.g Fri, -> Fri
        if ( weekday.lower() != today.strftime('%a').lower() ) or \
           ( month.lower() != today.strftime('%b').lower() ) or \
           ( int(day) != today.day):
            activePlayers.remove(player)
            continue

        # If the team is playing, but the game starts in less than 20 minutes 
        # from now, remove the player and continue on
        hour = int(gameTimeS.split(':')[0])
        minute = int(gameTimeS.split(':')[1])
        if timePeriod.lower() == 'pm':
            hour += 12
        gameTimeO = time(hour, minute) 
        twentyMinFromNow = datetime.now() + timedelta(minutes=20)
        if twentyMinFromNow.time() > gameTimeO:
            activePlayers.remove(player)
            continue

        # If the team is playing, but the player's not in the lineup, 
        # remove the player and continue on
        researchBot = Bot(BTSUSERNAME, BTSPASSWORD)
        players = None
        while players is None: # sometimes other errors come up, we need to try again
            try:
                players = researchBot.choose_players(p1=player, p2=())
            except NoPlayerFoundException:
                activePlayers.remove(player)
                break
            except:
                continue
        if player not in activePlayers:
            continue

        # If we're asked to filter by minERA, and the player is playing, 
        # and the opponent's starting pitcher's ERA is too high, 
        # remove the player and continue ons
        researchBot = Bot(BTSUSERNAME, BTSPASSWORD)
        if filt and 'minERA' in filt.keys():
            opERA = researchBot.get_opposing_pitcher_era(p1=player)
            minERA = filt['minERA']
            if opERA < minERA:
                activePlayers.remove(player)

    return activePlayers
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

def _get_espn_clubhouse_url(team):
    """
    str -> str
       team: str | 3 digit abbreviation of team 

    Produces the url of the espn clubhouse page for the given team
    """
    answers = {
        'mia': 'http://espn.go.com/mlb/team/_/name/mia/miami-marlins', 
        'cws': 'http://espn.go.com/mlb/team/_/name/chw/chicago-white-sox', 
        'nyy': 'http://espn.go.com/mlb/team/_/name/nyy/new-york-yankees', 
        'lad': 'http://espn.go.com/mlb/team/_/name/lad/los-angeles-dodgers', 
        'tor': 'http://espn.go.com/mlb/team/_/name/tor/toronto-blue-jays', 
        'phi': 'http://espn.go.com/mlb/team/_/name/phi/philadelphia-phillies',  
        'cle': 'http://espn.go.com/mlb/team/_/name/cle/cleveland-indians', 
        'stl': 'http://espn.go.com/mlb/team/_/name/stl/st-louis-cardinals', 
        'oak': 'http://espn.go.com/mlb/team/_/name/oak/oakland-athletics', 
        'hou': 'http://espn.go.com/mlb/team/_/name/hou/houston-astros',  
        'nym': 'http://espn.go.com/mlb/team/_/name/nym/new-york-mets', 
        'cin': 'http://espn.go.com/mlb/team/_/name/cin/cincinnati-reds', 
        'sd': 'http://espn.go.com/mlb/team/_/name/sdg/san-diego-padres', 
        'tex': 'http://espn.go.com/mlb/team/_/name/tex/texas-rangers', 
        'det': 'http://espn.go.com/mlb/team/_/name/det/detroit-tigers', 
        'sea': 'http://espn.go.com/mlb/team/_/name/sea/seattle-mariners', 
        'sf': 'http://espn.go.com/mlb/team/_/name/sfo/san-francisco-giants',
        'col': 'http://espn.go.com/mlb/team/_/name/col/colorado-rockies', 
        'pit': 'http://espn.go.com/mlb/team/_/name/pit/pittsburgh-pirates', 
        'laa': 'http://espn.go.com/mlb/team/_/name/laa/los-angeles-angels', 
        'wsh': 'http://espn.go.com/mlb/team/_/name/was/washington-nationals', 
        'chc': 'http://espn.go.com/mlb/team/_/name/chc/chicago-cubs', 
        'bos': 'http://espn.go.com/mlb/team/_/name/bos/boston-red-sox', 
        'tb': 'http://espn.go.com/mlb/team/_/name/tam/tampa-bay-rays', 
        'ari': 'http://espn.go.com/mlb/team/_/name/ari/arizona-diamondbacks', 
        'atl': 'http://espn.go.com/mlb/team/_/name/atl/atlanta-braves', 
        'mil': 'http://espn.go.com/mlb/team/_/name/mil/milwaukee-brewers', 
        'min': 'http://espn.go.com/mlb/team/_/name/min/minnesota-twins', 
        'kc': 'http://espn.go.com/mlb/team/_/name/kan/kansas-city-royals', 
        'bal': 'http://espn.go.com/mlb/team/_/name/bal/baltimore-orioles'
    }
    return answers[team]