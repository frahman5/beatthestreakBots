from selenium import webdriver

class Bot(object):
    ## make sure you logout after logging in. 
    def __init__(self, username, password):
        """
        string string -> None
            username: str | username on beat the streak
            password: str | password for given username

        Instantiates the bot, which represents an account
        on MLB's beat the streak
        """
        self.username = username
        self.password = password
        self.browser = webdriver.Firefox()
        self.pageTitles = {
            'login':'Account Management - Login/Register | MLB.com: Account', 
            'picks': 'Beat The Streak | MLB.com: Fantasy'}

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
        if not self.pageTitles['login'] in self.browser.title:
            self.get_login_page()
        self.browser.find_element_by_id('login_email').send_keys(self.username)
        self.browser.find_element_by_id('login_password').send_keys(self.password)
        self.browser.find_element_by_name('submit').click()

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