from pyvirtualdisplay import Display
import time
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta


from exception import NoPlayerFoundException, SameNameException
from decorators import logErrors
from config import ROOT



class Bot(object):
    ## make sure you logout after logging in. 

    def __init__(self, username, password, dev=False):
        """
        string string -> None
            username: str | username on beat the streak
            password: str | password for given username
            browser: webdriver | firefox web browser
            pageTitles: dict | dictionary of page titles for key pages
            teams: dict | keys: team full names (e.g Boston Red Sox), values:
               3 digit abbrevations used in beatthestreak html code
            dev: Indicates we are using this in dev mode, which changes
               "today" to "tomorrow", so that we don't run into the issue
               of player selections becoming locked

        Instantiates the bot, which represents an account
        on MLB's beat the streak
        """
        assert type(username) == str
        assert type(password) == str

        ## webdriver needs a display to run. This sets up a virtual "fake" one
        if ROOT == '/home/faiyamrahman/programming/Python/beatthestreakBots':
            self.display = Display(visible=0, size=(1024, 768))
            self.display.start()

        ## Set core attributes
        self.username = username
        self.password = password
        self.browser = webdriver.Chrome()
        self.today = datetime.today()
        self.dev = dev
        if self.dev:
            self.today = self.today + timedelta(days=1)

        
        # Create a logger so that we don't get blasted with unnecessary info
        # on every error in a test suite. Instead, we only get high priority shit
        seleniumLogger = logging.getLogger('selenium.webdriver.remote.remote_connection')
        seleniumLogger.setLevel(logging.WARNING)

           # used to check if we are on the right page at the right time
        self.pageTitles = {
            'login':'Account Management - Login/Register | MLB.com: Account', 
            'picks': 'Beat The Streak | MLB.com: Fantasy'}
           # used to check that we don't enter a bogus team name
        self.teams = (
            'mia', 'cws', 'nyy', 'lad', 'tor', 'phi', 'cle', 'stl', 'oak', 
            'hou', 'nym', 'cin', 'sd', 'tex', 'det', 'sea', 'sf', 'col',
            'pit', 'laa', 'wsh', 'chc', 'bos', 'tb', 'ari', 'atl', 
            'mil', 'min', 'kc', 'bal')
        # self.teams = {
        #     'Los Angeles Angels': 'ana', 'Baltimore Orioles': 'bal', 
        #     'Boston Red Sox': 'bos', 'Chicago White Sox': 'cws', 
        #     'Cleveland Indians': 'cle', 'Detroit Tigers': 'det',
        #     'Houston Astros': 'hou',  'Kansas City Royals': 'kc', 
        #     'Minnesota Twins': 'min', 'New York Yankees': 'nyy',
        #     'Oakland Athletics': 'oak', 'Seattle Mariners': 'sea',
        #     'Tampa Bay Rays': 'tb', 'Texas Rangers': 'tex',
        #     'Toronto Blue Jays': 'tor', 'Arizona Diamondbacks': 'ari',
        #     'Atlanta Braves': 'atl', 'Chicago Cubs': 'chc',
        #     'Cincinnati Reds': 'cin',  'Colorado Rockies': 'col',
        #     'Los Angeles Dodgers': 'la', 'Miami Marlins': 'mia',
        #     'Milwaukee Brewers': 'mil',  'New York Mets': 'nym',
        #     'Philadelphia Phillies': 'phi', 'Pittsburgh Pirates': 'pit',
        #     'San Diego Padres': 'sd', 'San Francisco Giants': 'sf',
        #     'St. Louis Cardinals': 'stl', 'Washington Nationals': 'was'
        #     }

    def choose_players(self, p1=(), p2=()):
        """
        TupleOfStrings TupleOfStrings -> None
           p1 and p2: Either the empty tuple or a tuple of format
              (firstName, lastName, teamAbbreviation) where firstName and
              lastName define a player in the MLB and teamAbbrevations
              is the team abbreviation used in beatthestreak's html code, 
              as defined in self.teams

        If p1 and p2 are both nonEmpty, choose p1 and p2. Else, we choose
        p1, which should be nonempty. 
        """
        ## Type checking
           # should both be tuples
        assert type(p1) == tuple
        assert type(p2) == tuple
           # p1 should be of length 3, contain strings, and have a valid team
        assert len(p1) == 3
        for item in p1:
            assert type(item) == str
        assert p1[2] in self.teams
           # p2 should be of length 0 or 3, and in the later case contain strings
           # and have a valid team
        assert len(p2) in (0,3)
        if len(p2) == 3:
            for item in p2:
                assert type(item) == str
            assert p2[2] in self.teams
        
        # Reset selections and then choose players
        print "------> Removing any currently selected players"
        self._reset_selections()
        assert self.browser.title == self.pageTitles['picks'] 
        print "------> Choosing player: {}".format(p1)
        self.__choose_single_player(p1)
        if len(p2) == 3:
            print "------> Choosing player: {}".format(p2)
            self.__choose_single_player(p2, doubleDown=True)
        # check that the players have been chosen
        playerSet = {player[0] + ' ' + player[1] for player in (p1, p2)
                      if len(player) != 0}
        assert set(self._get_chosen_players()) == playerSet

        # Close up shop, unless we're devving, in case we want to keep the 
        # screen open for testing
        if not self.dev:
            self.browser.close()

    def get_todays_recommended_players(self):
        """
        None -> TupleOfTupleOfStrings

        Returns a tuple of players (firstName, lastName, teamAbbrev) corresponding
        to the players recommended by MLB today
        """
        recommendedPlayers = []

        # Make sure we are on the make picks page and check that the 
        # recommendedPlayers player grid has dropped down
        self._get_player_selection_dropdown()
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, 'bts-players-grid')))

        # get rows correspodning to recommended players
        playerGrid = self.browser.find_element_by_id('bts-players-grid')
        playerRows = playerGrid.find_elements_by_tag_name('tr')[1:] # 0th elem is header of table

        # collect information about recommended players
        for row in playerRows:
            playerInfo = row.find_element_by_class_name('player-team')
            playerTuple = (
                str( playerInfo.find_element_by_class_name('first-name').text), 
                str( playerInfo.find_element_by_class_name('last-name').text), 
                str( playerInfo.find_element_by_class_name('team').text).lower()
                          )  
            recommendedPlayers.append(playerTuple)

        # tuplify the list and return it
        return tuple(recommendedPlayers)

    def claim_mulligan(self):
        print "-->Claiming Mulligan for u, p: {0}, {1}\n".format(self.username, self.password)

        ## navigate to claim mulligan page
        self._get_make_picks_page()
        more = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "last"))
            )
        more.click()
        button1 = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bam-button-primary"))
            )
        buttons = self.browser.find_elements_by_class_name('bam-button-primary')
        buttons[3].click()

        ## Claim the mulligan
        mulOption = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "mulligan-list")) 
            )
        mulOption.click()
        claimMul = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'claim-mulligan-btn'))
            )
        claimMul.click()
        
        # give it some time, then quit the browser and if necessary, stop the display
        time.sleep(10)
        self.browser.quit()
        if ROOT == '/home/faiyamrahman/programming/Python/beatthestreakBots':
            print "--> Stopping Display"
            self.display.stop()

    def has_claimed_mulligan(self):
        """
        Returns True if the account with self.username and self.password
        has claimed its mulligan, false otherwise
        """
        ## navigate to claim mulligan page
        self._get_make_picks_page()
        more = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "last"))
            )
        more.click()
        button1 = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bam-button-primary"))
            )
        buttons = self.browser.find_elements_by_class_name('bam-button-primary')
        buttons[3].click()

        ## Check if we've claimed the mulligan
        mulOption = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "mulligan-list")) 
            )
        mulOption.click()
        try:
            claimMul = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'claim-mulligan-btn')))
        except TimeoutException:
            return True

        return False

    def get_username(self):
        return self.username

    def get_password(self): 
        return self.password

    def _get_login_page(self):
        """
        Opens a web broswer and navigates to the beat the streak login page
        """
        url = 'https://secure.mlb.com/enterworkflow.do?flowId=fantasy.bts.' + \
              'btsloginregister&forwardUrl=http://mlb.mlb.com/mlb/fantasy/' + \
              'bts/y2014/'
        self.browser.get(url)
        time.sleep(3)
        assert self.browser.title == self.pageTitles['login']

    def _get_make_picks_page(self):
        """
        Logs in to mlb beat the streak site
        """
        ## Are we already on it?
        if self.pageTitles['picks'] in self.browser.title:
            return

        ## Else navigate to the login page
        if not self.pageTitles['login'] in self.browser.title:
            self._get_login_page()

        ## If we were already logged in, then now we are on the picks page
        if self.pageTitles['picks'] in self.browser.title:
            return
        
        # Otherwise, we need to login
        login = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, 'login_email')))
        login.send_keys(self.username)
        pword = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, 'login_password')))
        pword.send_keys(self.password)
        submit = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.NAME, 'submit')))
        submit.click()
        time.sleep(3)
        assert self.browser.title == self.pageTitles['picks']

    def _click_make_pick_today(self):
        """
        Clicks on make pick for today's date
        """
        ## make sure we're on the right page
        self._get_make_picks_page()

        # get today's row
        todayRow = self.__get_todays_make_pick_row()

        todayPlayerInfoRow = todayRow.find_element_by_class_name('player-info-rows')
        todayPlayerInfoRow.click()
        time.sleep(3)

    def _get_player_selection_dropdown(self):
        """
        Gets the player selection dropdown box. Should be used from the make picks
        page
        """
        # make sure we're on the make picks page
        self._get_make_picks_page()

        selectTeamBox = self.browser.find_elements_by_id('team-name')[0]
        if selectTeamBox.is_displayed():
            return
        else:
            self._click_make_pick_today() # includes a sleep at the end

    def _reset_selections(self):
        """
        If this bot has already made some selections today, removes
        the selections
        """
        self._get_player_selection_dropdown() # make the remove Buttons show up
 
        # if it's the empty Bot, then return
        if len(self._get_chosen_players()) == 0:
            return

        ## Use a webdriverWait so we throw an exception if shit isnt there
        firstRemoveButton = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'remove-action')))

        ## Get today's row
        todayRow = self.__get_todays_make_pick_row()
        removeButtonsRaw = todayRow.find_elements_by_class_name('remove-action')
        removeButtons = [elem for elem in removeButtonsRaw 
               if elem.get_attribute('class') == 'remove-action player-row']

        while removeButtons != []:
            removeButtons[0].click()
            time.sleep(3)
            subAndCancel = self.browser.find_elements_by_class_name('ui-button-text-only')
            subAndCancel[0].click()
            time.sleep(3)

            ## get the remaining remove Buttons
               # need to refresh todayRow because it might have moved off DOM
            todayRow = self.__get_todays_make_pick_row() 
            removeButtonsRaw = todayRow.find_elements_by_class_name('remove-action')
            removeButtons = [ elem for elem in removeButtonsRaw 
                   if elem.get_attribute('class') == 'remove-action player-row']
        time.sleep(3)

    def _quit_browser(self):
        """
        Closes self.browser
        """
        if ROOT == '/home/faiyamrahman/programming/Python/beatthestreakBots':
            self.display.stop()
        self.browser.quit()
            
    def _get_chosen_players(self):
        """
        None -> Tuple
           Returns a tuple of strings containing the names
           of players this bot currently has selected
        """

 
        # Get today's make pick row
        todayRow = self.__get_todays_make_pick_row()

        # Find the players selected for today
                # html elements that correspond to players are the first item
                # in a list. Other html elements on the make pick page that 
                # are first items in a list have text that either says 
                # 'date locked', 'double down', or 'make pick'
        firstItems = todayRow.find_elements_by_class_name('first')
        players = [ elem.text for elem in firstItems if 
                    elem.tag_name == 'li' and elem.text not in ('Date Locked', 
                    'Double Down', 'Make Pick')]
        return tuple(players)

    def __get_todays_make_pick_row(self):
        """
        None -> WebElement
           Returns the row on the make picks page corresponding to today
        """
        # make sure we are on the get make picks page
        self._get_make_picks_page()

        ## Get the row corresponding to today
        firstRow = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'tr')))
        rows = self.browser.find_elements_by_tag_name('tr')
            ## date in 'mm/dd/yyyy' format
        todayFormatted = self.today.date().strftime('%m/%d/%Y')
        todayRow = [ row for row in rows if 
                     row.get_attribute('data-date') == todayFormatted][0]

        return todayRow

    def __choose_single_player(self, player, doubleDown=False):
        """
        TupleOfStrings bool -> None
            player: (firstName, lastName, teamAbbreviation)
            doubleDown: True if this is a doubleDown pick, False otherwise

        Assigns player player to bot.
        """
        ## Type checking
        assert type(player) == tuple
        assert len(player) == 3
        assert player[2] in self.teams

        firstName, lastName, team = player

        ## Make sure the player selection dropdown has been dropped
        self._get_player_selection_dropdown()
            # click on "select teams"
        selectTeam = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, 'team-name')))
        # selectTeam = self.browser.find_element_by_id('team-name')
        selectTeam.click()
        time.sleep(3)
            # click on desired team
        team = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, team)))
        team.click()
        time.sleep(3)

        ## Make pick
            # get lists of firstNames, lastNames, and select Buttons
        namesThereYet = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "last-name")))
        lastNameElems = self.browser.find_elements_by_class_name("last-name")
        firstNameElems = self.browser.find_elements_by_class_name("first-name")
        selectButtons = self.browser.find_elements_by_class_name("select-action")
        assert len(lastNameElems) == len(selectButtons) * 2
        assert len(firstNameElems) == len(selectButtons) * 2
            # for each player on team team, the opposing pitcher's name shows
            # up once (in both name lists). Sift out the repeated last name of the 
            # opposing starting pitcher so that the index of a lastName in 
            # teamLastNames (resp. firstName in teamFirstNames) is the index
            # of the select button in selectButtons for the corresponding player
        teamLastNameElems = [elem for elem in lastNameElems
            if lastNameElems.index(elem) % 2 == 0]
        teamFirstNameElems = [elem for elem in firstNameElems
            if firstNameElems.index(elem) % 2 == 0]
        firstNameMatches = [teamFirstNameElems.index(elem) for elem 
            in teamFirstNameElems if elem.text == firstName]
        lastNameMatches = [teamLastNameElems.index(elem) for elem 
            in teamLastNameElems if elem.text == lastName]
        fullNameMatches = [index for index in firstNameMatches 
            if index in lastNameMatches]

        numMatches = len(fullNameMatches)
        if numMatches == 0: 
            raise NoPlayerFoundException("Player {0} {1} on team {2}".format(
                firstName, lastName, team) + "was not found")
        if numMatches == 1:
            selectButtons[fullNameMatches[0]].click()
        elif numMatches > 1: # pragma: no cover
            raise SameNameException("The {0} have two players ".format(team) + \
                        "with the same name: {0} {1}".format(firstName, lastName))
        if doubleDown:
            # first button : Double Down. SecondButton: Replace Selection
            buttonsThereYet = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'ui-button-text-only')))
            buttons = self.browser.find_elements_by_class_name('ui-button-text-only')
            buttons[0].click()

        time.sleep(3)
