import logging
import logging.handlers
from functools import wraps

from config import ADMIN, PASSWORD
from handlers import TlsSMTPHandler
from filepath import Filepath


class logErrors(object):
    """
    function -> function

    Wraps a function such that if there is an error during the course
    of the function execution, an email is sent to admin Email, and
    the errors are logged to btsReal/log.txt
    """
    def __init__(self, test=False):
        self.test = test

    def __call__(self, f):
        ## Create logger that handles emails and file logging
        logger = logging.getLogger()
            # handler to send emails
        smtpHandler = TlsSMTPHandler(
            mailhost=("smtp.gmail.com", 587), 
            fromaddr=ADMIN,
            toaddrs=(ADMIN,),
            subject=u'Beat the streak error!', 
            credentials=(ADMIN, PASSWORD))
             # handler to write to logs
        fileHandler = logging.FileHandler(Filepath.get_log_file(test=self.test))
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fileHandler.setFormatter(formatter)
             # add handlers to logger
        logger.addHandler(smtpHandler)
        logger.addHandler(fileHandler)

        @wraps(f) # So that the .__name__ and .__doc__ of f don't change
        def wrapper(*args, **kwargs):
            try:
                f(*args, **kwargs)
            except Exception as e:
                logger.error(e)

        return wrapper
