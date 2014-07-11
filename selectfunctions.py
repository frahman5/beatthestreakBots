from config import BTSUSERNAME, BTSPASSWORD
from bot import Bot

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
            assert type(filt['minERA'] == float)

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

    # filter out the players who aren't starting and apply any other used
    # requested filters
    players = _whoIsEligibleToday(players, filt=kwargs['filt'], browser=browser)

    ## Close the browser, stop the display if necessary
    _quit_browser(browser, display, 'get_batters')

    print tuple(players)
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
    assert type(browser) == WebDriver

    ## Are we going to filter by minERA?
    if 'minERA' in filt.keys():
        filterERA = True
    else:
        filterERA = False

    today = datetime.today()
    activePlayers = [player for player in players]
    for player in players:
        firstName, lastName, team = player

        # Go the ESPN clubhouse page
        browser.get(_get_espn_clubhouse_url(team))

        # Get info for the game the team is playing
        nextGameBox = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'current')))
        dateTimeOfNextGame = nextGameBox.find_elements_by_tag_name('h4')
        dateTime = str(dateOfNextGame.text)

        # If they aren't playing a game today, remove the player and continue
        weekday, month, day, gameTimeS = dateTime.split() #['weekday', 'month', 'day', 'time', 'AM/PM', 'Timezone']
        if ( weekday.lower() != today.strftime('%a').lower() ) or \
           ( month.lower() !=   today.strftime('%b').lower())
           ( int(day) != today.day):
            activePlayers.remove(player)
            continue

        # If the team is playing, but the game starts in less than 20 minutes from now, 
        # remove the player and continue on
        gameTimeO = time( int(gameTimeS.split(':')[0]), 
                          int(gameTimeS.split(':')[0]) )
        twentyMinFromNow = datetime.now() + timedelta(minutes=20)
        if twentyMinFromNow > gameTime0:
            activePlayers.remove(player)
            continue

        # Go the game's boscore page
        nextGameBox.find_element_by_partial_link_text('Lineup').click()

        # Get the team's boxscore
           # 4 mlbBoxes, 2 for each time (batting lineup, starting pitcher)
        mlbBoxes = browser.find_elements_by_class_name('mlb-box') 
        boxscore = None
        pitcherBoxScore = None
        for mlbBox in mlbBoxes:
            topHeader = mlbBox.find_elements_by_tag_name('thead')[0].text
            if (__get_team_nickname(team) in topHeader):
                if 'Hitters' in topHeader:
                    boxscore = mlbBox
                if 'Pitchers' in topHeader:
                    pitcherBoxScore = mlbBox

        assert boxscore
        boxscoreBody = boxscore.find_element_by_tag_name('tbody')

        # If the team is playing, but the player's not in the lineup, 
        # remove the player and continue on
        playerInLineup = False
        formattedName = firstName[0] + ' ' + lastName
        rows = boxscoreBody.find_elements_by_tag_name('tr')
        for row in rows:
            if ([] != row.find_elements_by_partial_link_text(formattedName)):
                playerInLineup = True
        if not playerInLineup:
            activePlayers.remove(playerInLineup)
            continue

        # If we're asked to filter by minERA, and the player is playing, 
        # and the opponent's starting pitcher's ERA is too high, 
        # remove the player and continue on
        if not pitcherBoxScore:
            continue
        pBSBody = pitcherBoxScore.find_element_by_tag_name('tbody')
        onlyRow = pBSBody.find_elements_by_tag_name('tr')
        cells = onlyRow.find_element_by_tag_name('td')
        era = float(cells[-1])
        if era < kwargs['minEra']:
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
    return ''