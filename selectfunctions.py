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
        browser.quit()
        if ROOT == '/home/faiyamrahman/programming/Python/beatthestreakBots':
            print "--> Stopping display for get batters"
            display.stop()
        raise

    ## Close the browser, stop the display if necessary
    browser.quit()
    if ROOT == '/home/faiyamrahman/programming/Python/beatthestreakBots':
        print "--> Stopping display for get batters"
        display.stop()

    print tuple(players)
    return tuple(players)