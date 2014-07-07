from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from bot import Bot

## webdriver needs a display to run. This sets up a virtual "fake" one
display = Display(visible=0, size=(1024, 768))
display.start()

## Try to choose players
bot = Bot('faiyam@faiyamrahman.com', 'beatthestreak1')
bot.choose_players(p1=('Jose', 'Reyes', 'Toronto Blue Jays'), p2=('Robinson', 'Cano', 'Seattle Mariners'))
bot.browser.quit()

display.stop()
