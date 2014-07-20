from bot import Bot
from config import BTSUSERNAME, BTSPASSWORD
from datetime import date

def main():
    bot = Bot(BTSUSERNAME, BTSPASSWORD, activeDate=date(2014,7,20))
    # bot.choose_players(p1=('Victor', 'Martinez', 'det'), p2=())
    # import pdb
    # pdb.set_trace()
    bot.choose_players( p1=('Dee', 'Gordon', 'lad'), 
                        p2=())
    # bot.choose_players( p1=('Yadier', 'Molina', 'stl'), 
    #                     p2=())
    # print bot.get_streak_length()

if __name__ == '__main__':
    main()


# ------> Choosing player: ('Adrian', 'Beltre', 'tex')
# ------> Choosing player: ('Alex', 'Rios', 'tex')
# ------> Failure: <type 'exceptions.IndexError'>