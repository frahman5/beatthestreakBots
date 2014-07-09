from config import BTSUSERNAME, BTSPASSWORD
from bot import Bot

def todaysRecommendedPicks(today):
    """
    datetime.date int -> listOfTuples
        today: datetime.date | today's date

    Produces a TupleOfTuples where each tuple is of format:
        (firstName, lastName, teamAbbrevations)
        for a player that is on today's "recommended picks" dropdwown
        on the MLB beat the streak player selection page
    """
    bot = Bot(BTSUSERNAME, BTSPASSWORD)
    return bot.get_todays_recommended_players()