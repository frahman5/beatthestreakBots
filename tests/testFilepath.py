import unittest

from beatthestreakBots.config import ROOT
from beatthestreakBots.filepath import Filepath as F

class TestFilepath(unittest.TestCase):

	def test_get_root(self):
		print "DID YOU SET THE APPROPRIATE ROOT IN CONFIG?"
		self.assertEqual(F.get_root(), ROOT)

	def test_get_accounts_file(self):
		accountsFile = ROOT + '/btsAccounts.xlsx'
		self.assertEqual(F.get_accounts_file(), accountsFile)

	def test_get_log_file(self):
		testLog = ROOT + '/tests/logs.txt'
		prodLog = ROOT + '/logs.txt'
		# Case 1: testing
		self.assertEqual(F.get_log_file(test=True), testLog)
		# Case 2: Production
		self.assertEqual(F.get_log_file(), prodLog)