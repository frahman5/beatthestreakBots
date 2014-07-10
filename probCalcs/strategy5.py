## Calculate probabilities relating to strategy 5
import math
import sys

def nCr(n, r):
    f = math.factorial
    return f(n)/ (f(r) * f(n-r))


def at_least_one_winner(minBatAve, numDays, threshold):
    """ 
    float int float -> int
      minBatAve: the minimum batting average any player selected in the strategy will have
      numDays: the number of days for which the competition will run
      threshold: a minimum percentage expressed as a decimal

    Return the number N such that if N accounts are made using strategy 5, all players
      selected have batting averages above minbatAve, and the strategy runs for numDays, 
      then with probability threshold we have at least one winner
    """
    p1 = minBatAve * 0.5 # probability of a hit given a single down
    p2 = minBatAve * minBatAve * 0.5  # probability of a two hits, given double down
  
    pOne = 0
    for i in range(29): # we can't have more than 29 succesfful double downs in a winning streak
       pOne += (numDays - 57 - i) * nCr(57-i, i) * (p1 ** (57-(2*i))) * (p2 ** i)
    pOne += nCr(29,29) * (p1 ** 0) * (p2 ** 29) ## edge case 

    pOneOrMore = 0
    numAccounts = 1
    while pOneOrMore < threshold:
        if numAccounts % 100 == 0:
            print "pOneOrMore with {} accounts: {}".format(numAccounts, pOneOrMore)
        pOneOrMore += pOne ** numAccounts
        numAccounts += 1
    
    print "To have a {} change of winning in {} days, if all batters chosen have minimum".format(threshold, numDays) + \
          " {} batting average. Running strategy 5, you need {} accounts".format(minBatAve, numAccounts)

if __name__ == '__main__':
    minBatAve = float(sys.argv[-3])
    numDays = int(sys.argv[-2])
    threshold = float(sys.argv[-1])
    at_least_one_winner(minBatAve, numDays, threshold)
