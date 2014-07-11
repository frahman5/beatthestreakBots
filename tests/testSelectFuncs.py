import datetime
import unittest

from beatthestreakBots.selectfunctions import todaysTopPBatters, _whoIsEligibleToday

class TestSelectFuncs(unittest.TestCase):

    def test_todaysTopPBatters(self):
        # Test only works on Jul 10th, 2014. Need to change
        # answers for other dates

        ## Get the top 10 and 20 playres on July 11th, by batting average
        top10 = [
                  ('Troy', 'Tulowitzki', 'col'),
                  ('Adrian', 'Beltre', 'tex'),
                  ('Jose', 'Altuve', 'hou'), 
                  ('Matt', 'Adams', 'stl'),
                  ('Victor', 'Martinez', 'det'),
                  ('Robinson', 'Cano', 'sea'),
                  ('Michael', 'Brantley', 'cle'),
                  ('Lonnie', 'Chisenhall', 'cle'),
                  ('Jonathan', 'Lucroy', 'mil'),
                  ('Casey', 'McGehee', 'mia')
                ]
        top11_20 = [
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
                   ]
        top20 = [player for player in top10]
        top20.extend(top11_20)

        ## Sort out players by opposing pitcher ERA and whether or not they're starting today
        Troy, Adrian, Jose, Matt, Victor, Robinson, Michael, Lonnie, Jonathan, Casey = top10
        Andrew, Miguel, Justin, Paul, Mike, Kurt, Yasiel, Ian, Hunter, Adam = top11_20
        
        ## Setting up top10, minERA 3.0
        for player in (Troy, Adrian, Victor, Robinson, Jonathan): # opERA < 3
          top10.remove(player)
        top10_3 = top10

        ## Setting up top20, minERA 4.0
        for player in ( Troy, Adrian, Jose, Matt, Victor, Robinson, Jonathan, 
                        Andrew, Miguel, Justin, Paul, Kurt, Yasiel, Ian):
            top20.remove(player)  # pitchers have era below 4
        top20_4 = top20

        ## Run tests
        today = datetime.datetime.today().date()
        # self.assertEqual( todaysTopPBatters( p=10, 
        #                                      today=today, 
        #                                      filt={'minERA':3.0}), 
        #                   tuple(top10_3) )
        self.assertEqual( todaysTopPBatters( p=20,
                                             today=today,
                                             filt={'minERA':4.0}),
                          tuple(top20_4))

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
