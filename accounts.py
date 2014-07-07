#!bvenv/bin/python
import sys
import random
import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bot import Bot
from filepath import Filepath
from config import GDUSERNAME, GDPASSWORD, OUTLOOKPW

## A globally shared browser for all activites
browser = None

def make_outlook365_email_addys(N):
    """
    int -> ListOfStrings

    Creates N new email addresses on outlook365 for admin account
    faiyam@faiyamrahman.com and returns a list of the new addresses
    """
    print "Let's make some email addresses!"
    global browser 
    browser = webdriver.Firefox()
    newUsernamesL = []

    usernameStarters = [ 'faiyam', 'rahman', 'bts', 'metro', 'williams', 
                         'grassfed', 'daft', 'fossil', 'water', 'earth']
    try : 
        ## get to manage aliases page
            # goDaddy account page
        browser.get('http://www.godaddy.com/')

            # get the login form to dropdown
        aButton = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'oi-group1'))
            )
        oiButtons = browser.find_elements_by_class_name('oi-group1')
        for button in oiButtons:
            if button.text == "Sign In\nRegister":
                button.click()
                break

            # login
        login = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'loginname')))
        login.send_keys(GDUSERNAME)
        password = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'password')))
        password.send_keys(GDPASSWORD)
        browser.find_element_by_class_name('sign-in-btn').click()
        assert browser.title == 'My Account'

            # launch outlook365 manager
        buttons = browser.find_elements_by_class_name('mr10')
        for button in buttons:
            if button.get_attribute('title') == "Office 365 Email and Productivity Control Center":
                button.click()
                break

            # get to manage aliases page
        gearIcon = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'gearIcon_faiyam@faiyamrahman.com')))
        gearIcon.click()
        accountManagement = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'account_management'))
            )
        links = accountManagement.find_elements_by_tag_name('a')
        for link in links:
            if link.text == 'Manage aliases':
                link.click()
                break
        browser.switch_to_window(browser.window_handles[1]) # hitting the manage aliases link opens a new window
        browser.find_element_by_id('password').send_keys(OUTLOOKPW)
        browser.find_element_by_id('submitBtn').click()
        
        print "About to enter the loop"
        ## enter in the N addy's
        i = 1
        while (i <= N):
               # randomly choose one of the two available domain names
            selectBox = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, 'ddlDomainsAliases_dropdown')))
            options = selectBox.find_elements_by_tag_name('option')
            domain = random.choice(options)
            domain.click()

                # construct a random email and try to add it
            username = random.choice(usernameStarters) + "." + \
                       random.choice(usernameStarters) + "." + \
                       str(random.randint(1,2014))
            aliasBox = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, 'tbEmailAlias')))
            aliasBox.send_keys(username)

                # if it doesn't work, try again
            dialogueBoxes = browser.find_elements_by_id('dialogBodyArea')
            for box in dialogueBoxes:
                if box.text == "Please try again later.":
                    browser.find_element_by_id('DialogManager1_dialogAcceptButton_0').click()
                    aliasBox.clear()
                    continue

                # otherwise continue forward young man!
            browser.find_element_by_id('SmtpAddButton').click()
            newUsernamesL.append(username + '@' + domain.text)  
            i += 1

        ## hit save and wait for it to work, prompting user to check
        browser.find_element_by_id('MultiPageLayout_Save').click()
        success = ''
        while success not in ('done', 'again'):
            print "Have these addresses been added?: Answer in 1 minute"
            print newUsernamesL
            time.sleep(60)
            success = raw_input('Hit "done" if the additions worked, or "again"' +\
                                'if we need to try again\n')
        if success == 'again':
            browser.quit()
            make_outlook365_email_addys(N)
    except Exception as e:
        raise e
    finally:
        ## return the newEmailAddys and close the browser
        browser.quit()
        return newUsernamesL

def make_espn_bts_account(username, password):
    """
    string string -> None

    Creates an ESPN beatthestreak account with the given username and password

    Assumes browser is already launched
    """
    print "Making BTS account for u, p: {0}, {1}\n".format(username, password)
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
    dDowns = browser.find_elements_by_tag_name('select')
    options = dDowns[0].find_elements_by_tag_name('option')
    for option in options: # select month 3
        if option.text == '3':
            print "we click month"
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

def claim_mulligan(username, password):
    """
    string string -> None

    Creates a bot with username and password and then claims the bots claim_mulligan

    Assumes browser is already launched
    """
    bot = Bot(str(username), password)
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

    random.seed() # will be takin random pauses along the way
    ## read in the production sheet to get the already existing accounts
       # Column A: id
       # Column B: Email
       # Column C: EmailPassword
       # Column D: MLBPassword
    df = pd.io.excel.read_excel(Filepath.get_accounts_file(), 
                sheetname='Production', parse_cols='A,B,C,D')
    testDF = pd.io.excel.read_excel(Filepath.get_accounts_file(), 
                sheetname='Test')
    otherDF = pd.io.excel.read_excel(Filepath.get_accounts_file(), 
                sheetname='Other')

    ## Create N new email addresses. Wrap it in a try-except if shit goes bad
    numAddresses = N
    usernamesBuffer = []
    while True:
        try:
            # opens and closes the browser on its own
            newUsernamesL = make_outlook365_email_addys(numAddresses) 
        except:
            continue
        else:
            if len(newUsernamesL) != numAddresses:
                numAddresses -= len(newUsernamesL)
                usernamesBuffer.extend(newUsernamesL)
                continue
            else:
                break
    if len(usernamesBuffer) != 0:
        newUsernamesL.extend(usernamesBuffer)

 
    for username in newUsernamesL:
        print "Finishing account number: {0} of {1}".format(newUsernamesL.index(username) + 1, len(newUsernamesL))

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
                    browser.quit()
                    accountMade = True
                ## Claim the bots mulligan 
                if not mulliganClaimed:
                    print "Let's claim a mulligan!"
                    # import pdb
                    # pdb.set_trace()
                    claim_mulligan(username, password) # uses its own browser
                    print "Mulligan claimed :)"
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
    testDF.to_excel(writer, index=False, sheet_name="Test")
    otherDF.to_excel(writer, index=False, sheet_name="Other")
    writer.save()

if __name__ == '__main__':
    """
    Usage: ./accounts.py N
    """
    assert len(sys.argv) == 2
    main(int(sys.argv[1]))