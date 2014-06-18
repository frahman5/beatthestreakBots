import unittest

from btsReal.filepath import Filepath as F

class TestFilepath(unittest.TestCase):

	def test_get_root(self):
		root = '/Users/faiyamrahman/programming/Python/btsReal'
		self.assertEqual(F.get_root(), root)

	def test_get_accounts_file(self):
		accountsFile = '/Users/faiyamrahman/programming/Python/btsReal/btsAccounts.xlsx'
		self.assertEqual(F.get_accounts_file(), accountsFile)