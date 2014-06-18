import unittest
import pandas as pd

from btsReal.bot import Bot
from btsReal.filepath import Filepath
class TestBot(unittest.TestCase):
    def setUp(self):
        ## get usernames and passwords for test bots
        df = pd.io.excel.read_excel(Filepath.get_accounts_file(), 
                sheetname='Test', parse_cols='A,B,C,D')
        ## Create empty Bot -- always should have no selections when used
        eBotVals = df[df.ID == 'emptyBot']
        self.eBot = Bot(str(eBotVals.Email.item()), 
                        str(eBotVals.MLBPassword.item()))

        # save values for sBot and dBot
        self.sBotVals = df[df.ID == 'singleBot']
        self.dBotVals = df[df.ID == 'doubleBot']

    def tearDown(self):
        self.eBot.quit_browser()

    def test_get_login_page(self):
        loginTitle = 'Account Management - Login/Register | MLB.com: Account'
        self.eBot.get_login_page()
        self.assertTrue(loginTitle in self.eBot.get_browser().title)

    def test_login(self):
    	pageTitle = 'Beat The Streak | MLB.com: Fantasy'
    	self.eBot.login()
    	self.assertTrue(pageTitle in self.eBot.get_browser().title)

    def test_reset_selections(self):
        ## Create single Bot -- always should have one selection when used
        self.sBot = Bot(str(self.sBotVals.Email.item()), 
                        str(self.sBotVals.MLBPassword.item()))
        ## Create double Bot -- always should have two selections when used
        self.dBot = Bot(str(self.dBotVals.Email.item()), 
                        str(self.dBotVals.MLBPassword.item()))

        ## Case 1: Empty Bot -- no selections before AND after func call
        print "Assure eBot has no selections"
        self.eBot.login()
        answer = ''
        while answer != 'yes':
            print "Set eBot to no selections then type yes"
            answer = raw_input()
        # test function
        removeButtons = self.eBot.browser.find_elements_by_class_name('remove-action')
        self.assertEqual(removeButtons, [])
        self.eBot.reset_selections()
        self.assertEqual(removeButtons, [])

        ## Case 2: Single Bot -- one selection before, no selections after func call
        print "Assure sBot has one selections"
        self.sBot.login()
        answer = ''
        while answer != 'yes':
            print "Set sBot to one selections then type yes"
            answer = raw_input()
        # test function
        removeButtons = self.sBot.browser.find_elements_by_class_name('remove-action')
        self.assertEqual(len(removeButtons), 1)
        self.sBot.reset_selections()
        self.assertEqual(removeButtons, [])
        self.sBot.quit_browser()

        ## Case 3: Double (down) Bot -- two selections before, one selection after func call
        print "Assure dBot has two selections"
        self.dBot.login()
        answer = ''
        while answer != 'yes':
            print "Set dBot to two selections then type yes"
            answer = raw_input()
        # test function
        removeButtons = self.dBot.browser.find_elements_by_class_name('remove-action')
        self.assertEqual(len(removeButtons), 2)
        self.dBot.reset_selections()
        self.assertEqual(removeButtons, [])
        self.dBot.quit_browser()





