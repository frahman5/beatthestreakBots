class Filepath(object):

	@classmethod
	def get_root(self):
		"""
		Returns the path of btsReal
		"""
		return '/Users/faiyamrahman/programming/Python/btsReal'

	@classmethod
	def get_accounts_file(self):
		"""
		Returns the path of the excel file containing account info
		for emails and beatthestreak accounts on mlb.com
		"""
		return self.get_root() + '/btsAccounts.xlsx'