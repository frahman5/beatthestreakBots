#!bvenv/bin/python
import sys
import random
import pandas as pd
import time

from selenium import webdriver

from bot import Bot
from filepath import Filepath
## A globally shared browser for all activites
browser = None

def make_outlook365_email_addys(N):
    """
    int -> ListOfStrings

    Creates N new email addresses on outlook365 for admin account
    faiyam@faiyamrahman.com and returns a list of the new addresses
    """
    import pdb
    pdb.set_trace()
    global browser 
    browser = webdriver.Firefox()
    newUsernamesL = []

    usernameStarters = [ 'faiyam', 'rahman', 'bts', 'metro', 'williams', 
                         'grassfed', 'daft', 'fossil', 'water', 'earth']
    ## get to manage aliases page
        ## get to outlook inbox
    url = 'https://sso.godaddy.com/?realm=pass&app=o365&wa=wsignin1.0&wt' +\
          'realm=urn:federation:MicrosoftOnline&wctx=wa%3Dwsignin1.0%26rpsnv' +\
          '%3D3%26ct%3D1404228578%26rver%3D6.1.6206.0%26wp%3DMBI_SSL%26wreply' +\
          '%3Dhttps:%252F%252Fpod51038.outlook.com%252Fowa%252F%26id%3D260563' +\
          '%26whr%3Dfaiyamrahman.com%26CBCXT%3Dout'
    browser.get(url) # sign in page
    browser.find_element_by_id('username').send_keys('faiyam@faiyamrahman.com')
    browser.find_element_by_id('password').send_keys('helloGoe234!')
    browser.find_element_by_id('submitBtn').click()
        ## go to manage aliases page
    url = 'https://portal.office.com/UserManagement/EditUser.aspx?tab=' + \
          'emailAddresses&id=ce2ec883-494a-4c13-808c-9cfcba873199'
    browser.get(url)
    raise Exception("done testing")

    ## enter in the N addy's
       # randomly choose one of the two available domain names
    selectBox = browser.find_element_by_id('ddlDomainsAliases_dropdown')
    options = selectBox.find_elements_by_tag_name('option')
    domain = random.choice(options)
    domain.click()
        # construct a random email and try to add it
    username = random.choice(usernameStarters) + "." + \
               random.choice(usernameStarters) + "." + \
               str(random.randint(1,2014))
    browser.find_element_by_id('tbEmailAlias').send_keys(username)
        # if it works, keep going, otherwise try another one
    newUsernamesL.append(username + domain.text)

    ## hit save and wait a minute
    # ????????????? # hit save
    time.sleep(60)

    ## prompt the user to check if shit worked
    success = ''
    while success not in ('done', 'again'):
        success = raw_input('Hit "done" if the additions worked, or "again"' +\
                            'if we need to try again')
    if success == 'again':
        browser.quit()
        make_outlook365_email_addys(N)

    ## return the list of strings and close the browser
    browser.quit()
    return newUsernamesL

def make_espn_bts_account(username, password):
    """
    string string -> None

    Creates an ESPN beatthestreak account with the given username and password

    Assumes browser is already launched
    """
    global browser

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
    time.sleep(5)
    ######### EXPERIMENT ##############
    dDowns = browser.find_elements_by_tag_name('select')
    options = dDowns[0].find_elements_by_tag_name('option')
    # options = dropDowns[0].find_elements_by_tag_name('option')
    for option in options: # select month 3
        if option.text == '3':
            option.click()
            # 2) birthDay
    dropDowns[1].click() # make the day options clickable
    time.sleep(5)
    dDowns = browser.find_elements_by_tag_name('select')
    options = dDowns[1].find_elements_by_tag_name('option')
    # options = dropDowns[1].find_elements_by_tag_name('option')
    for option in options: # select day 5
        if option.text == '5':
            option.click()
            # 3) birthYear
    dropDowns[2].click() # make the year options clickable
    time.sleep(5)
    dDowns = browser.find_elements_by_tag_name('select')
    options = dDowns[2].find_elements_by_tag_name('option')
    # options = dropDowns[2].find_elements_by_tag_name('option')
    for option in options: # select year 1991
        if option.text == '1991':
            option.click()
 
    ## Hit the submit button
    browser.find_element_by_id('submit_btn').click()
    time.sleep(5)

def claim_mulligan(username, password):
    """
    string string -> None

    Creates a bot with username and password and then claims the bots claim_mulligan

    Assumes browser is already launched
    """
    bot = Bot(username, password)
    bot.claim_mulligan()

def main(N):
    """
    int -> None

    Creates N unique beatthestreak accounts, claims mulligans for each account and
    also verifies the email addresses for each account.
    Stores all username and password info in btsAccounts.xlsx, sheetname "Production"
    """
    global browser
    newMLBPasswordsL = []

    passwordChoices = ['beatthestreak1', 'ksdfgusergjiserg98', 
                       'faiyamWinsbeat243', 'almaalmamater6573']

    ## read in the production sheet to get the already existing accounts
       # Column A: id
       # Column B: Email
       # Column C: EmailPassword
       # Column D: MLBPassword
    df = pd.io.excel.read_excel(Filepath.get_accounts_file(), 
                sheetname='Production', parse_cols='A,B,C,D')

    ## Create N new email addresses
    newUsernamesL = make_outlook365_email_addys(N) # opens and closes the browser on its own

    for username in newUsernamesL:
        print "Finishing account number: {0} of {1}".format(iteration, N)

        ## get a new firefox browser
        browser = webdriver.Firefox()
        
        ## Create a beatthestreak account on espn and kill the browser
        password = random.choice(passwordChoices)
        make_espn_bts_account(username, password)
        browser.quit()

        ## Claim the bots mulligan 
        claim_mulligan(username, password) # uses its own browser

        ## Hold on to the data to add to the btsAccounts excel file
        newMLBPasswordsL.append(password)

    ## add to the dataframe and replace the Production sheet
        # make sure the excel file has the column headers we expect
    assert df.columns[0] == 'ID'
    assert df.columns[1] == 'Email'
    assert df.columns[2] == 'EmailPassword'
    assert df.columns[3] == 'MLBPassword'
        # make a dataframe containing the new info
    firstID = len(df.ID) - 1
    idL = [firstID + i for i in range(0, len(newUsernamesL))]
            # outlook 365 aliases don't have their own passwords
    newEmailPasswordsL = ['n/a' for password in newMLBPasswordsL]
    extraDF = pd.concat([Series(idL, name='ID')], 
                         Series(newUsernamesL, name='Email'), 
                         Series(newEmailPasswordsL, name='EmailPassword'), 
                         Series(newMLBPasswordsL, name='MLBPassword'), 
                         axis=1)
        # create a dataframe with all the info and write it to file
    newDF = pd.concat([df, extraDF])
    newDF.to_excel(pd.ExcelWriter(Filepath.get_accounts_file()),
                   index=False, 
                   sheet_name='Production') 

def main2(username, password):
    global browser
    browser = webdriver.Firefox()

    # make_espn_bts_account(username, password)
    claim_mulligan(username, password)

if __name__ == '__main__':
    """
    Usage: ./accounts.py N
    """
    assert len(sys.argv) == 2
    main(int(sys.argv[1]))
    # main2(sys.argv[1], sys.argv[2])