import logging
import logging.handlers
from functools import wraps

from config import ADMIN, PASSWORD
from handlers import TlsSMTPHandler
from filepath import Filepath

class smoothBotError(object):
    """
    decorator for Bot functions. If any bot method throws an exception, 
    the bot's browser quits, and the exception is reraised so it can pass through
    to the upper-level logging logic
    """ 
    def __init__(self, f):
        self.f = f

    def __get__(self, instance, owner):
        """ Supports instance methods """
        self.cls = owner
        self.obj = instance

        return self.__call__

    def __call__(self):
        @wraps(self.f) # So that the .__name__ and .__doc__ of f don't change
        def wrapper(*args, **kwargs):
            try:
                self.f.__call__(*args, **kwargs)
            except:
                self.obj.quit_browser() # also closes display, if appropriate
                raise
        return wrapper

# def smoothBotError(func):
#     @wraps(func) # So that the .__name__ and .__doc__ of f don't change
#     def decorator(self, *args, **kwargs):
#         print 'instance %s of class %s is now decorated whee!' % (
#            self.username, self.__class__
#         )
#         try:
#             func(*args, **kwargs)
#         except:
#             self.quit_browser() # also closes display, if appropriate
#             raise

#         return decorator