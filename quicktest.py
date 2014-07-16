from bot import Bot
from config import BTSUSERNAME, BTSPASSWORD
from datetime import date

def main():
    bot = Bot(BTSUSERNAME, BTSPASSWORD, activeDate=date(2014,7,19))
    bot.choose_players(p1=('Victor', 'Martinez', 'det'), p2=())

if __name__ == '__main__':
    main()
