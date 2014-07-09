from config import ROOT
from datetime import datetime
import logging
import logging.handlers

class Filepath(object):

    @classmethod
    def get_root(self):
        """
        Returns the path of btsReal
        """
        return ROOT

    @classmethod
    def get_accounts_file(self):
        """
        Returns the path of the excel file containing account info
        for emails and beatthestreak accounts on mlb.com
        """
        return self.get_root() + '/btsAccountsTest.xlsx'

    @classmethod
    def get_test_file(self):
        """
        Returns the path of the excel file containing account info
        for test accounts on mlb.com
        """
        return self.get_root() + "/nonProductionBtsAccounts.xlsx"

    @classmethod
    def get_log_file(self, test=False):
        """
        Returns the path of the .txt file containing logs
        """
        today = datetime.today().date().strftime('%m-%d-%Y')

        if test:
            return self.get_root() + '/tests/logs/' + today + '.txt'
        else:
            return self.get_root() + '/logs/' + today + '.txt'
