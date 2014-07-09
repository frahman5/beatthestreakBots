import logging

from filepath import Filepath
def getLogger():
    ## Create logger that handles file logging
    logger = logging.getLogger()
         # handler to write to logs
    fileHandler = logging.FileHandler(Filepath.get_log_file())
    formatter = logging.Formatter('%(asctime)s %(message)s\n')
    fileHandler.setFormatter(formatter)
         # add handlers to logger
    logger.addHandler(fileHandler)

    return logger

def logError(username, password, p1, p2, exception, logger):
    """
    string string TupleOfStrings TupleOfStrings Exception logger -> None
        username: str | username of account being updated at the time of exception
        password: str | password of account being updated at the time of exception
        p1: TupleOfStrings | (firstName, lastName, team) of first player
            being added to account at time of exception
        p2: TupleOfStrings | (firstName, lastName, team) of second player 
            being added to account at time of exception (possible empty)
        exception: Exception | the exception raised 
        logger: logger | logger to use to log errors

    Logs the error to file
    """
       # we don't check the type of exception because i don't know how to do that
    assert type(username) == str
    assert type(password) == str
    assert (type(p1) == tuple) or not p1
    assert (type(p2) == tuple) or not p2
    assert type(logger) == logging.RootLogger

    logger.error("Unit account update failure: {}, {}".format(username, password))
    logger.error("    p1, p2: {}, {}".format(p1, p2))
    logger.error(exception, exc_info=True)

def logFailedAccounts(failedAccounts, numTotalAccounts, logger):
    """
    list int logger -> None
       failedAccounts: ListOfTuples | Each Tuple is a (username, password)
           if a failed Account
       numTotalAccounts: int | the total number of accounts that we attempted
           to update
       logger: logger | logger to use to log errors

    Logs the failedAccounts to today's error log in the event that the main 
    while loop failed to update all players
    """
    # check that we got an appropriate input
    assert len(failedAccounts) != 0
    assert type(failedAccounts) == list
    for elem in failedAccounts:
        assert type(elem) == tuple
        for thing in elem:
            assert type(thing) == str

    # log those errors baby
    logger.error("{} of {} accounts failed".format(
                    len(failedAccounts), numTotalAccounts))
    for failedAccount in failedAccounts:
        logger.error("    U, P: {}, {}".format(failedAccount[0], failedAccount[1]))
