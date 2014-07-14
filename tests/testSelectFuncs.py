import unittest
import os

from selenium import webdriver
from datetime import datetime, date

from beatthestreakBots.selectfunctions import topPBatters, _whoIsEligible
from beatthestreakBots.filepath import Filepath

class TestSelectFuncs(unittest.TestCase):

    def test_topPBatters(self):
        # Test only works on Jul 10th, 2014. Need to change
        # answers for other dates
        jul_14_top_30 = [
                  ('Troy', 'Tulowitzki', 'col'),
                  ('Adrian', 'Beltre', 'tex'),
                  ('Jose', 'Altuve', 'hou'), 
                  ('Matt', 'Adams', 'stl'),
                  ('Victor', 'Martinez', 'det'),
                  ('Robinson', 'Cano', 'sea'),
                  ('Michael', 'Brantley', 'cle'),
                  ('Lonnie', 'Chisenhall', 'cle'),
                  ('Jonathan', 'Lucroy', 'mil'),
                  ('Casey', 'McGehee', 'mia'),
                  ('Andrew', 'McCutchen', 'pit'),
                  ('Miguel', 'Cabrera', 'det'),
                  ('Justin', 'Morneau', 'col'),
                  ('Paul', 'Goldschmidt', 'ari'),
                  ('Mike', 'Trout', 'laa'),
                  ('Kurt', 'Suzuki', 'min'),
                  ('Yasiel', 'Puig', 'lad'), 
                  ('Ian', 'Kinsler', 'det'),
                  ('Hunter', 'Pence', 'sf'),
                  ('Adam', 'Jones', 'bal'),
                  ('Scooter', 'Gennett', 'mil'),
                  ('Charlie', 'Blackmon', 'col'),
                  ('Alex', 'Rios', 'tex'),
                  ('Carlos', 'Gomez', 'mil'),
                  ('Melky', 'Cabrera', 'tor'),
                  ('Ryan', 'Braun', 'mil'),
                  ('Ben', 'Revere', 'phi'),
                  ('Freddie', 'Freeman', 'atl'),
                  ('Giancarlo', 'Stanton', 'mia'),
                  ('Daniel', 'Murphy', 'nym')
          ]
        ## Get the top 10 and 20 playres on July 13th, by batting average
        top20Path = Filepath.get_root() + \
              '/tests/text/{}_top20.txt'.format(datetime.today().date())
        if not os.path.isfile(top20Path):
            try:
                top20Players = ['NOPLAYER' for i in range(20)]
                browser = webdriver.Chrome()
                browser.get('http://espn.go.com/mlb/stats/batting')
                print ''
                for player in jul_14_top_30:
                    if 'NOPLAYER' not in top20Players: # we're done!
                        break
                    oneBasedIndex = int(
                        raw_input('What rank (without ties) is {}\n'.format(player)))
                    if oneBasedIndex <= 20:
                        top20Players[oneBasedIndex-1] = player
                assert 'NOPLAYER' not in top20Players
                with open(top20Path, "w") as f:
                    for player in top20Players:
                        f.write('{},{},{}\n'.format(
                            player[0], player[1], player[2]))
                browser.quit()
            except:
                browser.quit()
                raise
        else:
            top20Players = []
            with open(top20Path, "r") as f:
                for line in f:
                    lineSplit = line.split(',')
                    top20Players.append( ( lineSplit[0], 
                                           lineSplit[1], 
                                           lineSplit[2].replace('\n', '')) )

        ## July 18th test
        top3 = top20Players[0:3]
        del top3[2] # facing a pitcher with ERA 3.24
        self.assertEqual( topPBatters( p=3, 
                                       activeDate=date(2014, 7, 18), 
                                       filt={'minERA': 3.81} ), 
                          tuple(top3) )

        # ## Sort out players by opposing pitcher ERA and whether or not they're starting today
        # Troy, Adrian, Jose, Matt, Victor, Robinson, Michael, Lonnie, Jonathan, Casey = top10
        # Andrew, Miguel, Justin, Paul, Mike, Kurt, Yasiel, Ian, Hunter, Adam = top11_20
        
        # ## Setting up top10, minERA 3.0
        # for player in (Troy, Adrian, Victor, Robinson, Jonathan): # opERA < 3
        #   top10.remove(player)
        # top10_3 = top10

        # ## Setting up top20, minERA 4.0
        # for player in ( Troy, Adrian, Jose, Matt, Victor, Robinson, Jonathan, 
        #                 Andrew, Miguel, Justin, Paul, Kurt, Yasiel, Ian):
        #     top20.remove(player)  # pitchers have era below 4
        # top20_4 = top20

        # ## Run tests
        # today = datetime.datetime.today().date()
        # self.assertEqual( todaysTopPBatters( p=10, 
        #                                      activeDate=today, 
        #                                      filt={'minERA':3.0}), 
        #                   tuple(top10_3) )
        # self.assertEqual( todaysTopPBatters( p=20,
        #                                      activeDate=today,
        #                                      filt={'minERA':4.0}),
        #                   tuple(top20_4))
        # # Should raise an error if given a date that's NOT today
        # self.assertRaises( ValueError, todaysTopPBatters, p=10, 
        #                     activeDate=today + timedelta(1), filt='minERA': 2.5)

    # def test__whosPlaying(self):
    #     ## The top 10 players by batting average on July 10th, 2014
    #     top10 = [
    #               ('Troy', 'Tulowitzki', 'col'),
    #               ('Adrian', 'Beltre', 'tex'),
    #               ('Jose', 'Altuve', 'hou'), 
    #               ('Matt', 'Adams', 'stl'),
    #               ('Victor', 'Martinez', 'det'),
    #               ('Robinson', 'Cano', 'sea'),
    #               ('Michael', 'Brantley', 'cle'),
    #               ('Lonnie', 'Chisenhall', 'cle'),
    #               ('Jonathan', 'Lucroy', 'mil'),
    #               ('Casey', 'McGehee', 'mia')
    #             ]

    #     self.assertEqual(_whoIsEligibleToday(top10, filt={}, browser=, top10Starting)
