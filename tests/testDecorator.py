import unittest
import datetime

from btsReal.decorators import logErrors
from btsReal.filepath import Filepath

class TestBot(unittest.TestCase):

    def test_log_and_email_errors(self):

        @logErrors(test=True)
        def sillyErrorFunc():
            raise Exception("Here is an test error message at time {}".format(
                datetime.datetime.now()))

        len0 = self.__file_len(Filepath.get_log_file(test=True))
        sillyErrorFunc()
        ## Test that log gets correctly updated
        len1 = self.__file_len(Filepath.get_log_file(test=True))
        self.assertGreater(len1, len0)
        ## Test that email gets sent
        print "Make sure you check ADMIN email for error"

    def __file_len(self, fname):
        """
        string -> int
        get the length of a file. Helper function for 
        test_log_and_email_errors
        """
        i = 0
        with open(fname) as f:
            for l in f:
                i += 1
        return i + 1