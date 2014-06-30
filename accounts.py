#!bvenv/bin/python
import sys
import random
import pandas as pd

from selenium import webdriver

## A globally shared browser for all activites
browser = None

def make_gmail_account(username, password):
	"""
	string string -> bool

	Creates a yahoo email account with the given username and password. 
	Returns True if successful, False otherwise
	"""
	pass

def make_espn_bts_account(username, password):
	"""
	string string -> None

	Creates an ESPN beatthestreak account with the given username and password
	"""
	pass

def claim_mulligan(username, password):
	"""
	string string -> None

	Creates a bot with username and password and then claims the bots claim_mulligan
	"""
	pass

def __get_yahoo_create_account_page():
    """
    Opens a web broswer and navigates to the beat the streak login page
    """
    if not browser:
    	browser = webdriver.Firefox()
    url = 'https://secure.mlb.com/enterworkflow.do?flowId=fantasy.bts.' + \
          'btsloginregister&forwardUrl=http://mlb.mlb.com/mlb/fantasy/' + \
          'bts/y2014/'
    self.browser.get(url)
    time.sleep(3)


def main(N):
	"""
	int -> None

	Creates N unique beatthestreak accounts, claims mulligans for each account
	and stores all username and password info in btsAccounts.xlsx, sheetname "Production"
	"""
	usernameStarters = [ 'faiyam', 'rahman', 'bts', 'metro', 'williams', 
						 'grassfed', 'daft', 'fossil', 'water', 'earth']
    passwordChoices = ['sdFgsdfg892m45', 'beatthesTreak82349234nn', 
                       'alma89345350Monopoly23', 'helloGoduEbye234', 
                       'n64Williams3459sdfgmmiopRos']
    newUsernames = []
    newPasswords = []

	## read in the production sheet to get the already existing accounts
	   # Column A: id
	   # Column B: Email
	   # Column C: EmailPassword
	   # Column D: MLBPassword
	df = pd.io.excel.read_excel(Filepath.get_accounts_file(), 
                sheetname='Production', parse_cols='A,B,C,D')
	random.seed()
	for iteration in range(N):
		print "Making account number: {0} of {1}".format(iteration, N)

		## Create a gmail account with a pseudo-random username
		success = False
		while not success:		
			username = random.choice(usernameStarters) + "." + \
			           random.choice(usernameStarters) + "." + \
			           str(random.randint(1,2014))
			password = random.choice(Choices)
			success = make_gmail_account(username, password)
		
		## Create a beatthestreak account on espn
        make_espn_bts_account(username, password)

        ## Claim the bots mulligan 
        bot = Bot(username, password)
        bot.claim_mulligan()

        ## Hold on to the data to add to the btsAccounts excel file
        newUsernames.append(username)
        newPasswords.append(password)
    ## add to the dataframe and replace the Production sheet



if __name__ == '__main__':
	"""
	Usage: ./accounts.py N
	"""
	assert len(sys.argv) == 2
	main(sys.argv[1])


