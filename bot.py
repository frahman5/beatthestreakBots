import time
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


from exception import NoPlayerFoundException, SameNameException
from decorators import logErrors


class Bot(object):
    ## make sure you logout after logging in. 

    # @logErrors
    def __init__(self, username, password):
        """
        string string -> None
            username: str | username on beat the streak
            password: str | password for given username
            browser: webdriver | firefox web browser
            pageTitles: dict | dictionary of page titles for key pages
            teams: dict | keys: team full names (e.g Boston Red Sox), values:
               3 digit abbrevations used in beatthestreak html code

        Instantiates the bot, which represents an account
        on MLB's beat the streak
        """
        assert type(username) == str
        assert type(password) == str

        self.username = username
        self.password = password
        self.browser = webdriver.Firefox()
        seleniumLogger = logging.getLogger('selenium.webdriver.remote.remote_connection')
        # Only display possible problems
        seleniumLogger.setLevel(logging.WARNING)

        self.pageTitles = {
            'login':'Account Management - Login/Register | MLB.com: Account', 
            'picks': 'Beat The Streak | MLB.com: Fantasy'}
        self.teams = {
            'Los Angeles Angels': 'ana', 'Baltimore Orioles': 'bal', 
            'Boston Red Sox': 'bos', 'Chicago White Sox': 'cws', 
            'Cleveland Indians': 'cle', 'Detroit Tigers': 'det',
            'Houston Astros': 'hou',  'Kansas City Royals': 'kc', 
            'Minnesota Twins': 'min', 'New York Yankees': 'nyy',
            'Oakland Athletics': 'oak', 'Seattle Mariners': 'sea',
            'Tampa Bay Rays': 'tb', 'Texas Rangers': 'tex',
            'Toronto Blue Jays': 'tor', 'Arizona Diamondbacks': 'ari',
            'Atlanta Braves': 'atl', 'Chicago Cubs': 'chc',
            'Cincinnati Reds': 'cin',  'Colorado Rockies': 'col',
            'Los Angeles Dodgers': 'la', 'Miami Marlins': 'mia',
            'Milwaukee Brewers': 'mil',  'New York Mets': 'nym',
            'Philadelphia Phillies': 'phi', 'Pittsburgh Pirates': 'pit',
            'San Diego Padres': 'sd', 'San Francisco Giants': 'sf',
            'St. Louis Cardinals': 'stl', 'Washington Nationals': 'was'
            }

    # @logErrors
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
        assert p1[2] in self.teams.keys()
           # p2 should be of length 0 or 3, and in the later case contain strings
           # and have a valid team
        assert len(p2) in (0,3)
        if len(p2) == 3:
            for item in p2:
                assert type(item) == str
            assert p2[2] in self.teams.keys()
        
        # Reset selections and then choose players
        self._reset_selections() 
        self.__choose_single_player(p1)
        if len(p2) == 3:
            self.__choose_single_player(p2, doubleDown=True)

    # @logErrors
    def claim_mulligan(self):
        print "Claiming Mulligan for u, p: {0}, {1}\n".format(self.username, self.password)

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
        
        # give it some time, then quit the browser
        time.sleep(10)
        self.browser.quit()
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


    # @logErrors
    def get_username(self):
        return self.username

    # @logErrors
    def get_password(self): 
        return self.password

    # @logErrors
    def _get_login_page(self):
        """
        Opens a web broswer and navigates to the beat the streak login page
        """
        url = 'https://secure.mlb.com/enterworkflow.do?flowId=fantasy.bts.' + \
              'btsloginregister&forwardUrl=http://mlb.mlb.com/mlb/fantasy/' + \
              'bts/y2014/'
        self.browser.get(url)
        time.sleep(3)

    # @logErrors
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
        self.browser.find_element_by_id('login_email').send_keys(self.username)
        self.browser.find_element_by_id('login_password').send_keys(self.password)
        self.browser.find_element_by_name('submit').click()
        time.sleep(3)

    # @logErrors
    def _click_make_pick_today(self):
        """
        Clicks on make pick for today's date
        """
        ## make sure we're on the right page
        self._get_make_picks_page()

        # click on today's make pick 
        playerInfoRows = self.browser.find_elements_by_class_name('player-info-rows')
        today = playerInfoRows[1] ## always the second row from the top
        today.click()
        time.sleep(3)

    # @logErrors
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

    # @logErrors
    def _reset_selections(self):
        """
        If this bot has already made some selections today, removes
        the selections
        """
        self._get_player_selection_dropdown() # make the remove Buttons show up

        removeButtonsRaw = self.browser.find_elements_by_class_name('remove-action')
        removeButtons = [elem for elem in removeButtonsRaw 
               if elem.get_attribute('class') == 'remove-action player-row']
        while removeButtons != []:
            removeButtons[0].click()
            time.sleep(3)
            subAndCancel = self.browser.find_elements_by_class_name('ui-button-text-only')
            subAndCancel[0].click()
            time.sleep(3)
            removeButtonsRaw = self.browser.find_elements_by_class_name('remove-action')
            removeButtons = [elem for elem in removeButtonsRaw 
                   if elem.get_attribute('class') == 'remove-action player-row']
        time.sleep(3)

    # @logErrors
    def _quit_browser(self):
        """
        Closes self.browser
        """
        self.browser.quit()
    
    # @logErrors
    def _get_chosen_players(self):
        """
        None -> Tuple
           Returns a tuple of strings containing the names
           of players this bot currently has selected
        """
        # html elements that correspond to players are the first item
        # in a list. Other html elements on the make pick page that 
        # are first items in a list have text that either says 'date locked', 
        # 'double down', or 'make pick'
        firstItems = self.browser.find_elements_by_class_name('first')
        players = [elem.text for elem in firstItems if 
            elem.tag_name == 'li' and elem.text not in ('Date Locked', 
                'Double Down', 'Make Pick')]
        return tuple(players)

    # @logErrors
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
        assert player[2] in self.teams.keys()

        firstName, lastName, team = player

        ## Get to selection dropdown for team
        self._get_player_selection_dropdown()
            # click on "select teams"
        selectTeam = self.browser.find_element_by_id('team-name')
        selectTeam.click()
        time.sleep(3)
            # click on desired team
        team = self.browser.find_element_by_class_name(self.teams[team])
        team.click()
        time.sleep(3)

        ## Make pick
            # get lists of firstNames, lastNames, and select Buttons
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
            buttons = self.browser.find_elements_by_class_name('ui-button-text-only')
            buttons[0].click()

        time.sleep(3)
