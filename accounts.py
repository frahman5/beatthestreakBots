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

def make_gmail_account(username, password):
    """
    string string -> bool

    Creates a yahoo email account with the given username and password. 
    Returns True if successful, False otherwise

    Assumes browser is already launched
    """
    global browser

    ## get the gmail create account page
    url = 'https://accounts.google.com/SignUp?service=mail&continue=https' + \
          '%3A%2F%2Fmail.google.com%2Fmail%2F&ltmpl=default'
    browser.get(url)

    ## Supply account creation info
        # Enter email username. If it's already taken, return False
    browser.find_element_by_id('GmailAddress').send_keys(username)
    errorMessage = browser.find_element_by_id('errormsg_0_GmailAddress')
    if errorMessage.text != '':
        return False
        # Handle all other non dropdowns
    browser.find_element_by_id('FirstName').send_keys('Faiyam')
    browser.find_element_by_id('LastName').send_keys('Rahman')
    browser.find_element_by_id('Passwd').send_keys(password)
    browser.find_element_by_id('PasswdAgain').send_keys(password)
    browser.find_element_by_id('RecoveryPhoneNumber').send_keys('3472626300')
    browser.find_element_by_id('RecoveryEmailAddress').send_keys('frahman305@gmail.com')
    browser.find_element_by_id('BirthDay').send_keys('5')
    browser.find_element_by_id('BirthYear').send_keys('1991')
    browser.find_element_by_id('TermsOfService').click()
        # Handle dropdowns
    dropDowns = browser.find_elements_by_class_name('jfk-select')
            # 1) birthMonth
    dropDowns[0].click()
    options = browser.find_elements_by_class_name("goog-menuitem-content")
    for option in options:
        if option.text == 'March':
            option.click()
            # 2) Gender
    dropDowns[1].click()
    options = browser.find_elements_by_class_name("goog-menuitem-content")
    for option in options:
        if option.text == 'Male':
            option.click()
            # 3) Location --> defaults to United States so we leave it alone

    ## Prompt user to do the captcha and submit the form
    userResponse = ''
    while userResponse != 'n':
        userResponse = raw_input("Solve captcha, then type enter n to continue\n")
    submitButton = browser.find_element_by_id('submitbutton')
    submitButton.click()
    time.sleep(5)

    ## Click the continue button (verifying account)
    submitButton = browser.find_element_by_id('next-button')
    submitButton.click()
    time.sleep(5)

    ## Prompt user to enter verification code and submit the form
    userResponse = ''
    while userResponse != 'n':
        userResponse = raw_input("Enter verification number (see your phone)," +\
                                  "then type n to continue\n")
    submitButton = browser.find_element_by_id('VerifyPhone')
    submitButton.click()
    time.sleep(5)

    return True

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

    Creates N unique beatthestreak accounts, claims mulligans for each account
    and stores all username and password info in btsAccounts.xlsx, sheetname "Production"
    """
    global browser

    usernameStarters = [ 'faiyam', 'rahman', 'bts', 'metro', 'williams', 
                         'grassfed', 'daft', 'fossil', 'water', 'earth']
    passwordChoices = ['sdFgsdfg892m45@', 'beatthesTr&k78', 
                       'alma8oly23@', 'helloGoe234!', 'n64Will!iam345']
    newUsernamesL, newPasswordsL = [], []

    ## read in the production sheet to get the already existing accounts
       # Column A: id
       # Column B: Email
       # Column C: EmailPassword
       # Column D: MLBPassword
    df = pd.io.excel.read_excel(Filepath.get_accounts_file(), 
                sheetname='Production', parse_cols='A,B,C,D')
    random.seed()
    for iteration in range(int(N)):
        print "Making account number: {0} of {1}".format(iteration, N)

        ## get a new firefox browser
        browser = webdriver.Firefox()
        
        ## Create a gmail account with a pseudo-random username
        success = False
        while not success:      
            username = random.choice(usernameStarters) + "." + \
                       random.choice(usernameStarters) + "." + \
                       str(random.randint(1,2014))
            password = random.choice(passwordChoices)
            success = make_gmail_account(username, password)
        
        ## Create a beatthestreak account on espn
        make_espn_bts_account(username, password)
        browser.quit()

        ## Claim the bots mulligan 
        claim_mulligan(username, password)

        ## Hold on to the data to add to the btsAccounts excel file
        newUsernamesL.append(username)
        newPasswordsL.append(password)

        ## Kill the firefox browser
        browser.quit()

    ## add to the dataframe and replace the Production sheet
        # make sure the excel file has the column headers we expect
    assert df.columns[0] == 'ID'
    assert df.columns[1] == 'Email'
    assert df.columns[2] == 'EmailPassword'
    assert df.columns[3] == 'MLBPassword'
        # make a dataframe containing the new info
    firstID = len(df.ID) - 1
    idL = [firstID + i for i in range(0, len(newUsernamesL))]
    extraDF = pd.concat([Series(idL, name='ID')], 
                         Series(newUsernamesL, name='Email'), 
                         Series(newPasswordsL, name='EmailPassword'), 
                         Series(newPasswordsL, name='MLBPassword'), 
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
    # assert len(sys.argv) == 2
    # main(sys.argv[1])
    main2(sys.argv[1], sys.argv[2])


