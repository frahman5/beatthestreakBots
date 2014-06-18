from selenium import webdriver
import time

class Bot(object):
    ## make sure you logout after logging in. 

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
        self.browser.implicitly_wait(5) # wait 2 seconds if an element is not there

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

    def get_login_page(self):
        """
        Opens a web broswer and navigates to the beat the streak login page
        """
        url = 'https://secure.mlb.com/enterworkflow.do?flowId=fantasy.bts.' + \
              'btsloginregister&forwardUrl=http://mlb.mlb.com/mlb/fantasy/' + \
              'bts/y2014/'
        self.browser.get(url)

    def login(self):
        """
        Logs in to mlb beat the streak site
        """
        ## make sure we're on the right page
        if not self.pageTitles['login'] in self.browser.title:
            self.get_login_page()
        
        # login (waits for page to load)
        time.sleep(2)
        self.browser.find_element_by_id('login_email').send_keys(self.username)
        self.browser.find_element_by_id('login_password').send_keys(self.password)
        self.browser.find_element_by_name('submit').click()

    def _click_make_pick_today(self):
        """
        Clicks on make pick for today's date
        """
        ## make sure we're on the right page
        if not self.pageTitles['picks'] in self.browser.title:
            self.login()

        # click on today's make pick 
        time.sleep(2)
        playerInfoRows = self.browser.find_elements_by_class_name('player-info-rows')
        today = playerInfoRows[1] ## always the second row from the top
        today.click()

    def choose_player(self, team, firstName, lastName):
        """
        string string string -> None

        Chooses player firstName lastName on team team 
        """
        ## type checking
        for param in (team, firstName, lastName):
            assert type(param) == str
        assert team in self.teams.keys()

        # click on make pick for today
        self._click_make_pick_today() 

        ## click on "select teams"
        selectTeam = self.browser.find_element_by_id('team-name')
        selectTeam.click()

        ## click on desired team
        time.sleep(2)
        team = self.browser.find_element_by_class_name(self.teams[team])
        team.click()

        ## Make pick
            # For each row including a "select" button, there are two last
            # names, one for a player on team team, and one for the opposing
            # starting pitcher. 
        time.sleep(2)
        lastNameElems = self.browser.find_elements_by_class_name("last-name")
        lastNames = [elem.text for elem in lastNameElems]

        selectButtons = self.browser.find_elements_by_class_name("select-action")
        assert len(lastNames) == len(selectButtons) * 2
            # sift out the repeated last name of the opposing starting pitcher.
            # This way, the index of a lastName in teamLastNames is the index
            # of the select button in selectButtons for the corresponding player
        teamLastNames = [elem for elem in lastNames 
            if lastNames.index(elem) % 2 == 0]

        desiredPlayer = [elem for elem in teamLastNames if elem == lastName]
            # Either desiredPlayer is len 1 or > 1:
            # len1: # check that firstname is correct and then select player
        if len(desiredPlayer) == 1:
            player = desiredPlayer[0]
            print player
            firstNames = self.browser.find_elements_by_class_name('first-name')
            assert firstNames[lastNames.index(player)].text == firstName
            print firstNames[lastNames.index(player)].text
            import pdb
            pdb.set_trace()
            selectButtons[teamLastNames.index(player)].click()
            # len > 1: proceed via firstName
        elif len(desiredPlayer) > 1:
            print desiredPlayer
            firstNameElems = self.browser.find_elements_by_class_name('first-name')
            firstNames = [elem.text for elem in firstNameElems]
            teamFirstNames = [elem for elem in firstNames 
                if firstNames.index(elem) % 2 == 0]
            desiredPlayer = [elem for elem in teamFirstNames 
                if elem.text == firstNames]
            if len(desiredPlayer) == 1: # check that lastName is correct and select player
                player = desiredPlayer[0]
                assert lastNames[firstNames.index(player)].text == lastName
                selectButtons[teamFirstNames.index(player)].click()
            elif len(desiredPlayer) > 1: 
                correctNames = [player for player in desiredPlayer 
                    if teamLastNames[teamFirstNames.index(player)].text == lastName]
                if len(correctNames) == 1:
                    selectButtons[teamFirstNames.index(player)].click()
                else:
                    raise SameNameException("Team {0} has two players".format(team) + \
                        "with same name: {0} {1}".format(firstName, lastName))

    def reset_selections(self):
        """
        If this bot has already made some selections today, removes
        the selections
        """
        pass
        
    def quit_browser(self):
        """
        Closes self.browser
        """
        self.browser.quit()

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def __set_username(self, username):
        assert type(username) == str
        self.username == username

    def __set_password(self, password):
        assert type(password) == str
        self.password = password

    def get_browser(self):
        return self.browser