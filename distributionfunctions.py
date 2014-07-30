import random 
import datetime

from bot import Bot
from config import playerExceptions, ignorePlayers
from exception import NoPlayerFoundException

def randDownRandPlayers(**kwargs):
    """
    kwargs -> None
        bot: Bot | the bot to which we need to assign players
        eligiblePlayers: ListOfTuples | List of distribution-eligible
           players. Format: (firstName, lastName, 3digitTeamAbbreviation)
        activeDate: datetimedate | date for which we are making selections

    Randomly decides whether or not to doubleDown, and randomly chooses
    players to assign to bot. Returns the assigned players
    """
    print "RANDOM DOWN"
    # Update the bot and return the players
    return staticDownRandPlayers( bot=kwargs['bot'], 
                                  eligiblePlayers=kwargs['eligiblePlayers'], 
                                  doubleDown=random.choice((True, False)) )

def staticDownRandPlayers(**kwargs):
    """
    kwargs -> None
        bot: Bot | the bot to which we are assigning playres
        eligiblePlayers: ListOfTuples | List of distribution-eligible
            players. Format: (firstName, lastName, 3digitTeamAbbreviation)
        doubleDown: bool | True if its a double down, False if its a single Down

    Given a type of Down, randomly chooses playres to assign to bot. Returns
    the assigned players
    """
    print "STATIC DOWN : {}".format(kwargs['doubleDown'])
    ## check arguments
    assert type(kwargs['bot'] == Bot)
    assert type(kwargs['eligiblePlayers'] == list)
    assert len(kwargs['eligiblePlayers']) != 0
    assert type(kwargs['doubleDown'] == bool)

    # Pseudo-randomly choose playres
    global ignorePlayers                            # list of players to ignore
    global playerExceptions                         # number of NoPlayerFoundExceptions for each player
    print "iP: {}".format(ignorePlayers)
    print "pE: {}".format(playerExceptions)
    try: 
        p1 = random.choice(kwargs['eligiblePlayers'])
        if kwargs['doubleDown'] and (len(kwargs['eligiblePlayers']) != 1):
            p2 = p1
            while (p1 == p2):
                p2 = random.choice(kwargs['eligiblePlayers'])
        else:
            p2 = ()
        # Assign the players to the bot and return them to the caller
        kwargs['bot'].choose_players(p1=p1, p2=p2)
        return p1, p2
    except NoPlayerFoundException as e:
        ## Update the count of NoPlayerFoundExceptions for the players, and 
        ## add them to ignroePlayers if necessary
        for player in (p1, p2):
            if player in playerExceptions.keys():
                playerExceptions[player] += 1
            else:
                playerExceptions[player] = 1
            if playerExceptions[player] == 10:
                ignorePlayers.append(player)
        e.args += (' with players {} and {}'.format(p1, p2),)
        raise e
    except Exception as e:
        e.args += (' with players {} and {}'.format(p1, p2),)
        raise e
