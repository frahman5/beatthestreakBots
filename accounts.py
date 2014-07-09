#! /usr/bin/python
import sys
import random
import pandas as pd
import time

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bot import Bot
from filepath import Filepath
from config import GDUSERNAME, GDPASSWORD, OUTLOOKPW, ROOT

def make_espn_bts_account(username, password):
    """
    string string -> None

    Creates an ESPN beatthestreak account with the given username and password

    Assumes browser is already launched
    """
    ## Open up shop
         # webdriver needs a display to run. This sets up a virtual "fake" one
    if ROOT == '/home/faiyamrahman/programming/Python/beatthestreakBots':
        print "--> Starting Display"
        display = Display(visible=0, size=(1024, 768))
        display.start()
    browser = webdriver.Chrome()

    print "-->Making BTS account for u, p: {0}, {1}\n".format(username, password)

    ## get the gmail create account page
    url = 'https://secure.mlb.com/enterworkflow.do?flowId=fantasy.bts.' + \
          'btsloginregister&forwardUrl=http://mlb.mlb.com/mlb/fantasy/bts/y2014/'
    browser.get(url)

    ## Enter in account information
        # Handle all non dropdowns
    browser.find_element_by_id('register_email').send_keys(username)
    browser.find_element_by_id('register_pwd').send_keys(password)
    browser.find_element_by_id('register_pwd_confirm').send_keys(password)
    browser.find_element_by_id('select_register').click() 
    browser.find_element_by_id('register_optin').click()
        # Handle dropdowns
    dropDowns = browser.find_elements_by_tag_name('select')
            # 1) birthMonth
    dropDowns[0].click() # make the month options clickable
    dDowns = browser.find_elements_by_tag_name('select')
    options = dDowns[0].find_elements_by_tag_name('option')
    for option in options: # select month 3
        if option.text == '3':
            option.click()
            
            # 2) birthDay
    dropDowns[1].click() # make the day options clickable
    dDowns = browser.find_elements_by_tag_name('select')
    options = dDowns[1].find_elements_by_tag_name('option')
    for option in options: # select day 5
        if option.text == '5':
            option.click()
            # 3) birthYear
    dropDowns[2].click() # make the year options clickable
    dDowns = browser.find_elements_by_tag_name('select')
    options = dDowns[2].find_elements_by_tag_name('option')
    for option in options: # select year 1991
        if option.text == '1991':
            option.click()
 
    ## Hit the submit button
    browser.find_element_by_id('submit_btn').click()
    assert browser.title == 'Beat The Streak | MLB.com: Fantasy'

    ## Close up shop
    browser.quit()
    if ROOT == '/home/faiyamrahman/programming/Python/beatthestreakBots':
        print "--> Stopping Display"
        display.stop()
    

def claim_mulligan(username, password):
    """
    string string -> None

    Creates a bot with username and password and then claims the bots mulligan

    Bot launches and closes its own display and browser
    """
    bot = Bot(str(username), password)
    bot.claim_mulligan()

def main(N):
    """
    int -> None

    Creates N unique beatthestreak accounts, and claims mulligans for each account.
    Stores all username and password info in btsAccounts.xlsx, sheetname "Production"

       IMPORTANT: Does not actually make email addresses for the accounts. 
    If any account gets to over 40 hits in a row, we'll go and MANUALLY
    make an email account and validate it. 
    """
    global browser
    newUsernamesL = []
    newMLBPasswordsL = []
    usernameStarters = [ 'faiyam', 'rahman', 'bts', 'metro', 'williams', 
                         'grassfed', 'daft', 'fossil', 'water', 'earth']

    ## read in the production sheet to get the already existing accounts
       # Column A: id
       # Column B: Email
       # Column C: EmailPassword
       # Column D: MLBPassword
    df = pd.io.excel.read_excel(Filepath.get_accounts_file(), 
                sheetname='Production', parse_cols='A,B,C,D')

    ## Create N new fake email addresses. We'll go and ACTUALLY make them
    ## if they reach a certain plateau streak length
    listOfEmails = list(df.Email) # need a list to check if an email has already been used
    i = 0
    while (i < N):
        username = random.choice(usernameStarters) + "." + \
                    random.choice(usernameStarters) + "." + \
                    str(random.randint(1,2014)) + '@faiyamrahman.com'
        # make sure we don't repeat an address
        if (username in listOfEmails) or (username in newUsernamesL):
            continue
        newUsernamesL.append(username)
        i += 1

    for username in newUsernamesL:
        time.sleep(10) # give it some time to clean things up
        print "\nFinishing account number: {0} of {1}".format(newUsernamesL.index(username) + 1, len(newUsernamesL))

        ## get a new firefox browser
        browser = webdriver.Chrome()
        
        ## Wrap this in a try except in case selenium fails us
        accountMade, mulliganClaimed = (False, False)
        while True:
            try:
                ## Create a beatthestreak account on espn and kill the browser
                if not accountMade:
                    password = 'beatthestreak1'
                    make_espn_bts_account(username, password)
                    accountMade = True
                ## Claim the bots mulligan 
                if not mulliganClaimed:
                    claim_mulligan(username, password) # uses its own browser
                    print "-->Mulligan claimed :)"
                    mulliganClaimed = True
            except Exception as e:
                print e.message
                continue
            else:
                break

        

        ## Hold on to the data to add to the btsAccounts excel file
        newMLBPasswordsL.append(password)

    ## add to the dataframe and replace the Production sheet
        # make sure the excel file has the column headers we expect
    assert df.columns[0] == 'ID'
    assert df.columns[1] == 'Email'
    assert df.columns[2] == 'EmailPassword'
    assert df.columns[3] == 'MLBPassword'
        # make a dataframe containing the new info
    firstID = len(df.ID)
    idL = [firstID + i for i in range(0, len(newUsernamesL))]
            # outlook 365 aliases don't have their own passwords
    newEmailPasswordsL = ['n/a' for password in newMLBPasswordsL]
    extraDF = pd.concat([pd.Series(idL, name='ID'), 
                         pd.Series(newUsernamesL, name='Email'), 
                         pd.Series(newEmailPasswordsL, name='EmailPassword'), 
                         pd.Series(newMLBPasswordsL, name='MLBPassword')], 
                         axis=1)
        # create a dataframe with all the info and write it to file
    newDF = pd.concat([df, extraDF])
    writer = pd.ExcelWriter(Filepath.get_accounts_file())
    newDF.to_excel(writer,
                   index=False, 
                   sheet_name='Production') 
    writer.save()

if __name__ == '__main__':
    """
    Usage: ./accounts.py N
    """
    assert len(sys.argv) == 2
    
    numAccounts = int(sys.argv[1])
    origCount = numAccounts
    # make accounts in sets of 20 so that in case something bad happens,
    #  we dont lose e.g 1000 accounts
    blockSize = 20
    while numAccounts > 0:
        if numAccounts < blockSize:
            main(numAccounts)
            break
        else: 
            print "********** CREATING IN CHUNKS OF {}:.Completed {} of {} ***********".format(
                  blockSize, origCount-numAccounts, origCount) 
            main(blockSize)
            numAccounts -= blockSize
