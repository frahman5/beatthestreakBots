import unittest
import time
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
        self.sBot = None
        self.dBot = None

    def tearDown(self):
        self.eBot._quit_browser()
        if self.sBot:
            self.sBot._quit_browser()
        if self.dBot:
            self.dBot._quit_browser()

    # @unittest.skip("Not Focus")
    def test_get_login_page(self):
        loginTitle = 'Account Management - Login/Register | MLB.com: Account'
        self.eBot._get_login_page()
        self.assertTrue(loginTitle in self.eBot._get_browser().title)

    # @unittest.skip("Not Focus")
    def test_get_make_pick_page(self):
    	pageTitle = 'Beat The Streak | MLB.com: Fantasy'
        ## Case 1: Bot is not yet logged in:
    	self.eBot._get_make_picks_page()
    	self.assertTrue(pageTitle in self.eBot._get_browser().title)
        ## Case 2: Bot is already logged in:
        self.eBot._get_make_picks_page()
        self.assertTrue(pageTitle in self.eBot._get_browser().title)

    # @unittest.skip("Not Focus")
    def test_get_player_selection_dropdown(self):
        self.eBot._get_make_picks_page()

        ## Case 1: the player selection dropdown has NOT yet been clicked
        selectTeamBox = self.eBot.browser.find_elements_by_id('team-name')[0]
        self.assertFalse(selectTeamBox.is_displayed())
        self.eBot._get_player_selection_dropdown()
        self.assertTrue(selectTeamBox.is_displayed())
        ## Case 2: the player selection dropdown has ALREADY been clicked
        self.assertTrue(selectTeamBox.is_displayed())
        self.eBot._get_player_selection_dropdown()
        self.assertTrue(selectTeamBox.is_displayed())

    # @unittest.skip("Not Focus")
    def test__reset_selections(self):
        ## Case 1: Empty Bot -- no selections before AND after func call
        self.__assure_bot_setup(self.eBot)
        removeButtonsRaw = self.eBot.browser.find_elements_by_class_name('remove-action')
        removeButtons = [elem for elem in removeButtonsRaw 
            if elem.get_attribute('class') == 'remove-action player-row']
        self.assertEqual(removeButtons, []) 

        self.eBot._reset_selections() # reset selections
        # should still be no remove Buttons after _reset_selections
        removeButtonsRaw = self.eBot.browser.find_elements_by_class_name('remove-action')
        removeButtons = [elem for elem in removeButtonsRaw 
            if elem.get_attribute('class') == 'remove-action player-row']
        self.assertEqual(removeButtons, [])

        ## Case 2: Single Bot -- one selection before, no selections after func call
        self.sBot = Bot(str(self.sBotVals.Email.item()), 
                        str(self.sBotVals.MLBPassword.item()))
        self.__assure_bot_setup(self.sBot)
        removeButtonsRaw = self.sBot.browser.find_elements_by_class_name('remove-action')
        removeButtons = [elem for elem in removeButtonsRaw 
            if elem.get_attribute('class') == 'remove-action player-row']
        self.assertEqual(len(removeButtons), 1)

        self.sBot._reset_selections() # reset the selection
        # should now be zero removeButtons
        removeButtonsRaw = self.sBot.browser.find_elements_by_class_name('remove-action')
        removeButtons = [elem for elem in removeButtonsRaw 
            if elem.get_attribute('class') == 'remove-action player-row']
        self.assertEqual(removeButtons, [])

        ## Case 3: Double (down) Bot -- two selections before, one selection after func call
        self.dBot = Bot(str(self.dBotVals.Email.item()), 
                        str(self.dBotVals.MLBPassword.item()))
        self.__assure_bot_setup(self.dBot)
        removeButtonsRaw = self.dBot.browser.find_elements_by_class_name('remove-action')
        removeButtons = [elem for elem in removeButtonsRaw 
            if elem.get_attribute('class') == 'remove-action player-row']
        self.assertEqual(len(removeButtons), 2)

        self.dBot._reset_selections() # reset selections
        # should be no remove buttons after we reset selections
        removeButtonsRaw = self.dBot.browser.find_elements_by_class_name('remove-action')
        removeButtons = [elem for elem in removeButtonsRaw 
            if elem.get_attribute('class') == 'remove-action player-row']
        self.assertEqual(removeButtons, [])

    def __assure_bot_setup(self, bot):
        """
        bot -> None

        Helper function to make sure that when they are used, eBot has no
        selections, sBot has 1 selection and dBot has two selections
        """
        if bot == self.eBot:
            botString = "eBot"
            selString = '0'
        elif bot == self.sBot:
            botString = "sBot"
            selString = '1'
        elif bot == self.dBot:
            botString = "dBot"
            selString = '2'
        else:
            raise Exception("Can only pass one of eBot, sBot or dBot to" + \
                "_assure_bot_setup")
        
        print "***** Assure {0} has {1} selection(s) *****".format(
                 botString, selString)
        bot._get_make_picks_page()
        answer = ''
        while answer != 'yes':
            print "Set {0} to {1} selection(s) then type yes".format(
                     botString, selString)
            answer = raw_input()

    def test_choose_player(self):
        ## Case 1: Single Down
            # Case 1.1: Ebot-> single Down

            ## Assure eBot is empty, then assign him some
            ## random active player, then check that that
            ## active player and only that active player is assigned
            ## to him

            # Case 1.2: sBot -> singleDown

            # Case 1.3: dBot -> single Down

        ## Case 2: Double Down
            # Case 2.1: Ebot -> double Down

            # Case 2.2: sBot -> double Down

            # Case 2.3: dBot -> double Down
        self.assertTrue(False)


