from bot import Bot

def randDownRandPlayers(bot, eligiblePlayers):
    """
    Bot ListOfTuples int -> None
        bot: Bot | the bot to which we need to assign players
        eligiblePlayers: ListOfTuples | List of distribution-eligible
           players. Format: (firstName, lastName, 3digitTeamAbbreviation)

    Randomly decides whether or not to doubleDown, and randomly chooses
    players to assign to bot. Returns the assigned players
    """
    # Update the bot and return the players
    return staticDownRandPlayers( bot=bot, eligiblePlayers=eligiblePlayers, 
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
    import random

    ## check arguments
    assert type(kwargs['bot'] == Bot)
    assert type(kwargs['eligiblePlayers'] == list)
    assert len(eligiblePlayers) != 0
    assert type(kwargs['doubleDown'] == bool)

    # Pseudo-randomly choose playres
    p1 = random.choice(eligiblePlayers)
    if kwargs['doubleDown']:
        p2 = p1
        while (p1 == p2):
            p2 = random.choice(eligiblePlayers)
    else:
        p2 = ()

    # Assign the players to the bot and return them to the caller
    bot.choose_players(p1=p1, p2=p2)
    return p1, p2
