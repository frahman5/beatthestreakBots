class BaseException(Exception):
    def __init__(self, message):
         Exception.__init__(self, message)
         
    def __str__(self):
         return repr(self.message)

class NoPlayerFoundException(BaseException):
	pass

class SameNameException(BaseException):
	pass

class FailedAccountException(BaseException):
    pass

class FailedUpdateException(BaseException):
    pass