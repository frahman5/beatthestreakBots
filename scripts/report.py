# Script to retrieve the streak lengths for all accounts and report
# updated information to file
import pandas as pd
from datetime import datetime, timedelta

def main():

    ## Put heatthestreakBots on the path and import bot
    import sys
    sys.path.append('/Users/faiyamrahman/programming/Python/')
    from beatthestreakBots.bot import Bot

    ## Retrieve usernames and passwords from master accounts file
    path = '/Users/faiyamrahman/Desktop/final/master/btsAccounts.xlsx'
    df = pd.read_excel( path, 
                        sheetname='Production', 
                        parse_cols='B,' + # usernames
                                   'D')   # passwords

    # ## Make series with streak lengths for each account
    lenDF = len(df)
    yesterday = datetime.today().date() - timedelta(days=1)
    streakLengths = [ None for i in range(lenDF) ]
    for index, username, password in df.itertuples():  
        print "--> Retrieving streak for account {} of {}".format(index + 1, lenDF)
        streakLength = None
        while streakLength is None:
            try: 
                bot = Bot(str(username), str(password), activeDate=yesterday)
                streakLength = bot.get_streak_length()
            except KeyboardInterrupt:
                break
                raise 
            except:
                exc_type = sys.exc_info()[0]
                print "------> Failure: {}".format(exc_type)
                continue
        streakLengths[index] = streakLength

    dateFormatted = str(yesterday.month) + '-' + str(yesterday.day)
    # streakLengthSeries = pd.Series(streakLengths, name=dateFormatted)

    ## Update the accounts file with streak lengths
    fulldf = pd.read_excel( path, sheetname='Production')
    df = pd.concat([fulldf, streakLengthSeries], axis=1)
    df.to_excel( path, sheet_name='Production', index=False)

    ## Report info about top ballers to file
    df = pd.read_excel( path, sheetname="Production")
    streakInfo = zip(df.Email, df.Strategy, df[dateFormatted])
    topFile = open('/Users/faiyamrahman/Desktop/final/logs/top({}).txt'.format(
                  yesterday), "a+")
        # Print info about top 10 global streaks
    streakInfo.sort(key=lambda x: x[-1], reverse=True)
    topFile.write("Top 10 accounts on date: {}\n".format(yesterday))
    for i in range(10):
        topFile.write("    {}: {}, {}\n".format(
            i + 1, streakInfo[i][0], streakInfo[i][2]))
    topFile.flush()
        # For each strategy, print info about top 5 local streaks
    for strategy in range(5, 18):
             # already sorted by streak length!
        localStreakInfo = [ info for info in streakInfo if info[1] == strategy]
        topFile.write('\n')
        topFile.write("Top 5 Accounts for Strategy {}\n".format(strategy))
        for i in range(5):
            topFile.write("    {}: {}, {}\n".format(
                i + 1, localStreakInfo[i][0], localStreakInfo[i][2]))
    topFile.close()

if __name__ == '__main__':
    main()