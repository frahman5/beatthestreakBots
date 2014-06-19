import unittest

from btsReal.filepath import Filepath as F

class TestFilepath(unittest.TestCase):

	def test_get_root(self):
		root = '/Users/faiyamrahman/programming/Python/btsReal'
		self.assertEqual(F.get_root(), root)

	def test_get_accounts_file(self):
		accountsFile = '/Users/faiyamrahman/programming/Python/btsReal/btsAccounts.xlsx'
		self.assertEqual(F.get_accounts_file(), accountsFile)

	def test_get_log_file(self):
		testLog = '/Users/faiyamrahman/programming/Python/btsReal/tests/logs.txt'
		prodLog = '/Users/faiyamrahman/programming/Python/btsReal/logs.txt'
		# Case 1: testing
		self.assertEqual(F.get_log_file(test=True), testLog)
		# Case 2: Production
		self.assertEqual(F.get_log_file(), prodLog)