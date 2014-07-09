def randDownRandPlayers(bot, eligiblePlayers):
    """
    Bot ListOfTuples int -> None
        bot: Bot | the bot to which we need to assign players
        eligiblePlayers: ListOfTuples | List of distribution-eligible
           players. Format: (firstName, lastName, 3digitTeamAbbreviation)

    Randomly decides whether or not to doubleDown, and randomly chooses
    players to assign to bot. Returns the assigned players
    """
    import random

    # Pseudo-randomly choose whether or not to doubleDown
    doubleDown = random.choice((True, False))

    # Pseudo-randomly choose players
    p1 = random.choice(eligiblePlayers)
    if doubleDown:
        p2 = p1
        while (p1 == p2):
            p2 = random.choice(eligiblePlayers)
    else:
        p2 = ()

    # Assign the players to the bot!
    bot.choose_players(p1=p1, p2=p2)
    return p1, p2
