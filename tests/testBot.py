import unittest
import time
import pandas as pd

from beatthestreakBots.bot import Bot
from beatthestreakBots.filepath import Filepath
from beatthestreakBots.exception import NoPlayerFoundException

class TestBot(unittest.TestCase):

    def setUp(self):
        ## get usernames and passwords for test bots
        df = pd.io.excel.read_excel(Filepath.get_test_file(), 
                sheetname='Test', parse_cols='A,B,C,D')

        # If necessary, initalize sBot and dBot. Else set to None
        # sBot: always should have one selection when used
        # dBot: always should have two selections when used
        testsWithSAndDBots = (
            'testBot.TestBot.test_get_chosen_players', 
            'testBot.TestBot.test__reset_selections', 
            'testBot.TestBot.test_choose_players', 
            'testBot.TestBot.test_has_claimed_mulligan'
            )
        if self.id() in testsWithSAndDBots:
            self.dBotVals = df[df.ID == 'doubleBot']
            self.sBotVals = df[df.ID == 'singleBot']
            self.dBot = Bot( str(self.dBotVals.Email.item()), 
                             str(self.dBotVals.MLBPassword.item()), 
                             dev=True)
            self.sBot = Bot( str(self.sBotVals.Email.item()), 
                             str(self.sBotVals.MLBPassword.item()), 
                             dev=True)
            self.sBot.browser.set_window_position(34, 52) # for accessibility
        else:
            self.sBot = None
            self.dBot = None

        # Create empty Bot -- always should have no selections when used
        # Doubles as default testing bot
        self.eBotVals = df[df.ID == 'emptyBot']
        print "eBotEmail: " + str(self.eBotVals.Email.item())
        print "eBotPassword: " + str(self.eBotVals.MLBPassword.item())
        self.eBot = Bot( str(self.eBotVals.Email.item()), 
                         str(self.eBotVals.MLBPassword.item()), 
                         dev=True)
        self.eBot.browser.set_window_position(64, 82) # for accessibility

    def tearDown(self):
        self.eBot._quit_browser()
        if self.sBot:
                self.sBot._quit_browser()

        if self.dBot:
                self.dBot._quit_browser()

    def test_has_claimed_mulligan(self):
        self.assertTrue(self.sBot.has_claimed_mulligan())
        self.assertFalse(self.eBot.has_claimed_mulligan())

    @unittest.skip("Not Focus") 
    def test_get_login_page(self):
        loginTitle = 'Account Management - Login/Register | MLB.com: Account'
        self.eBot._get_login_page()
        self.assertTrue(loginTitle in self.eBot.browser.title)

    @unittest.skip("Not Focus")
    def test_get_make_pick_page(self):
        pageTitle = 'Beat The Streak | MLB.com: Fantasy'
        ## Case 1: Bot is not yet logged in:
        self.eBot._get_make_picks_page()
        self.assertTrue(pageTitle in self.eBot.browser.title)
        ## Case 2: Bot is already on picks page
        self.eBot._get_make_picks_page()
        self.assertTrue(pageTitle in self.eBot.browser.title)
        ## Case 3: Bot is already logged in but not on picks page
        self.eBot.browser.get('www.google.com')
        self.eBot._get_make_picks_page()
        self.assertTrue(pageTitle in self.eBot.browser.title)

    # @unittest.skip("Not Focus")
       ## indirectly tests "_click_make_pick_today"
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
        todayRow = self.eBot._Bot__get_todays_make_pick_row()
        # removeButtonsRaw = self.eBot.browser.find_elements_by_class_name('remove-action')
        removeButtonsRaw = todayRow.find_elements_by_class_name('remove-action')
        removeButtons = [elem for elem in removeButtonsRaw 
            if elem.get_attribute('class') == 'remove-action player-row']
        self.assertEqual(removeButtons, []) 

        self.eBot._reset_selections() # reset selections
        # should still be no remove Buttons after _reset_selections
        todayRow = self.eBot._Bot__get_todays_make_pick_row()
        removeButtonsRaw = todayRow.find_elements_by_class_name('remove-action')
        # removeButtonsRaw = self.eBot.browser.find_elements_by_class_name('remove-action')
        removeButtons = [elem for elem in removeButtonsRaw 
            if elem.get_attribute('class') == 'remove-action player-row']
        self.assertEqual(removeButtons, [])

        ## Case 2: Single Bot -- one selection before, no selections after func call
        self.__assure_bot_setup(self.sBot)
        todayRow = self.sBot._Bot__get_todays_make_pick_row()
        removeButtonsRaw = todayRow.find_elements_by_class_name('remove-action')
        # removeButtonsRaw = self.sBot.browser.find_elements_by_class_name('remove-action')
        removeButtons = [elem for elem in removeButtonsRaw 
            if elem.get_attribute('class') == 'remove-action player-row']
        self.assertEqual(len(removeButtons), 1)

        self.sBot._reset_selections() # reset the selection
        # should now be zero removeButtons
        todayRow = self.sBot._Bot__get_todays_make_pick_row()
        removeButtonsRaw = todayRow.find_elements_by_class_name('remove-action')
        # removeButtonsRaw = self.sBot.browser.find_elements_by_class_name('remove-action')
        removeButtons = [elem for elem in removeButtonsRaw 
            if elem.get_attribute('class') == 'remove-action player-row']
        self.assertEqual(removeButtons, [])

        ## Case 3: Double (down) Bot -- two selections before, one selection after func call
        self.__assure_bot_setup(self.dBot)
        # removeButtonsRaw = self.dBot.browser.find_elements_by_class_name('remove-action')
        todayRow = self.dBot._Bot__get_todays_make_pick_row()
        removeButtonsRaw = todayRow.find_elements_by_class_name('remove-action')
        removeButtons = [elem for elem in removeButtonsRaw 
            if elem.get_attribute('class') == 'remove-action player-row']
        self.assertEqual(len(removeButtons), 2)

        self.dBot._reset_selections() # reset selections
        # should be no remove buttons after we reset selections
        # removeButtonsRaw = self.dBot.browser.find_elements_by_class_name('remove-action')
        todayRow = self.dBot._Bot__get_todays_make_pick_row()
        removeButtonsRaw = todayRow.find_elements_by_class_name('remove-action')
        removeButtons = [elem for elem in removeButtonsRaw 
            if elem.get_attribute('class') == 'remove-action player-row']
        self.assertEqual(removeButtons, [])

    # @unittest.skip("Not Focus")
    def test_get_chosen_players(self):
        # Case 1: eBot has no chosen players
        self.__assure_bot_setup(self.eBot)
        self.assertEqual(self.eBot._get_chosen_players(), ())

        # Case 2: sBot has 1 chosen player
        self.__assure_bot_setup(self.sBot)
        player = raw_input("Which player did you choose? Please enter " + \
            "firstName + lastName \n")
        self.assertEqual(self.sBot._get_chosen_players(), (player,))

        # Case 3: dBot has 2 chosen players
        self.__assure_bot_setup(self.dBot)
        player1 = raw_input("Which players did you choose. Please enter " + \
            "the first as firstName + lastName \n")
        player2 = raw_input("now please enter the second in the same format \n")
        self.assertEqual(set(self.dBot._get_chosen_players()), 
            set([player1, player2]))

    # @unittest.skip("Not Focus")
    def test_choose_players(self):
        ## Get some active players to test with
        somePlayers = (
            ('Jose', 'Reyes', 'Toronto Blue Jays'), 
            ('Robinson', 'Cano', 'Seattle Mariners'), 
            ('Derek', 'Norris', 'Oakland Athletics'), 
            ('Daniel', 'Murphy', 'New York Mets'), 
            ('Carlos', 'Ruiz', 'Philadelphia Phillies'))
        self.eBot._get_make_picks_page() # give the tester somehwere to look
        actPlayer1 = None
        actPlayer2 = None
        actTeam = None
        for firstName, lastName, team in somePlayers:
            answer = ''
            if actPlayer1 and actPlayer2:
                break
            while answer not in ('yes', 'no'):
                print "Is {0} {1} on team {2} active today?".format(
                     firstName, lastName, team)
                answer = raw_input()
            if answer == 'yes':
                if actPlayer1:
                    actPlayer2 = (firstName, lastName, team)
                    break
                else:
                    actPlayer1 = (firstName, lastName, team)
                    actTeam = team
            elif answer == 'no':
                continue
        if None in (actPlayer1, actPlayer2, actTeam):
            print "Please add more players to some players"
            assert False


        ## Case 1: Single Down
            # Case 1.1: Ebot-> single Down
        self.__assure_bot_setup(self.eBot) # assure eBot is empty
        self.eBot.choose_players(p1=actPlayer1)
        self.assertEqual(self.eBot._get_chosen_players(), 
            (actPlayer1[0] + ' ' + actPlayer1[1],))
            # Case 1.2: sBot -> singleDown
        self.__assure_bot_setup(self.sBot) # assure sBot has single down
        self.sBot.choose_players(p1=actPlayer2)
        self.assertEqual(self.sBot._get_chosen_players(), 
            (actPlayer2[0] + ' ' + actPlayer2[1],))
            # Case 1.3: dBot -> single Down
        self.__assure_bot_setup(self.dBot) # assure dBot has double down
        self.dBot.choose_players(p1=actPlayer1)
        self.assertEqual(self.dBot._get_chosen_players(), 
            (actPlayer1[0] + ' ' + actPlayer1[1],))

        ## Case 2: Double Down
            # Case 2.1: Ebot -> double Down
        self.__assure_bot_setup(self.eBot) # assure eBot is empty
        self.eBot.choose_players(p1=actPlayer1, p2=actPlayer2)
        self.assertEqual(set(self.eBot._get_chosen_players()), 
            set(
                [ actPlayer1[0] + ' ' + actPlayer1[1], 
                  actPlayer2[0] + ' ' + actPlayer2[1] ] 
                ))
            # Case 2.2: sBot -> double Down
        self.__assure_bot_setup(self.sBot) # assure sBot has single down
        self.sBot.choose_players(p1=actPlayer1, p2 =actPlayer2)
        self.assertEqual(set(self.sBot._get_chosen_players()), 
            set(
                [ actPlayer1[0] + ' ' + actPlayer1[1], 
                  actPlayer2[0] + ' ' + actPlayer2[1] ] 
                ))
            # Case 2.3: dBot -> double Down
        self.__assure_bot_setup(self.dBot) # assure dBot has double down
        self.dBot.choose_players(p1=actPlayer1, p2=actPlayer2)
        self.assertEqual(set(self.dBot._get_chosen_players()), 
            set(
                [ actPlayer1[0] + ' ' + actPlayer1[1], 
                  actPlayer2[0] + ' ' + actPlayer2[1] ] 
                ))

        ## Case 3: No player on given team with given name
        self.__assure_bot_setup(self.eBot) # assure eBot is empty
        self.assertRaises(NoPlayerFoundException, 
            self.eBot.choose_players, p1=('oogly', 'boogly', actTeam))

    def test_get_username(self):
        self.assertEqual(self.eBot.get_username(), 
            self.eBotVals.Email.item())

    def test_get_password(self):
        self.assertEqual(self.eBot.get_password(), 
            self.eBotVals.MLBPassword.item())

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

    def test_get_todays_recommended_players(self):
        self.eBot._get_make_picks_page() # give the tester somehwere to look

        recommendedPlayers = []
        while True:
            answer = raw_input("Enter the next recommended player for tomorrow" + 
                " Format: (firstName, lastName, teamAbbrevation). If there" + 
                " are no more players, enter 'done'\n")
            if answer == 'done':
                break
            recommendedPlayers.append(tuple(answer.split()))

        self.assertEqual( set(recommendedPlayers), 
                          set(self.eBot.get_todays_recommended_players()) )
