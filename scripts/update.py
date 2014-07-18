import pandas as pd
from datetime import datetime, timedelta

def main(directory, checkDate):
    """
    string datetime.date -> None

    Takes the directory where all the updated minion Account Files are and 
    a date for which to check them. rints info about which accounts updated 
    succesfully on given date
    """
    # Go to the given directory
    import os
    os.chdir(directory)

    for strategy in range(5, 18):
        # if strategy == 6:
        #     import pdb
        #     pdb.set_trace()
        # Get dataframes
        df1 = pd.read_excel('sN={},vMN=1.xlsx'.format(strategy))
        df2 = pd.read_excel('sN={},vMN=2.xlsx'.format(strategy))

        # Get series corresponding to given date
        dateFormatted = str(checkDate.month) +  '-' + str(checkDate.day)
        dateSeries1 = df1[dateFormatted]
        dateSeries2 = df2[dateFormatted]

        # get total done and report info
        filledOut1 = [elem for elem in dateSeries1 if not pd.isnull(elem)]
        filledOut2 = [elem for elem in dateSeries2 if not pd.isnull(elem)]
        totalDone = len(filledOut1) + len(filledOut2)
        if totalDone == 1000:
            print "--> Strategy {}: DONE!".format(strategy)
        elif totalDone < 1000:
            print "--> Strategy {}: NOT DONE. Remaining: {}".format(strategy, 
                1000-totalDone)
        else:
            raise ValueError("Strategy: {}. Total Done ({}) should be >=0, <=1000".format(
                strategy, totalDone))


if __name__ == '__main__':
    import sys

    # Get arguments
    directory = sys.argv[-2]
    dateNum = int(sys.argv[-1])
    checkDate = datetime.today().date() + timedelta(days=dateNum)

    # Run this bitch
    main(directory, checkDate)